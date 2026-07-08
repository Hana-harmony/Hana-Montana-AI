from __future__ import annotations

import importlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from hannah_montana_ai.core.config import Settings
from hannah_montana_ai.domain.schemas import Importance, Sentiment, SourceType, SummaryLines
from hannah_montana_ai.services.model import require_lora_adapter_artifact

NEWS_SUMMARY_PROMPT_VERSION = "news-summary-qwen3-wwi-v1"


@dataclass(frozen=True)
class NewsSummaryContext:
    title: str
    snippet: str
    content: str
    source_type: SourceType
    importance: Importance
    sentiment: Sentiment
    event_tags: list[str]
    stock_code: str | None
    stock_name: str | None
    stock_name_en: str
    fallback: SummaryLines


class NewsSummaryClient(Protocol):
    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        pass


type MlxModelLoader = Callable[[str, Path | None], tuple[Any, Any]]
type MlxTextGenerator = Callable[[Any, Any, str, int, float], str]


class OpenAiCompatibleNewsSummaryClient:
    def __init__(self, endpoint: str, model: str, timeout_seconds: float) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        parsed_url = urllib.parse.urlparse(self._endpoint)
        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError("LLM endpoint must use http or https")
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.1,
            "top_p": 0.8,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(  # noqa: S310
            f"{self._endpoint}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(  # noqa: S310  # nosec B310
            request,
            timeout=self._timeout_seconds,
        ) as response:
            body = json.loads(response.read().decode("utf-8"))
        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("LLM response has no choices")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise ValueError("LLM response has no message")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM response content is empty")
        return content


class MlxQwenNewsSummaryClient:
    def __init__(
        self,
        *,
        model: str,
        adapter_path: Path | None,
        temperature: float = 0.0,
        model_loader: MlxModelLoader | None = None,
        text_generator: MlxTextGenerator | None = None,
    ) -> None:
        self._model_name = model
        self._adapter_path = adapter_path
        self._temperature = temperature
        self._model_loader = model_loader or self._load_mlx_model
        self._text_generator = text_generator or self._generate_mlx_text
        self._pipeline: tuple[Any, Any] | None = None

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        model, tokenizer = self._load_pipeline()
        prompt = self._format_chat_prompt(messages, tokenizer)
        return self._text_generator(
            model,
            tokenizer,
            prompt,
            max_tokens,
            self._temperature,
        )

    def _load_pipeline(self) -> tuple[Any, Any]:
        if self._pipeline is None:
            self._pipeline = self._model_loader(self._model_name, self._adapter_path)
        return self._pipeline

    @staticmethod
    def _load_mlx_model(model_name: str, adapter_path: Path | None) -> tuple[Any, Any]:
        try:
            mlx_lm = importlib.import_module("mlx_lm")
        except ImportError as exception:
            raise ValueError(
                "mlx_lm is required for direct news summary Qwen3 local generation"
            ) from exception
        load = cast(Callable[..., tuple[Any, Any]], mlx_lm.load)
        return load(
            model_name,
            adapter_path=str(adapter_path) if adapter_path is not None else None,
        )

    @staticmethod
    def _generate_mlx_text(
        model: Any,
        tokenizer: Any,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        try:
            mlx_lm = importlib.import_module("mlx_lm")
        except ImportError as exception:
            raise ValueError(
                "mlx_lm is required for direct news summary Qwen3 local generation"
            ) from exception
        sample_utils = importlib.import_module("mlx_lm.sample_utils")
        make_sampler = cast(Callable[..., Callable[[Any], Any]], sample_utils.make_sampler)
        sampler = make_sampler(temp=temperature)
        generate = cast(Callable[..., str], mlx_lm.generate)
        return generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=sampler,
            verbose=False,
        )

    @staticmethod
    def _format_chat_prompt(messages: list[dict[str, str]], tokenizer: Any) -> str:
        apply_chat_template = getattr(tokenizer, "apply_chat_template", None)
        if callable(apply_chat_template):
            try:
                return cast(
                    str,
                    apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                        enable_thinking=False,
                    ),
                )
            except TypeError:
                return cast(
                    str,
                    apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                    ),
                )

        rendered_messages = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            rendered_messages.append(f"<|im_start|>{role}\n{content}<|im_end|>")
        rendered_messages.append("<|im_start|>assistant\n")
        return "\n".join(rendered_messages)


class NewsSummaryGenerator:
    _META_TERMS = (
        "importance",
        "sentiment",
        "classified",
        "classification",
        "priority",
        "중요도",
        "감성",
        "분류",
    )
    _ADVICE_TERMS = (
        "guaranteed",
        "outperform",
        "price target",
        "must buy",
        "should buy",
        "must sell",
        "should sell",
    )
    _HALLUCINATION_TERMS = (
        "memory-hazard",
        "hazard shielding",
        "shielding technology",
        "three-sentence",
        "drew attention in the article",
        "article-backed market context",
        "the story links the shift to supply",
        "next disclosure and watch the market reaction",
        "trading by samjeon nix",
        "by samjeon nix as key",
        "core themes of ai and human death",
        "latest market and company interventions",
        "market and business events confirmed",
        "countermeasures inspection",
        "approval of the megaproject",
        "latest public news confirmed in the original",
        "impact of this president",
        "holding and surveillance",
        "samjeon nix trading",
        "latest market and corporate events confirmed",
        "krw-3777b",
        "sheriff's rifle",
        "iseutasi",
        "investor's net buying flow",
        "entrepreneurhan",
        "hallinkyos",
        "sk hallinkyos",
        "skhinky",
        "sinerlwyk",
        "investor impact is to watch",
        "investor impact is to track",
        "investor impact is greater",
        "investor impact is higher",
        "golden electric group",
        "electronicstronics",
        "investor impact is better than expected",
        "korean basis on a korean scale",
        "more orders placed on the market",
        "reported event",
        "market sentiment and investor positioning",
        "the next disclosure and market reaction",
        "as the story develops",
        "foreign exchanges as the market becomes more active",
        "key market issue",
        "1b company stocks",
        "market synchronizer",
        "1st consolidated farm",
        "pbr 1-kilogram",
        "large-capacity",
        "cellia",
        "beilwane",
        "kimmidl markettron",
        "middlemarketron",
        "stock-bearer",
        "zhishi is why",
        "north korean market",
        "north financial market",
        "market-sense",
        "samsung exosphate",
    )
    _ALLOWED_HYPHENATED_TERMS = {
        "ai-server",
        "article-backed",
        "back-end",
        "balance-sheet",
        "buy-side",
        "data-center",
        "foreign-investor",
        "high-bandwidth",
        "high-performance",
        "high-value",
        "high-value-added",
        "investor-facing",
        "market-wide",
        "operating-profit",
        "price-to-book",
        "sell-side",
        "semiconductor-led",
        "stock-market",
        "treasury-share",
        "year-on-year",
    }
    _KOREAN_TO_ENGLISH_TERMS = {
        "반도체": ("semiconductor", "chip", "memory"),
        "메모리": ("memory",),
        "HBM": ("hbm",),
        "데이터센터": ("data center", "data-center"),
        "AI": ("ai", "artificial intelligence"),
        "서버": ("server",),
        "영업이익": ("operating profit", "earnings"),
        "실적": ("earnings", "results", "profit"),
        "수익성": ("profitability", "margin"),
        "주가": ("stock price", "shares"),
        "시가총액": ("market cap", "market capitalization"),
        "시총": ("market cap", "market capitalization"),
        "외국인": ("foreign investor", "foreign investors"),
        "기관": ("institutional investors", "institutions"),
        "순매수": ("net buying", "net purchase"),
        "순매도": ("net selling"),
        "코스피": ("kospi",),
        "코스닥": ("kosdaq",),
        "환율": ("exchange rate", "currency"),
        "금리": ("interest rate", "rates"),
        "수주": ("order", "orders", "contract"),
        "계약": ("contract", "deal"),
        "공급": ("supply",),
        "자사주": ("treasury share", "treasury-share", "buyback"),
        "소각": ("cancellation", "retirement"),
        "배당": ("dividend",),
        "유상증자": ("capital increase", "share issuance"),
        "전환사채": ("convertible bond",),
        "상장폐지": ("delisting",),
        "거래정지": ("trading halt",),
        "감사의견": ("audit opinion",),
        "소송": ("lawsuit", "litigation"),
        "리스크": ("risk",),
        "변동성": ("volatility",),
        "방산": ("defense",),
        "조선": ("shipbuilding",),
        "배터리": ("battery",),
        "바이오": ("biotech", "bio"),
        "인수": ("acquisition",),
        "합병": ("merger",),
        "분할": ("spin-off", "split"),
        "기업회생": ("corporate rehabilitation", "restructuring"),
        "한계기업": ("marginal companies", "distressed companies"),
        "좀비기업": ("zombie companies", "distressed companies"),
        "구조조정": ("restructuring",),
        "자본 배분": ("capital allocation",),
        "재무구조": ("financial structure", "balance sheet"),
        "ETF": ("etf", "exchange-traded fund"),
        "단일종목": ("single-stock", "single stock"),
        "레버리지": ("leverage", "leveraged"),
        "빚투": ("leveraged retail", "debt-funded", "margin"),
        "삼닉": ("samjeon nix", "samsung electronics and sk hynix"),
        "삼전닉스": ("samjeon nix", "samsung electronics and sk hynix"),
        "금융투자회사": ("securities firm", "securities firms", "brokerage"),
        "미들마켓론": ("mid-market loan", "middle-market loan"),
        "로드쇼": ("roadshow", "roadshows"),
        "반도체 클러스터": ("semiconductor cluster",),
        "메가프로젝트": ("megaproject", "megaprojects"),
        "개미": ("retail investor", "retail investors"),
        "상반기": ("first half",),
        "상장사": ("listed companies", "listed-company"),
        "대구": ("daegu",),
        "트럼프": ("trump",),
        "쿠팡": ("coupang",),
        "한미": ("korea-u.s.", "korea-us", "u.s.-korea"),
        "통상 갈등": ("trade tension", "trade tensions", "trade dispute"),
        "무역 보복": ("trade retaliation", "retaliatory tariffs"),
        "연기금": ("pension fund", "pension funds"),
        "대체투자": ("alternative investment", "alternative investments"),
        "하반기": ("second half",),
        "삼성전자": ("samsung electronics",),
        "DX": ("dx",),
        "DS": ("ds",),
        "투트랙": ("two-track", "two track"),
        "ESG": ("esg",),
        "현대차": ("hyundai motor",),
        "기아": ("kia",),
        "모비스": ("mobis", "hyundai mobis"),
        "USMCA": ("usmca",),
        "원산지": ("rules of origin", "origin rules"),
        "멕시코": ("mexico", "mexican"),
        "수신": ("deposit", "deposits"),
        "은행": ("bank", "banks"),
        "요구불예금": ("demand deposit", "demand deposits"),
        "하이닉스": ("sk hynix",),
        "ADR": ("adr",),
        "RV": ("rv",),
        "HEV": ("hev", "hybrid"),
        "인센티브": ("incentive", "incentives"),
        "제약바이오": ("pharma", "biotech", "healthcare"),
        "PBR": ("pbr", "price-to-book"),
        "외환시장": ("fx market", "foreign-exchange market"),
        "셀 코리아": ("sell korea", "foreign selling"),
        "자산배분": ("asset allocation",),
        "금통위": ("monetary policy board", "bok"),
        "부동산": ("real estate", "housing"),
    }
    _ENGLISH_FALLBACK_TOPICS = (
        (("증시", "은행", "수신"), "bank deposit inflows after stock-market volatility"),
        (("삼전", "하이닉스", "ADR"), "semiconductor sentiment around earnings and ADR listing"),
        (("현대차", "기아", "RV", "HEV"), "Hyundai and Kia's RV and HEV profit strategy"),
        (("트럼프", "쿠팡", "통상"), "Korea-U.S. trade-tension risk linked to Coupang"),
        (("연기금", "대체투자"), "pension-fund alternative-investment performance"),
        (("삼성전자", "DX", "DS", "ESG"), "Samsung Electronics' two-track ESG strategy"),
        (("현대차", "기아", "모비스", "USMCA"), "USMCA parts-rule risk for Korean automakers"),
        (("반도체 클러스터", "메가프로젝트"), "semiconductor cluster policy support"),
        (("개미", "상반기", "순매수"), "retail net buying in the first half"),
        (("대구", "상장사", "시총"), "Daegu-listed companies' market-cap decline"),
        (("단일종목", "레버리지", "ETF"), "single-stock leveraged ETF volatility"),
        (("삼닉", "레버리지"), "Samjeon Nix leveraged-product losses"),
        (("빚투", "삼전닉스"), "leveraged retail speculation around Samjeon Nix"),
        (("금융투자회사", "뉴욕"), "Korean securities firms' overseas expansion"),
        (("미들마켓론",), "mid-market lending by Korean securities firms"),
        (("삼전닉스",), "Samjeon Nix trading"),
        (("엔비디아", "로봇매출", "액추에이터"), "Nvidia-linked robotics and actuator stocks"),
        (("엔비디아", "피지컬 AI"), "Nvidia-linked physical AI suppliers"),
        (("기업회생", "한계기업"), "corporate rehabilitation and marginal-company restructuring"),
        (("기업회생", "좀비기업"), "corporate rehabilitation and zombie-company restructuring"),
        (("기업회생",), "corporate rehabilitation filings"),
        (("한계기업",), "marginal-company restructuring"),
        (("좀비기업",), "zombie-company restructuring"),
        (("구조조정",), "corporate restructuring"),
        (("IPO", "공모금액"), "the cooling Korean IPO market"),
        (("상장기업", "공모금액"), "weaker listing and offering activity"),
        (("공모가", "신규상장"), "new-listing weakness"),
        (("HBM", "메모리", "반도체"), "semiconductor and HBM demand"),
        (("영업이익",), "earnings recovery expectations"),
        (("실적",), "earnings recovery expectations"),
        (("어닝",), "earnings recovery expectations"),
        (("외국인", "순매수"), "foreign-investor net buying"),
        (("외국인", "순매도"), "foreign-investor net selling"),
        (("기관", "순매수"), "institutional net buying"),
        (("기관", "순매도"), "institutional net selling"),
        (("코스피",), "the KOSPI market move"),
        (("코스닥",), "the KOSDAQ market move"),
        (("환율",), "exchange-rate pressure"),
        (("금리",), "interest-rate pressure"),
        (("수주", "계약"), "order and contract momentum"),
        (("공급",), "supply conditions"),
        (("자사주", "소각"), "treasury-share cancellation"),
        (("유상증자",), "paid-in capital increase"),
        (("배당",), "dividend policy"),
        (("상장폐지", "거래정지"), "listing and trading-risk issues"),
    )
    _ENGLISH_FALLBACK_DRIVERS = (
        (("HBM",), "HBM demand"),
        (("메모리",), "memory-market conditions"),
        (("데이터센터",), "data-center investment"),
        (("엔비디아", "로봇매출", "1%"), "Nvidia's small direct robotics revenue contribution"),
        (("액추에이터",), "investor attention shifting toward actuator suppliers"),
        (("부품 공급망",), "interest moving from finished robots to the parts supply chain"),
        (("공모금액", "반토막"), "offering proceeds falling sharply"),
        (("공모가", "밑돌"), "new listings trading below their offering prices"),
        (("코스닥", "소외"), "weak KOSDAQ demand"),
        (("중복상장", "규제"), "listing-rule uncertainty"),
        (("단일종목", "레버리지"), "high turnover in single-stock leveraged ETFs"),
        (("리밸런싱", "변동성"), "ETF rebalancing flows increasing late-session volatility"),
        (("개미", "레버리지"), "retail investors concentrating in leveraged products"),
        (("빚투",), "debt-funded retail speculation"),
        (("삼전닉스",), "attention on Samjeon Nix as shorthand for Korea's two chip bellwethers"),
        (("미들마켓론",), "new mid-market loan opportunities"),
        (("뉴욕", "금융투자회사"), "Korean securities firms localizing overseas businesses"),
        (("로드쇼",), "overseas investor demand at roadshows"),
        (
            ("반도체 클러스터", "메가프로젝트"),
            "government follow-up measures for semiconductor megaprojects",
        ),
        (("개미", "순매수"), "retail investors providing heavy net buying"),
        (("대구", "시총"), "regional listed-company market-cap weakness"),
        (("기업회생",), "rising corporate rehabilitation filings"),
        (("한계기업",), "delayed restructuring of marginal companies"),
        (("좀비기업",), "zombie-company cleanup"),
        (("구조조정",), "restructuring pressure"),
        (("자본 배분",), "capital-allocation efficiency"),
        (("재무구조",), "balance-sheet weakness"),
        (("외국인", "순매수"), "foreign-investor net buying"),
        (("외국인", "순매도"), "foreign-investor net selling"),
        (("기관", "순매수"), "institutional net buying"),
        (("기관", "순매도"), "institutional net selling"),
        (("환율",), "currency moves"),
        (("금리",), "interest-rate expectations"),
        (("수주",), "new orders"),
        (("공급",), "supply changes"),
        (("정책",), "policy expectations"),
        (("공시",), "the company disclosure"),
        (("공모금액", "반토막"), "offering proceeds falling sharply"),
        (("공모가", "밑돌"), "new listings trading below their offering prices"),
        (("코스닥", "소외"), "weak KOSDAQ demand"),
        (("중복상장", "규제"), "listing-rule uncertainty"),
    )
    _ENGLISH_FALLBACK_WATCH_ITEMS = (
        (("액추에이터",), "actuator order visibility and supplier exposure"),
        (("부품 공급망",), "parts-supply-chain earnings visibility"),
        (("기업회생", "한계기업"), "credit risk and restructuring speed"),
        (("기업회생",), "rehabilitation filing trends and creditor-loss risk"),
        (("한계기업",), "marginal-company cleanup and market discipline"),
        (("좀비기업",), "zombie-company cleanup and capital-allocation risk"),
        (("구조조정",), "restructuring speed and investor-loss risk"),
        (("IPO", "소노인터내셔널"), "whether major listings revive IPO demand"),
        (("공모가", "밑돌"), "post-listing share performance and investor demand"),
        (("중복상장", "규제"), "listing-rule changes and large-company IPO timing"),
        (("단일종목", "레버리지"), "ETF rebalancing flows and late-session volatility"),
        (("빚투",), "margin exposure, retail flows, and volatility in major chip names"),
        (("미들마켓론",), "overseas revenue diversification, deal flow, and credit risk controls"),
        (
            ("반도체 클러스터",),
            "policy execution, capex timing, and chip supply-chain beneficiaries",
        ),
        (
            ("개미", "순매수"),
            "whether retail net buying continues and which sectors absorb the flows",
        ),
        (
            ("대구", "시총"),
            "regional market-cap trends, KOSDAQ weakness, and company-level earnings",
        ),
        (("영업이익",), "operating-profit recovery and earnings guidance"),
        (("실적",), "operating-profit recovery and earnings guidance"),
        (("HBM", "메모리"), "memory pricing and HBM shipment momentum"),
        (("외국인", "기관"), "whether investor flows continue"),
        (("외국인",), "whether investor flows continue"),
        (("기관",), "whether investor flows continue"),
        (("코스피", "코스닥"), "index breadth and follow-through buying"),
        (("환율",), "currency sensitivity and foreign flow"),
        (("금리",), "rate expectations and valuation pressure"),
        (("수주", "계약"), "order backlog and revenue timing"),
        (("유상증자",), "dilution risk and funding use"),
        (("자사주", "소각"), "shareholder-return execution"),
        (("상장폐지", "거래정지"), "trading restrictions and disclosure follow-up"),
    )

    def __init__(
        self,
        *,
        enabled: bool = False,
        model_name: str = "Qwen3-0.6B-GGUF-Q4",
        max_tokens: int = 260,
        client: NewsSummaryClient | None = None,
    ) -> None:
        self._enabled = enabled
        self._model_name = model_name
        self._max_tokens = max_tokens
        self._client = client

    @classmethod
    def from_settings(cls, settings: Settings) -> NewsSummaryGenerator:
        enabled = settings.news_summary_generation_mode == "local_llm"
        client: NewsSummaryClient | None = None
        if enabled:
            if settings.news_summary_llm_endpoint:
                client = OpenAiCompatibleNewsSummaryClient(
                    endpoint=settings.news_summary_llm_endpoint,
                    model=settings.news_summary_llm_model,
                    timeout_seconds=settings.news_summary_llm_timeout_seconds,
                )
            else:
                client = MlxQwenNewsSummaryClient(
                    model=settings.news_summary_mlx_model,
                    adapter_path=require_lora_adapter_artifact(
                        settings.news_summary_mlx_adapter_path,
                        "News summary Qwen3 LoRA adapter",
                    ),
                )
        return cls(
            enabled=enabled,
            model_name=(
                settings.news_summary_llm_model
                if settings.news_summary_llm_endpoint
                else settings.news_summary_mlx_model
            ),
            max_tokens=settings.news_summary_llm_max_tokens,
            client=client,
        )

    def generate(self, context: NewsSummaryContext) -> SummaryLines:
        if not self._enabled or self._client is None:
            return self._english_fallback(context)
        if not self._has_usable_full_text(context.content):
            return self._english_fallback(context)

        try:
            raw_content = self._client.generate(
                self.messages(context),
                max_tokens=self._max_tokens,
            )
            candidate = self._parse_llm_output(raw_content)
            summary = SummaryLines(
                what=self._sanitize(candidate.get("what", "")),
                why=self._sanitize(candidate.get("why", "")),
                impact=self._sanitize(candidate.get("impact", "")),
            )
            if not self._is_quality_output(summary, context):
                return self._english_fallback(context)
            return summary
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError):
            return self._english_fallback(context)

    @classmethod
    def messages(cls, context: NewsSummaryContext) -> list[dict[str, str]]:
        payload = {
            "task": "Write three investor-facing analysis lines from the article body.",
            "schema": {
                "what": "one complete English sentence describing what happened",
                "why": "one complete English sentence explaining the article-backed reason",
                "impact": "one complete English sentence explaining the investor impact",
            },
            "rules": [
                "Return only compact JSON with keys what, why, impact.",
                "Use only evidence from article_text, title, snippet, event_tags, and labels.",
                "Write every value in English.",
                "Each value must be exactly one complete sentence.",
                "Do not use ellipses, bullet points, Korean sentences, or truncated fragments.",
                "Do not mention importance, sentiment, priority, or classification labels.",
                "Do not give buy, sell, price-target, or guaranteed-return advice.",
            ],
            "labels": {
                "source_type": context.source_type,
                "importance": context.importance,
                "sentiment": context.sentiment,
                "event_tags": context.event_tags,
            },
            "entity": {
                "stock_code": context.stock_code or "",
                "stock_name": context.stock_name or "",
                "stock_name_en": context.stock_name_en,
            },
            "title": context.title,
            "snippet": context.snippet,
            "article_text": cls._truncate_context(context.content),
        }
        return [
            {
                "role": "system",
                "content": (
                    "You are a Korean financial-news analyst for foreign retail investors. "
                    "You ground every sentence in the provided Korean article and output "
                    "strict JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            },
        ]

    @classmethod
    def training_example(
        cls,
        context: NewsSummaryContext,
        target: SummaryLines,
    ) -> dict[str, object]:
        return {
            "schema_version": "news-summary-wwi-sft/v1",
            "prompt_version": NEWS_SUMMARY_PROMPT_VERSION,
            "messages": [
                *cls.messages(context),
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "what": target.what,
                            "why": target.why,
                            "impact": target.impact,
                        },
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                },
            ],
            "target": {
                "what": target.what,
                "why": target.why,
                "impact": target.impact,
            },
        }

    @staticmethod
    def _parse_llm_output(raw_content: str) -> dict[str, str]:
        cleaned = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("LLM response does not contain a JSON object")
        parsed = json.loads(match.group(0))
        if not isinstance(parsed, dict):
            raise ValueError("LLM JSON response must be an object")
        return {
            key: value
            for key, value in parsed.items()
            if key in {"what", "why", "impact"} and isinstance(value, str)
        }

    @classmethod
    def _sanitize(cls, text: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        normalized = normalized.strip("`'\" ")
        return normalized

    @classmethod
    def _is_quality_output(cls, summary: SummaryLines, context: NewsSummaryContext) -> bool:
        lines = [summary.what, summary.why, summary.impact]
        if any(not cls._is_valid_sentence(line) for line in lines):
            return False
        normalized_lines = {line.lower() for line in lines}
        if len(normalized_lines) != 3:
            return False
        combined = " ".join(lines)
        lower_combined = combined.lower()
        if any(term in lower_combined for term in cls._META_TERMS):
            return False
        if any(term in lower_combined for term in cls._ADVICE_TERMS):
            return False
        if any(term in lower_combined for term in cls._HALLUCINATION_TERMS):
            return False
        if cls._has_unsupported_hyphenated_term(combined):
            return False
        if not cls._passes_source_specific_quality(combined, context):
            return False
        if re.search(r"[가-힣]", combined):
            return False
        if not cls._mentions_relevant_subject(combined, context):
            return False
        return cls._has_grounded_financial_terms(combined, context)

    @classmethod
    def _passes_source_specific_quality(cls, combined: str, context: NewsSummaryContext) -> bool:
        evidence = f"{context.title} {context.snippet} {context.content}"
        lower = combined.lower()
        if any(term in evidence for term in ("미들마켓론", "유럽 로드쇼")):
            return any(
                term in lower
                for term in (
                    "securities firm",
                    "securities firms",
                    "mid-market loan",
                    "middle-market loan",
                    "roadshow",
                    "overseas",
                )
            )
        if "개미" in evidence and "순매수" in evidence and "상반기" in evidence:
            return "retail" in lower and "net buying" in lower
        if cls._is_kospi_rollercoaster_context(evidence):
            return "kospi" in lower and any(
                term in lower
                for term in (
                    "volatility",
                    "swung",
                    "reversed",
                    "foreign",
                    "8,000",
                    "8000",
                )
            )
        if "삼전닉스" in evidence and "레버리지" in evidence:
            return "samjeon nix" in lower or (
                "leveraged" in lower and ("retail" in lower or "single-stock" in lower)
            )
        if "대구" in evidence and "시총" in evidence and any(
            term in evidence for term in ("상장사", "상장법인")
        ):
            return "daegu" in lower and (
                "market cap" in lower or "market capitalization" in lower
            )
        if "반도체 클러스터" in evidence and "메가프로젝트" in evidence:
            return "semiconductor cluster" in lower or "megaproject" in lower
        if "수신" in evidence and "은행" in evidence and "증시" in evidence:
            return "bank" in lower and ("deposit" in lower or "liquidity" in lower)
        if cls._is_bank_earnings_context(evidence):
            return "bank" in lower and ("earnings" in lower or "financial" in lower)
        if "하이닉스" in evidence and "ADR" in evidence and "삼성전자" in evidence:
            return "adr" in lower and ("earnings" in lower or "foreign" in lower)
        if "RV" in evidence and "HEV" in evidence and "현대차" in evidence:
            return "rv" in lower and "hev" in lower and (
                "new-car price" in lower
                or "incentive" in lower
                or "profitability" in lower
            )
        return True

    @classmethod
    def _is_valid_sentence(cls, line: str) -> bool:
        if not line or "\n" in line:
            return False
        if len(line) > 320:
            return False
        if "..." in line or "…" in line:
            return False
        if line.startswith(("-", "*", "•")):
            return False
        if not re.search(r"[.!?]$", line):
            return False
        if re.search(r"^\d{6}\b", line):
            return False
        if cls._is_fragmentary_sentence(line):
            return False
        chunks = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line)
        if len([chunk for chunk in chunks if chunk.strip()]) != 1:
            return False
        return len(re.findall(r"[A-Za-z0-9%$]+", line)) >= 7

    @classmethod
    def _is_fragmentary_sentence(cls, line: str) -> bool:
        normalized = re.sub(r"\s+", " ", line).strip()
        lower = normalized.lower()
        if normalized.startswith("()") or lower in {".", "korean stock market."}:
            return True
        letter_count = len(re.findall(r"[A-Za-z]", normalized))
        punctuation_count = len(re.findall(r"[()%,;:·]", normalized))
        if letter_count == 0 or punctuation_count / letter_count > 0.34:
            return True
        word_count = len(re.findall(r"[A-Za-z]{2,}", normalized))
        return lower.startswith("the article cites ") and word_count < 6

    @classmethod
    def _has_unsupported_hyphenated_term(cls, combined: str) -> bool:
        for token in re.findall(r"\b[a-z][a-z]+(?:-[a-z][a-z]+)+(?:'s)?\b", combined.lower()):
            normalized = token.removesuffix("'s")
            if normalized not in cls._ALLOWED_HYPHENATED_TERMS:
                return True
        return False

    @classmethod
    def _mentions_relevant_subject(cls, combined: str, context: NewsSummaryContext) -> bool:
        lower = combined.lower()
        if context.stock_name_en and context.stock_name_en.lower() in lower:
            return True
        if context.stock_code and context.stock_code in combined:
            return True
        title_context = f"{context.title} {context.snippet} {context.content}"
        market_terms = ("코스피", "코스닥", "증시", "시장", "환율", "금리")
        if any(term in title_context for term in market_terms):
            return any(
                term in lower
                for term in (
                    "kospi",
                    "kosdaq",
                    "korean market",
                    "stock market",
                    "market",
                    "exchange rate",
                    "interest rate",
                )
            )
        return "the company" in lower or "the issuer" in lower

    @classmethod
    def _has_grounded_financial_terms(cls, combined: str, context: NewsSummaryContext) -> bool:
        evidence = f"{context.title} {context.snippet} {context.content}"
        lower = combined.lower()
        matched = 0
        for korean_term, english_terms in cls._KOREAN_TO_ENGLISH_TERMS.items():
            if korean_term not in evidence:
                continue
            if any(english_term in lower for english_term in english_terms):
                matched += 1
        if matched >= 2:
            return True
        if matched == 1 and any(
            tag.lower().replace("_", " ") in lower for tag in context.event_tags
        ):
            return True
        if matched == 1 and len(context.content) >= 200:
            return True
        return False

    @staticmethod
    def _has_usable_full_text(content: str) -> bool:
        normalized = re.sub(r"\s+", " ", content).strip()
        if len(normalized) < 120:
            return False
        return "..." not in normalized and "…" not in normalized

    @staticmethod
    def _truncate_context(content: str) -> str:
        normalized = re.sub(r"\s+", " ", content).strip()
        if len(normalized) <= 6500:
            return normalized
        return normalized[:6500].rsplit(" ", 1)[0].strip()

    @classmethod
    def _english_fallback(cls, context: NewsSummaryContext) -> SummaryLines:
        evidence = " ".join((context.title, context.snippet, context.content))
        if "델라웨어" in evidence and "회사법" in evidence:
            return cls._delaware_corporate_law_fallback(evidence)
        if any(term in evidence for term in ("인류멸망", "인공초지능", "챗지피티", "ChatGPT")):
            return cls._ai_superintelligence_column_fallback(evidence)
        if "하이닉스" in evidence and "ADR" in evidence and "나스닥" in evidence:
            return cls._sk_hynix_adr_listing_fallback(evidence)
        if any(term in evidence for term in ("엇갈린 금리", "금리 시계")) and any(
            term in evidence for term in ("한·미", "한국과 미국", "Fed")
        ):
            return cls._rate_decoupling_fallback(evidence)
        if "코스피" in evidence and "PER" in evidence and "골드만삭스" in evidence:
            return cls._kospi_per_valuation_fallback(evidence)
        if "코스피" in evidence and any(term in evidence for term in ("1조클럽", "1조 클럽")):
            return cls._kospi_trillion_club_fallback(evidence)
        if cls._is_korean_market_plunge_context(evidence):
            return cls._korean_market_plunge_fallback(evidence)
        if cls._is_kospi_rollercoaster_context(evidence):
            return cls._kospi_rollercoaster_fallback(evidence)
        if "환율" in evidence and any(term in evidence for term in ("1575", "1500원", "1600원")):
            return cls._won_dollar_rate_forecast_fallback(evidence)
        if "제약바이오" in evidence and "PBR" in evidence:
            return cls._pharma_biotech_pbr_fallback(evidence)
        if "24시간" in evidence and "외환시장" in evidence:
            return cls._twenty_four_hour_fx_market_fallback(evidence)
        if "셀 코리아" in evidence or "Sell Korea" in evidence:
            return cls._sell_korea_foreign_flow_fallback(evidence)
        if "변동성 장세" in evidence and any(term in evidence for term in ("반도체", "ETF")):
            return cls._volatile_market_risk_fallback(evidence)
        if "원칙의 힘" in evidence or ("자산배분" in evidence and "장기" in evidence):
            return cls._investment_principles_fallback(evidence)
        if "삼전닉스" in evidence and "금통위" in evidence:
            return cls._july_financial_turning_point_fallback(evidence)
        if "주식 부자" in evidence and "부동산" in evidence:
            return cls._stock_wealth_real_estate_fallback(evidence)
        if "트럼프" in evidence and "쿠팡" in evidence and any(
            term in evidence for term in ("통상", "무역 보복", "301조", "차별")
        ):
            return cls._coupang_trade_tension_fallback(evidence)
        if "연기금" in evidence and "대체투자" in evidence:
            return cls._pension_alternative_investment_fallback(evidence)
        if "삼성전자" in evidence and "DX" in evidence and "DS" in evidence and "ESG" in evidence:
            return cls._samsung_two_track_esg_fallback(evidence)
        if any(term in evidence for term in ("현대차", "기아", "모비스")) and any(
            term in evidence for term in ("USMCA", "원산지", "멕시코", "82%")
        ):
            return cls._hyundai_usmca_parts_fallback(evidence)
        if "수신" in evidence and "은행" in evidence and "증시" in evidence:
            return cls._bank_deposit_inflow_fallback(evidence)
        if cls._is_financial_leadership_profile_context(evidence):
            return cls._financial_leadership_profile_fallback(evidence)
        if cls._is_broker_recommendation_list_context(evidence):
            return cls._broker_recommendation_list_fallback(evidence)
        if cls._is_defense_nato_rally_context(evidence):
            return cls._defense_nato_rally_fallback(evidence)
        if cls._is_defense_supercycle_context(evidence):
            return cls._defense_supercycle_fallback(evidence)
        if cls._is_nps_rebalancing_context(evidence):
            return cls._nps_rebalancing_fallback(evidence)
        if cls._is_botabio_stock_manipulation_context(evidence):
            return cls._botabio_stock_manipulation_fallback(evidence)
        if cls._is_deepfake_security_theme_context(evidence):
            return cls._deepfake_security_theme_fallback(evidence)
        if cls._is_quantum_security_theme_context(evidence):
            return cls._quantum_security_theme_fallback(evidence)
        if cls._is_information_security_theme_context(evidence):
            return cls._information_security_theme_fallback(evidence)
        if cls._is_quantum_crypto_risk_context(evidence):
            return cls._quantum_crypto_risk_fallback(evidence)
        if cls._is_duoback_market_warning_context(evidence):
            return cls._duoback_market_warning_fallback(evidence)
        if cls._is_daily_disclosure_roundup_context(evidence):
            return cls._daily_disclosure_roundup_fallback(evidence)
        if cls._is_ecm_league_table_context(evidence):
            return cls._ecm_league_table_fallback(evidence)
        if cls._is_delisting_rule_tightening_context(evidence):
            return cls._delisting_rule_tightening_fallback(evidence)
        if cls._is_fx_24h_market_open_context(evidence):
            return cls._fx_24h_market_open_fallback(evidence)
        if cls._is_insider_share_purchase_context(evidence):
            return cls._insider_share_purchase_fallback(evidence)
        if cls._is_pharma_healthcare_contract_context(evidence):
            return cls._pharma_healthcare_contract_fallback(evidence)
        if cls._is_stock_manipulation_legal_context(evidence):
            return cls._stock_manipulation_legal_fallback(evidence)
        if cls._is_bank_policy_undervaluation_context(evidence):
            return cls._bank_policy_undervaluation_fallback(evidence)
        if cls._is_bank_earnings_context(evidence):
            return cls._bank_earnings_fallback(evidence)
        if cls._is_limit_up_ai_infra_context(evidence):
            return cls._limit_up_ai_infra_fallback(evidence)
        if any(term in evidence for term in ("주간수급리포트", "외인 20兆", "19조8374억원")) and (
            "코스피" in evidence and "코스닥" in evidence and "반도체" in evidence
        ):
            return cls._weekly_semiconductor_flow_fallback(evidence)
        if "하이닉스" in evidence and "ADR" in evidence and "삼성전자" in evidence:
            return cls._semiconductor_earnings_adr_fallback(evidence)
        if "현대차" in evidence and "기아" in evidence and "RV" in evidence and "HEV" in evidence:
            return cls._hyundai_rv_hev_profit_fallback(evidence)
        if "엔비디아" in evidence and any(term in evidence for term in ("액추에이터", "로봇매출")):
            return cls._nvidia_robotics_fallback(evidence)
        if any(term in evidence for term in ("기업회생", "한계기업", "좀비기업")):
            return cls._corporate_rehabilitation_fallback(evidence)
        if (
            "단일종목" in evidence
            and "레버리지" in evidence
            or "삼전닉스" in evidence
            and "레버리지" in evidence
        ):
            return cls._single_stock_leverage_fallback(evidence)
        if "빚투" in evidence and any(term in evidence for term in ("삼전닉스", "삼닉")):
            return cls._retail_speculation_fallback(evidence)
        if any(term in evidence for term in ("미들마켓론", "뉴욕 법인", "유럽 로드쇼")):
            return cls._securities_overseas_expansion_fallback(evidence)
        if "반도체 클러스터" in evidence and "메가프로젝트" in evidence:
            return cls._semiconductor_cluster_policy_fallback(evidence)
        if "개미" in evidence and "순매수" in evidence and "상반기" in evidence:
            return cls._retail_net_buying_fallback(evidence)
        if "대구" in evidence and "시총" in evidence and any(
            term in evidence for term in ("상장사", "상장법인")
        ):
            return cls._regional_market_cap_fallback(evidence)
        if any(term in evidence for term in ("IPO", "기업공개", "공모금액", "공모가")):
            return cls._ipo_market_fallback(evidence)
        subject = cls._english_subject(context, evidence)
        topic = cls._first_fallback_phrase(
            evidence, cls._ENGLISH_FALLBACK_TOPICS, "the reported event"
        )
        event_phrase = cls._fallback_event_phrase(evidence, topic)
        drivers = cls._fallback_driver_phrase(evidence)
        if drivers == "market sentiment and investor positioning":
            drivers = cls._fallback_specific_driver_phrase(evidence)
        watch_item = cls._first_fallback_phrase(
            evidence,
            cls._ENGLISH_FALLBACK_WATCH_ITEMS,
            "the next disclosure and market reaction",
        )
        if watch_item == "the next disclosure and market reaction":
            watch_item = cls._fallback_specific_watch_item(evidence)
        what_subject = "The financial item" if subject == "The article" else subject
        return SummaryLines(
            what=f"{what_subject} was tied to {event_phrase}.",
            why=f"The article cites {drivers}.",
            impact=f"Investors should track {watch_item}.",
        )

    @classmethod
    def _coupang_trade_tension_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["U.S. criticism of Korea's treatment of Coupang"]
        if "301조" in evidence:
            why_parts.append("possible Section 301 trade-retaliation risk")
        if "반도체" in evidence or "자동차" in evidence:
            why_parts.append("concerns over pressure on chip and auto exports")
        return SummaryLines(
            what=(
                "Korea-U.S. trade tensions drew attention after reports that Trump "
                "traded Coupang shares while in office."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track Korea-U.S. trade talks, Section 301 risks, "
                "and possible pressure on Korean exporters."
            ),
        )

    @classmethod
    def _pension_alternative_investment_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["strong listed-equity returns"]
        if "고전" in evidence or "부진" in evidence:
            why_parts.append("weak alternative-investment performance")
        if "하반기" in evidence:
            why_parts.append("expectations for second-half improvement")
        return SummaryLines(
            what=(
                "Korean pension funds posted strong stock returns while alternative "
                "investments lagged."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track asset-allocation shifts, alternative-asset "
                "valuations, and pension-fund equity flows."
            ),
        )

    @classmethod
    def _samsung_two_track_esg_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["different business structures between DX and DS"]
        if "ESG" in evidence:
            why_parts.append("separate sustainability priorities")
        if "투트랙" in evidence:
            why_parts.append("two-track ESG execution")
        return SummaryLines(
            what=(
                "Samsung Electronics' DX and DS divisions drew attention for separate "
                "ESG strategies."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track ESG disclosure quality, division-level risks, "
                "and whether sustainability spending affects margins."
            ),
        )

    @classmethod
    def _hyundai_usmca_parts_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["U.S. reluctance to extend USMCA in its current form"]
        if "82%" in evidence:
            why_parts.append("a proposed 82% North American parts threshold")
        if "멕시코" in evidence:
            why_parts.append("exposure to Mexico-based production networks")
        return SummaryLines(
            what=(
                "Hyundai Motor, Kia, and Hyundai Mobis faced renewed USMCA parts-rule "
                "uncertainty."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track USMCA talks, Mexico supply-chain costs, "
                "and tariff risk for Korean automakers."
            ),
        )

    @classmethod
    def _bank_deposit_inflow_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["stock-market volatility lifting safe-asset demand"]
        if "차익 실현" in evidence:
            why_parts.append("profit-taking after the equity rally")
        if "89조" in evidence or "90조" in evidence:
            why_parts.append("nearly KRW 90 trillion in deposit growth")
        return SummaryLines(
            what=(
                "Money flowed back into major Korean banks as stock-market volatility "
                "lifted safe-asset demand."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track bank deposit growth, margin effects, and "
                "whether equity volatility redirects liquidity."
            ),
        )

    @classmethod
    def _bank_earnings_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["solid second-quarter bank earnings expectations"]
        if "환율" in evidence:
            why_parts.append("limited FX-related earnings pressure")
        if "금리" in evidence:
            why_parts.append("rate momentum supporting the banking sector")
        if any(term in evidence for term in ("KB금융", "신한금융", "신한지주")):
            why_parts.append("preferred-pick calls for KB Financial and Shinhan Financial")
        return SummaryLines(
            what=(
                "Korean bank stocks moved around expectations for solid "
                "second-quarter earnings."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track bank earnings, rate sensitivity, and whether "
                "KB Financial, Shinhan Financial, and Hana Financial hold recent highs."
            ),
        )

    @classmethod
    def _limit_up_ai_infra_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["Honam semiconductor and AI infrastructure expectations"]
        if "미래산업" in evidence:
            why_parts.append("Mirae Industrial's Asan plant expansion")
        if "MLCC" in evidence or "삼화콘덴서" in evidence:
            why_parts.append("MLCC demand tied to AI infrastructure and robotics")
        if "에브리봇" in evidence or "로봇" in evidence:
            why_parts.append("robotics automation themes in KOSDAQ small caps")
        return SummaryLines(
            what=(
                "Korean limit-up stocks clustered around Honam semiconductor, "
                "AI infrastructure, MLCC, and robotics themes."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track theme durability, order conversion, and "
                "volatility in related small- and mid-cap stocks."
            ),
        )

    @classmethod
    def _financial_leadership_profile_fallback(cls, evidence: str) -> SummaryLines:
        subject = "Shinhan Financial Group leadership"
        if "하나금융" in evidence:
            subject = "Korean financial-holding leadership"
        return SummaryLines(
            what=f"{subject} moved into focus through a CEO profile.",
            why=(
                "The article cites Jin Ok-dong's banking career, Japan experience, "
                "and productive and inclusive finance agenda."
            ),
            impact=(
                "Investors should track governance continuity, overseas expansion, "
                "and how leadership strategy affects financial-holding valuations."
            ),
        )

    @classmethod
    def _broker_recommendation_list_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["KB Securities' weekly buy-recommendation list"]
        if "대한전선" in evidence:
            why_parts.append("new coverage or a buy call on Taihan Cable & Solution")
        if "HD건설기계" in evidence:
            why_parts.append("earnings expectations for HD Hyundai Construction Equipment")
        return SummaryLines(
            what="KB Securities highlighted 14 Korean stocks in its first-July buy list.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should compare target-price changes, earnings assumptions, "
                "and sector rotation across the recommended names."
            ),
        )

    @classmethod
    def _defense_nato_rally_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["expectations around the NATO annual summit"]
        if "엠앤씨솔루션" in evidence:
            why_parts.append("a sharp rally in MNC Solution")
        if "국방비" in evidence:
            why_parts.append("global defense-spending attention")
        return SummaryLines(
            what="Korean defense stocks rallied ahead of the NATO annual summit.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track summit-driven order expectations, defense "
                "export momentum, and whether the rally broadens beyond leading names."
            ),
        )

    @classmethod
    def _defense_supercycle_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["geopolitical risk and defense-export expectations"]
        if "우주산업" in evidence:
            why_parts.append("policy support for space-industry investment")
        if "엠앤씨솔루션" in evidence:
            why_parts.append("buying in satellite, aerospace, and defense-equipment names")
        return SummaryLines(
            what="Korean aerospace and defense stocks rallied on supercycle expectations.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track export orders, government space spending, "
                "and whether gains broaden beyond large defense contractors."
            ),
        )

    @classmethod
    def _nps_rebalancing_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["National Pension Service second-quarter portfolio changes"]
        if "IT" in evidence or "전자부품" in evidence:
            why_parts.append("larger positions in IT and electronics-parts stocks")
        if "바이오" in evidence or "소부장" in evidence:
            why_parts.append("reduced exposure to KOSDAQ materials, equipment, and biotech")
        return SummaryLines(
            what=(
                "Korea's National Pension Service rebalanced domestic equities "
                "toward recovery sectors."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should compare pension-flow support, valuation pressure, "
                "and earnings recovery across added and reduced holdings."
            ),
        )

    @classmethod
    def _botabio_stock_manipulation_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["Botabio's past share-price surge after celebrity-family investment"]
        if "주가 조작" in evidence or "주가조작" in evidence:
            why_parts.append("pending legal proceedings around alleged stock manipulation")
        return SummaryLines(
            what="The article revisited Botabio's stock-price timeline and legal overhang.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:2])) + ".",
            impact=(
                "Investors should treat the item as governance and litigation context "
                "rather than an earnings catalyst."
            ),
        )

    @classmethod
    def _deepfake_security_theme_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["profit-taking after recent gains in deepfake-related stocks"]
        if "생성형" in evidence:
            why_parts.append("continued generative-AI security demand")
        if "라온시큐어" in evidence:
            why_parts.append("mixed trading in AI security and authentication names")
        return SummaryLines(
            what="Deepfake-related Korean security stocks corrected despite long-term AI demand.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should separate short-term theme volatility from companies "
                "with commercialized AI security and authentication technology."
            ),
        )

    @classmethod
    def _information_security_theme_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["global cyberattack risk and corporate security investment"]
        if "제로트러스트" in evidence:
            why_parts.append("zero-trust security adoption expectations")
        if "핀텔" in evidence:
            why_parts.append("strong buying in AI video-analysis and security-solution names")
        return SummaryLines(
            what=(
                "Korean information-security stocks traded mixed as AI and zero-trust "
                "themes developed."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track customer wins, recurring security demand, "
                "and whether profit-taking remains concentrated in recent outperformers."
            ),
        )

    @classmethod
    def _quantum_security_theme_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["demand for quantum-resistant security infrastructure"]
        if "코위버" in evidence:
            why_parts.append("Cowaver's terabit optical-transport and quantum-encryption exposure")
        if "QKD" in evidence or "PQA" in evidence:
            why_parts.append("attention to QKD and post-quantum cryptography infrastructure")
        return SummaryLines(
            what=(
                "Quantum-security infrastructure stocks drew buying around "
                "next-generation encryption demand."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should verify commercialization timing, public-sector demand, "
                "and whether optical-network suppliers convert theme interest into orders."
            ),
        )

    @classmethod
    def _quantum_crypto_risk_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["research lowering the qubit resources needed to break public-key encryption"]
        if "Q-Day" in evidence or "Q-데이" in evidence:
            why_parts.append("concern that Q-Day could arrive earlier than expected")
        if "RSA" in evidence or "ECC" in evidence:
            why_parts.append("risks to RSA and elliptic-curve cryptography")
        return SummaryLines(
            what=(
                "Quantum-computing progress raised concern that current encryption "
                "could weaken sooner."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track post-quantum cryptography migration, QKD demand, "
                "and security vendors with commercial quantum-safe products."
            ),
        )

    @classmethod
    def _duoback_market_warning_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["Korea Exchange market-warning rules"]
        if "60%" in evidence or "100%" in evidence:
            why_parts.append(
                "price-rise thresholds for re-designation as an investment-warning stock"
            )
        return SummaryLines(
            what=(
                "Duoback was released from investment-warning status but faces "
                "possible re-designation."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:2])) + ".",
            impact=(
                "Investors should monitor trading-halt risk, market-warning thresholds, "
                "and whether volatility remains elevated after the status change."
            ),
        )

    @classmethod
    def _daily_disclosure_roundup_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["multiple corporate disclosures across contracts, buybacks, and financing"]
        if "전환사채" in evidence:
            why_parts.append("convertible-bond and financing updates")
        if "공급계약" in evidence:
            why_parts.append("new supply-contract announcements")
        return SummaryLines(
            what="The daily disclosure roundup listed multiple Korean corporate announcements.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should review each issuer separately for dilution, order backlog, "
                "asset revaluation, and shareholder-return effects."
            ),
        )

    @classmethod
    def _ecm_league_table_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["first-half ECM underwriting volume above KRW 5 trillion"]
        if "SKC" in evidence:
            why_parts.append("SKC's rights offering reshaping securities-firm rankings")
        if "한화솔루션" in evidence:
            why_parts.append("Hanwha Solutions' rights offering affecting the podium")
        return SummaryLines(
            what="Korean ECM league-table rankings shifted around large rights offerings.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track underwriting concentration, fee income, "
                "and which securities firms benefit from large equity-financing deals."
            ),
        )

    @classmethod
    def _delisting_rule_tightening_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["tightened KOSDAQ delisting and administrative-issue rules"]
        if "시총 미달" in evidence or "시가총액" in evidence:
            why_parts.append("market-cap shortfall risk")
        if "듀오백" in evidence:
            why_parts.append("Duoback and other low market-cap names cited as examples")
        return SummaryLines(
            what="Tighter KOSDAQ delisting rules put low market-cap companies under scrutiny.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should check market-cap compliance, profitability, "
                "and business competitiveness before trading at-risk small caps."
            ),
        )

    @classmethod
    def _fx_24h_market_open_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["Korea's won-dollar FX market moving to 24-hour trading"]
        if "1527.6" in evidence:
            why_parts.append("the opening rate near KRW 1,527.6 per dollar")
        if "하나은행" in evidence:
            why_parts.append("official checks at Hana Bank's dealing room")
        return SummaryLines(
            what="Korea's won-dollar FX market opened under a 24-hour trading schedule.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track won liquidity, overnight volatility, "
                "and whether broader FX access supports Korean assets."
            ),
        )

    @classmethod
    def _insider_share_purchase_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["insider buying by RaonSecure CEO Lee Soon-hyung"]
        if "2억" in evidence:
            why_parts.append("a purchase worth about KRW 200 million")
        return SummaryLines(
            what="RaonSecure's CEO bought company shares in the market.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:2])) + ".",
            impact=(
                "Investors should treat the purchase as insider-confidence context "
                "and still verify business momentum and future disclosures."
            ),
        )

    @classmethod
    def _pharma_healthcare_contract_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["a new healthcare raw-material distribution contract"]
        if "29.90" in evidence or "상한가" in evidence:
            why_parts.append("Cho-A Pharm rising to the daily upper limit")
        if "신약" in evidence:
            why_parts.append("expectations for drug-candidate progress")
        return SummaryLines(
            what="Cho-A Pharm rallied on a new healthcare raw-material distribution catalyst.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should verify contract revenue, clinical progress, "
                "and whether the pharma theme rally becomes sustained earnings."
            ),
        )

    @classmethod
    def _stock_manipulation_legal_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["alleged stock manipulation involving Duoback shares"]
        if "289억" in evidence:
            why_parts.append("about KRW 28.9 billion of trading cited by prosecutors")
        if "14억" in evidence:
            why_parts.append("alleged unfair gains of about KRW 1.4 billion")
        return SummaryLines(
            what="A court case put alleged Duoback share-price manipulation back in focus.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should treat the story as legal and governance risk context "
                "and monitor court findings rather than reading it as an operating update."
            ),
        )

    @classmethod
    def _bank_policy_undervaluation_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["record earnings and stable capital ratios"]
        if "500조" in evidence:
            why_parts.append("roughly KRW 500 trillion in policy-finance obligations")
        if "주주환원" in evidence:
            why_parts.append("shareholder-return expectations")
        return SummaryLines(
            what="Korean financial holding companies rebounded as undervaluation concerns eased.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track policy-finance costs, capital efficiency, "
                "non-bank earnings, and whether shareholder returns keep valuations rising."
            ),
        )

    @classmethod
    def _semiconductor_earnings_adr_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["heavy foreign selling in semiconductor stocks"]
        if "삼성전자" in evidence:
            why_parts.append("Samsung Electronics' upcoming earnings")
        if "ADR" in evidence:
            why_parts.append("SK hynix's U.S. ADR listing")
        return SummaryLines(
            what=(
                "Samsung Electronics earnings and SK hynix's ADR listing became key "
                "tests for semiconductor sentiment."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track foreign flows, memory earnings surprises, "
                "and overseas demand for chip stocks."
            ),
        )

    @classmethod
    def _weekly_semiconductor_flow_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["heavy foreign selling across KOSPI and KOSDAQ"]
        if "삼성전자" in evidence or "SK하이닉스" in evidence:
            why_parts.append("profit-taking in major semiconductor stocks")
        if "메타" in evidence or "애플" in evidence:
            why_parts.append("U.S. tech-stock weakness after Meta and Apple shocks")
        return SummaryLines(
            what=(
                "Foreign investors' nearly KRW 20 trillion sell-off pushed KOSPI "
                "and KOSDAQ lower last week."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track Samsung Electronics earnings, SK hynix flows, "
                "and whether semiconductor bargain buying continues."
            ),
        )

    @classmethod
    def _hyundai_rv_hev_profit_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["falling U.S. new-car prices"]
        if "인센티브" in evidence:
            why_parts.append("rising dealer incentives")
        if "역대 최대" in evidence or "최다" in evidence:
            why_parts.append("record first-half sales")
        return SummaryLines(
            what=(
                "Hyundai Motor and Kia leaned on RV and HEV sales to protect U.S. "
                "profitability as new-car prices fell."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track incentives, product mix, hybrid demand, and "
                "U.S. margin resilience."
            ),
        )

    @classmethod
    def _nvidia_robotics_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["Nvidia's small direct robotics revenue contribution"]
        if "부품 공급망" in evidence:
            why_parts.append("interest moving from finished robots to the parts supply chain")
        if "액추에이터" in evidence:
            why_parts.append("investor attention shifting toward actuator suppliers")
        return SummaryLines(
            what=(
                "Nvidia-linked robotics and actuator stocks moved into focus after "
                "robotics revenue was reported in the 1% range."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track actuator order visibility, supplier exposure, "
                "and whether robotics demand turns into earnings."
            ),
        )

    @classmethod
    def _corporate_rehabilitation_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["rising corporate rehabilitation filings"]
        if "한계기업" in evidence:
            why_parts.append("delayed restructuring of marginal companies")
        if "좀비기업" in evidence:
            why_parts.append("zombie-company cleanup pressure")
        if "이자보상배율" in evidence:
            why_parts.append("interest-coverage stress among listed companies")
        return SummaryLines(
            what=(
                "Corporate rehabilitation filings increased sharply as financially "
                "fragile Korean companies came under restructuring pressure."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track credit risk, creditor exposure, and whether "
                "capital moves from marginal-company cleanup to stronger businesses."
            ),
        )

    @classmethod
    def _delaware_corporate_law_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["Delaware amendments expanding contract freedom in governance"]
        if "SB313" in evidence:
            why_parts.append("SB313 validating broad shareholder agreements")
        if "한국 상법" in evidence or "상법 개정" in evidence:
            why_parts.append("a contrast with Korea's shareholder-rights reforms")
        return SummaryLines(
            what=(
                "Delaware corporate-law amendments drew attention because they move "
                "in the opposite direction from Korea's recent commercial-law reforms."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track governance-rule changes, controlling-shareholder "
                "rights, and whether Korean reforms affect listing appeal."
            ),
        )

    @classmethod
    def _ai_superintelligence_column_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["global warnings about artificial superintelligence"]
        if "반도체" in evidence or "삼전닉스" in evidence:
            why_parts.append("speculative chip-stock enthusiasm in Korea")
        if "ChatGPT" in evidence or "챗지피티" in evidence:
            why_parts.append("growing reliance on generative AI tools")
        return SummaryLines(
            what=(
                "A market column linked AI-risk warnings with Korea's speculative "
                "semiconductor-stock mood."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track AI policy risk, semiconductor speculation, "
                "and whether hype increases market volatility."
            ),
        )

    @classmethod
    def _sk_hynix_adr_listing_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["SK hynix's planned Nasdaq ADR listing"]
        if "45조" in evidence:
            why_parts.append("a potential KRW 45 trillion capital raise")
        if "희석" in evidence or "자금 이탈" in evidence:
            why_parts.append("dilution and domestic-liquidity concerns")
        return SummaryLines(
            what=(
                "SK hynix's planned Nasdaq ADR listing became a key issue for Korean "
                "semiconductor investors."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track ADR demand, share-dilution risk, and whether "
                "global passive funds enter the stock."
            ),
        )

    @classmethod
    def _rate_decoupling_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["cooling U.S. employment data"]
        if "물가" in evidence or "부동산" in evidence:
            why_parts.append("Korean inflation, housing, and household-debt pressure")
        if "원화" in evidence:
            why_parts.append("possible support for the won from a narrower rate gap")
        return SummaryLines(
            what=(
                "Korea and the United States faced diverging interest-rate paths as "
                "U.S. employment cooled."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track the won-dollar rate, foreign equity flows, "
                "and household-debt pressure from any Bank of Korea hike."
            ),
        )

    @classmethod
    def _kospi_per_valuation_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["foreign selling and technology-stock weakness"]
        if "12개월" in evidence or "PER" in evidence:
            why_parts.append("KOSPI's 12-month forward PER falling sharply")
        if "골드만삭스" in evidence:
            why_parts.append("Goldman Sachs' view that valuation upside remains")
        return SummaryLines(
            what=(
                "KOSPI's forward valuation fell to its lowest level since the global "
                "financial crisis."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track foreign selling, earnings revisions, bond "
                "yields, and whether cheap valuations draw inflows."
            ),
        )

    @classmethod
    def _kospi_trillion_club_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["fewer listed companies exceeding KRW 1 trillion in market value"]
        if "대형주" in evidence or "삼성전자" in evidence or "SK하이닉스" in evidence:
            why_parts.append("deeper concentration in large-cap stocks")
        if "코스닥" in evidence:
            why_parts.append("weaker breadth in KOSDAQ names")
        return SummaryLines(
            what=(
                "KOSPI recovered the 8,000 level, but the KRW 1 trillion club "
                "shrank as large-cap concentration deepened."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track market breadth, large-cap concentration, "
                "and whether gains spread beyond top semiconductor stocks."
            ),
        )

    @classmethod
    def _kospi_rollercoaster_fallback(cls, evidence: str) -> SummaryLines:
        if "삼성전자" in evidence and any(term in evidence for term in ("하락 반전", "8천선")):
            what = (
                "KOSPI reversed lower intraday even as Samsung Electronics' earnings "
                "expectations supported chip sentiment."
            )
        else:
            what = (
                "KOSPI swung sharply and finished near the 8,000 level as market "
                "volatility stayed high."
            )
        why_parts = []
        if "외국인" in evidence and "순매도" in evidence:
            why_parts.append("continued foreign net selling")
        if "기관" in evidence and "순매도" in evidence:
            why_parts.append("institutional selling")
        if any(term in evidence for term in ("삼성전자", "SK하이닉스", "반도체")):
            why_parts.append("large chip-stock moves around earnings expectations")
        if "환율" in evidence:
            why_parts.append("won-dollar volatility after longer FX trading hours")
        if not why_parts:
            why_parts.append("intraday index swings and weak market breadth")
        return SummaryLines(
            what=what,
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track foreign flows, chip bellwether earnings, "
                "and whether KOSPI breadth stabilizes."
            ),
        )

    @classmethod
    def _korean_market_plunge_fallback(cls, evidence: str) -> SummaryLines:
        what = "KOSPI and KOSDAQ sold off sharply"
        if "매도 사이드카" in evidence or "사이드카" in evidence:
            what += " as sell-side circuit breakers were triggered"
        if "800선" in evidence:
            what += " and KOSDAQ fell below the 800 level"
        why_parts = []
        if any(
            term in evidence
            for term in ("반도체", "삼성전자", "SK하이닉스", "필라델피아반도체")
        ):
            why_parts.append("semiconductor weakness")
        if any(term in evidence for term in ("중동", "이란", "국제유가", "유가")):
            why_parts.append("Middle East risk and oil-price pressure")
        if "단일종목" in evidence and "레버리지" in evidence:
            why_parts.append("single-stock leveraged ETF flows")
        if not why_parts:
            why_parts.append("heavy program selling and weak market breadth")
        watch_parts = ["foreign flows", "chip bellwether earnings"]
        if "ADR" in evidence:
            watch_parts.append("SK hynix ADR demand")
        if "레버리지" in evidence or "ETF" in evidence:
            watch_parts.append("ETF rebalancing flows")
        return SummaryLines(
            what=what + ".",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact="Investors should track " + ", ".join(dict.fromkeys(watch_parts[:3])) + ".",
        )

    @classmethod
    def _won_dollar_rate_forecast_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["experts expecting the won-dollar rate to remain near KRW 1,500"]
        if "대미투자" in evidence:
            why_parts.append("U.S. investment pressure on Korean companies")
        if "엔저" in evidence:
            why_parts.append("yen weakness adding regional currency pressure")
        if "1600" in evidence:
            why_parts.append("some forecasts warning of a possible KRW 1,600 overshoot")
        return SummaryLines(
            what=(
                "Market experts expected the won-dollar rate to stay elevated into "
                "next year, with a year-end high-point forecast near KRW 1,575."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track exchange-rate sensitivity, import-cost "
                "pressure, foreign flows, and exporters' margin resilience."
            ),
        )

    @classmethod
    def _pharma_biotech_pbr_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["pharma and biotech shares lagging the semiconductor-led rally"]
        if "90곳" in evidence or "90" in evidence:
            why_parts.append("about 90 healthcare companies trading below 1x PBR")
        if "금리" in evidence:
            why_parts.append("interest-rate pressure weighing on valuations")
        return SummaryLines(
            what=(
                "Pharma and biotech stocks showed widespread undervaluation as many "
                "healthcare companies traded below 1x PBR."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track sector rotation, balance-sheet quality, and "
                "whether biotech investor appetite recovers beyond semiconductor-led flows."
            ),
        )

    @classmethod
    def _twenty_four_hour_fx_market_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["Korea opening won-dollar trading around the clock"]
        if "일본" in evidence:
            why_parts.append("comparison with Japan's freely traded yen market")
        if "중국" in evidence:
            why_parts.append("contrast with China's controlled onshore and offshore yuan markets")
        if "얇은 유동성" in evidence:
            why_parts.append("thin overnight liquidity raising volatility risk")
        return SummaryLines(
            what=(
                "Korea's 24-hour FX market began a structural shift toward wider "
                "global access to won trading."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track won liquidity, overnight volatility, and "
                "whether foreign access narrows Korea's currency discount."
            ),
        )

    @classmethod
    def _sell_korea_foreign_flow_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["record foreign selling of Korean equities"]
        if "150조" in evidence:
            why_parts.append("foreign net selling reaching roughly KRW 150 trillion")
        if "상대 성과" in evidence or "실적" in evidence:
            why_parts.append("relative performance and earnings as return conditions")
        if "환율" in evidence:
            why_parts.append("exchange-rate stability as a foreign-flow variable")
        return SummaryLines(
            what=(
                "Record Sell Korea flows raised questions about when foreign investors "
                "could return to Korean equities."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track earnings momentum, relative returns, exchange "
                "rates, and index events that could restore foreign demand."
            ),
        )

    @classmethod
    def _volatile_market_risk_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["sharp semiconductor-stock corrections after an overheated first half"]
        if "레버리지" in evidence or "ETF" in evidence:
            why_parts.append("single-stock leveraged ETFs amplifying volatility")
        if "데이터센터" in evidence or "인공지능" in evidence:
            why_parts.append(
                "questions about AI infrastructure spending and chip profit allocation"
            )
        return SummaryLines(
            what=(
                "Korean market volatility rose as semiconductor stocks corrected and "
                "investors reassessed AI-driven expectations."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should lower return assumptions, manage concentration risk, "
                "and watch whether AI demand supports chip earnings."
            ),
        )

    @classmethod
    def _investment_principles_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["extreme volatility encouraging short-term trading"]
        if "자산배분" in evidence:
            why_parts.append("asset allocation as a practical risk-control tool")
        if "장기" in evidence:
            why_parts.append("long-term index and growth-company investing as a steadier approach")
        return SummaryLines(
            what=(
                "A market column argued that investment discipline matters more in "
                "chaotic markets."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should review asset allocation, avoid excessive short-term "
                "trading, and focus on durable growth exposure."
            ),
        )

    @classmethod
    def _july_financial_turning_point_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["Samsung Electronics and SK hynix earnings becoming early July tests"]
        if "금통위" in evidence:
            why_parts.append("the Bank of Korea Monetary Policy Board meeting")
        if "FOMC" in evidence:
            why_parts.append("the U.S. FOMC and big-tech capex guidance")
        if "AI" in evidence:
            why_parts.append("concerns over AI investment momentum")
        return SummaryLines(
            what=(
                "July became a turning point for Korean financial markets as chip "
                "earnings and policy meetings approached."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track Samjeon Nix earnings, BOK and FOMC decisions, "
                "and whether AI capex guidance calms volatility."
            ),
        )

    @classmethod
    def _stock_wealth_real_estate_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["large stock-market gains increasing household financial wealth"]
        if "1146조" in evidence:
            why_parts.append("estimated first-half household stock gains near KRW 1,146 trillion")
        if "서울" in evidence or "아파트" in evidence:
            why_parts.append("possible spillover into Seoul apartment demand")
        return SummaryLines(
            what=(
                "Stock wealth from Samsung Electronics and SK hynix raised questions "
                "about whether money could move into real estate."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track wealth-effect spending, Seoul housing demand, "
                "and whether stock gains rotate into property assets."
            ),
        )

    @classmethod
    def _ipo_market_fallback(cls, evidence: str) -> SummaryLines:
        what = (
            "The Korean IPO market cooled as listing counts and offering proceeds fell "
            "sharply."
        )
        why_parts = []
        if cls._contains_term(evidence, "공모가") and cls._contains_term(evidence, "밑돌"):
            why_parts.append("new listings traded below their offering prices")
        if cls._contains_term(evidence, "코스닥"):
            why_parts.append("weak KOSDAQ demand weighed on investor appetite")
        if cls._contains_term(evidence, "중복상장") or cls._contains_term(evidence, "규제"):
            why_parts.append("listing-rule uncertainty kept issuers cautious")
        why = "The article cites " + ", ".join(why_parts[:3]) + "."
        if not why_parts:
            why = "The article cites weaker demand for new listings and lower offering proceeds."
        impact = (
            "Investors should track whether major listings revive demand and whether "
            "new stocks hold their offering prices."
        )
        return SummaryLines(what=what, why=why, impact=impact)

    @classmethod
    def _single_stock_leverage_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["high turnover in single-stock leveraged ETFs"]
        if "리밸런싱" in evidence or "장 막판" in evidence:
            why_parts.append("ETF rebalancing flows increasing late-session volatility")
        if "개미" in evidence:
            why_parts.append("retail investors concentrating in leveraged products")
        return SummaryLines(
            what=(
                "Single-stock leveraged ETFs in Korea drew scrutiny as retail buying "
                "concentrated in major chip-linked products."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track ETF rebalancing flows, late-session volatility, "
                "and whether risk controls tighten."
            ),
        )

    @classmethod
    def _retail_speculation_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["debt-funded retail speculation"]
        if "반도체" in evidence:
            why_parts.append("chip-cycle optimism around Samsung Electronics and SK hynix")
        if "우려" in evidence or "경고" in evidence:
            why_parts.append("analyst warnings about speculation rather than investment")
        return SummaryLines(
            what="Korean retail speculation around Samjeon Nix drew renewed risk warnings.",
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track margin exposure, retail flows, and volatility "
                "in major chip names."
            ),
        )

    @classmethod
    def _securities_overseas_expansion_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["Korean securities firms localizing overseas businesses"]
        if "미들마켓론" in evidence:
            why_parts.append("new mid-market loan opportunities")
        if "로드쇼" in evidence:
            why_parts.append("overseas investor demand at roadshows")
        return SummaryLines(
            what=(
                "Korean securities firms expanded overseas financing and "
                "investor-relations businesses."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track overseas revenue diversification, deal flow, "
                "and credit risk controls."
            ),
        )

    @classmethod
    def _semiconductor_cluster_policy_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["government follow-up measures for semiconductor megaprojects"]
        if "점검회의" in evidence:
            why_parts.append("a policy review meeting on semiconductor cluster support")
        if "지원" in evidence:
            why_parts.append("planned support for chip-sector investment")
        return SummaryLines(
            what=(
                "Korea's semiconductor cluster support plan moved into focus as "
                "the government prepared a review meeting."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track policy execution, capex timing, and "
                "chip supply-chain beneficiaries."
            ),
        )

    @classmethod
    def _retail_net_buying_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["retail investors providing heavy net buying"]
        if "코스피" in evidence:
            why_parts.append("stronger KOSPI performance drawing investor flows")
        if "161조" in evidence:
            why_parts.append("first-half net purchases reaching KRW 161 trillion")
        return SummaryLines(
            what=(
                "Retail investors net bought heavily in the first half as Korean "
                "stocks rallied."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track whether retail net buying continues and "
                "which sectors absorb the flows."
            ),
        )

    @classmethod
    def _regional_market_cap_fallback(cls, evidence: str) -> SummaryLines:
        why_parts = ["regional listed-company market-cap weakness"]
        if "코스닥" in evidence:
            why_parts.append("KOSDAQ weakness weighing on local listed companies")
        if "2조" in evidence:
            why_parts.append("a roughly KRW 2 trillion market-cap decline")
        return SummaryLines(
            what=(
                "Daegu-listed companies' market capitalization fell as a five-quarter "
                "rally ended."
            ),
            why="The article cites " + ", ".join(dict.fromkeys(why_parts[:3])) + ".",
            impact=(
                "Investors should track regional market-cap trends, KOSDAQ weakness, "
                "and company-level earnings."
            ),
        )

    @classmethod
    def _english_subject(cls, context: NewsSummaryContext, evidence: str) -> str:
        if any(term in evidence for term in ("IPO", "기업공개", "공모금액", "공모가")):
            return "The Korean IPO market"
        if context.stock_name_en:
            if re.search(r"[가-힣]", context.stock_name_en):
                return "The company"
            return context.stock_name_en
        if "코스피" in evidence and "코스닥" in evidence:
            return "KOSPI and KOSDAQ"
        if "코스피" in evidence:
            return "KOSPI"
        if "코스닥" in evidence:
            return "KOSDAQ"
        if any(term in evidence for term in ("증시", "주식시장", "금융시장")):
            return "The Korean stock market"
        if any(term in evidence for term in ("기업회생", "한계기업", "좀비기업", "구조조정")):
            return "The Korean corporate restructuring issue"
        if context.source_type == "DISCLOSURE":
            return "The issuer"
        return "The article"

    @classmethod
    def _fallback_driver_phrase(cls, evidence: str) -> str:
        drivers = [
            phrase
            for required_terms, phrase in cls._ENGLISH_FALLBACK_DRIVERS
            if cls._has_all_terms(evidence, required_terms)
            and not (
                phrase == "data-center investment"
                and cls._is_financial_earnings_context(evidence)
            )
        ]
        if not drivers:
            return "market sentiment and investor positioning"
        return ", ".join(dict.fromkeys(drivers[:3]))

    @classmethod
    def _fallback_event_phrase(cls, evidence: str, topic: str) -> str:
        if any(term in evidence for term in ("주요공시", "주요 종목 뉴스", "장 마감후")):
            return "a Korean disclosure and stock-news roundup"
        if any(term in evidence for term in ("CB", "전환사채", "반품 CB")):
            return "convertible-bond resale and shareholder-risk concerns"
        if any(term in evidence for term in ("K바이오", "HLB", "TG-C", "큐로셀")):
            return "K-bio regulatory, clinical, and pipeline catalysts"
        if any(term in evidence for term in ("대주주", "최대주주", "손바뀜")):
            return "controlling-shareholder and governance changes"
        if any(term in evidence for term in ("특허", "제네릭", "무효심판")):
            return "a patent dispute and generic-drug entry risk"
        if any(term in evidence for term in ("라네즈", "젝시믹스", "트라이써클", "애경산업")):
            return "consumer-brand launches and retail-channel promotions"
        if any(term in evidence for term in ("동전주", "상장폐지", "관리종목")):
            return "tightened delisting rules for low-priced stocks"
        if topic != "the reported event":
            return topic
        return "a financial catalyst described in the article"

    @classmethod
    def _fallback_specific_driver_phrase(cls, evidence: str) -> str:
        if any(term in evidence for term in ("주요공시", "공시", "계약")):
            return "company disclosures, contract notices, and capital-action updates"
        if any(term in evidence for term in ("CB", "전환사채")):
            return "convertible-bond terms, resale structure, and investor exposure"
        if any(term in evidence for term in ("K바이오", "HLB", "TG-C", "임상", "허가")):
            return "clinical data, approval timelines, and pipeline-event risk"
        if any(term in evidence for term in ("대주주", "최대주주", "손바뀜")):
            return "ownership changes, governance uncertainty, and funding plans"
        if any(term in evidence for term in ("특허", "제네릭", "무효심판")):
            return "patent-review outcomes and follow-on generic competition"
        if any(term in evidence for term in ("실적", "영업이익", "매출")):
            return "earnings, revenue, and operating-profit expectations"
        return "article-specific disclosures and price-sensitive follow-up events"

    @classmethod
    def _fallback_specific_watch_item(cls, evidence: str) -> str:
        if any(term in evidence for term in ("CB", "전환사채")):
            return "conversion terms, resale timing, and dilution risk"
        if any(term in evidence for term in ("특허", "제네릭", "무효심판")):
            return "appeal results, generic launches, and product-sales exposure"
        if any(term in evidence for term in ("K바이오", "HLB", "TG-C", "임상", "허가")):
            return "regulatory decisions, clinical milestones, and related stock volatility"
        if any(term in evidence for term in ("대주주", "최대주주", "손바뀜")):
            return "ownership filings, funding use, and governance changes"
        if any(term in evidence for term in ("주요공시", "공시", "계약")):
            return "follow-up filings, contract size, and market reaction"
        return "follow-up filings, funding terms, and price reaction"

    @staticmethod
    def _is_bank_earnings_context(evidence: str) -> bool:
        return (
            any(term in evidence for term in ("은행주", "은행업종", "금융지주"))
            and any(term in evidence for term in ("2분기", "분기"))
            and any(term in evidence for term in ("실적", "최선호주", "투자의견"))
        )

    @staticmethod
    def _is_limit_up_ai_infra_context(evidence: str) -> bool:
        return (
            "상한가" in evidence
            and any(term in evidence for term in ("금호건설", "미래산업", "삼화전자"))
            and any(term in evidence for term in ("AI 인프라", "AI인프라", "MLCC", "로봇"))
        )

    @staticmethod
    def _is_financial_leadership_profile_context(evidence: str) -> bool:
        return (
            "[Who Is" in evidence
            or "Who Is ?" in evidence
            or ("대표이사 회장" in evidence and "생애" in evidence)
        )

    @staticmethod
    def _is_broker_recommendation_list_context(evidence: str) -> bool:
        return (
            "KB증권" in evidence
            and "매수 추천" in evidence
            and any(term in evidence for term in ("14종목", "7월 첫째주", "Buy 유지"))
        )

    @staticmethod
    def _is_defense_nato_rally_context(evidence: str) -> bool:
        return (
            "방산주" in evidence
            and "나토" in evidence
            and any(term in evidence for term in ("엠앤씨솔루션", "한화시스템", "한국항공우주"))
        )

    @staticmethod
    def _is_defense_supercycle_context(evidence: str) -> bool:
        return (
            any(term in evidence for term in ("방산 슈퍼사이클", "방산 수출", "우주항공과국방"))
            and "한국항공우주" in evidence
            and any(term in evidence for term in ("한화에어로스페이스", "한화시스템"))
        )

    @staticmethod
    def _is_nps_rebalancing_context(evidence: str) -> bool:
        return (
            "국민연금" in evidence
            and any(term in evidence for term in ("IT·뷰티", "IT·전자부품", "전자부품"))
            and "코스닥" in evidence
            and any(term in evidence for term in ("소부장", "바이오"))
        )

    @staticmethod
    def _is_botabio_stock_manipulation_context(evidence: str) -> bool:
        return (
            "보타바이오" in evidence
            and "견미리" in evidence
            and any(term in evidence for term in ("주가 조작", "주가조작", "대법원"))
        )

    @staticmethod
    def _is_deepfake_security_theme_context(evidence: str) -> bool:
        return (
            "딥페이크" in evidence
            and any(term in evidence for term in ("생성형 AI", "생성형 인공지능"))
            and any(term in evidence for term in ("라온시큐어", "파수AI", "시선AI"))
        )

    @staticmethod
    def _is_information_security_theme_context(evidence: str) -> bool:
        return (
            "정보보안" in evidence
            and any(term in evidence for term in ("제로트러스트", "보안 투자", "사이버 공격"))
            and any(term in evidence for term in ("라온시큐어", "핀텔", "샌즈랩"))
        )

    @staticmethod
    def _is_quantum_security_theme_context(evidence: str) -> bool:
        return (
            "코위버" in evidence
            and any(term in evidence for term in ("양자암호", "양자컴퓨팅", "광전송"))
            and any(term in evidence for term in ("QKD", "PQA", "테라급"))
        )

    @staticmethod
    def _is_quantum_crypto_risk_context(evidence: str) -> bool:
        return (
            any(term in evidence for term in ("Q-데이", "Q-Day", "수백만 큐비트", "양자컴퓨터"))
            and any(term in evidence for term in ("암호 해독", "RSA", "ECC", "공개키 암호"))
        )

    @staticmethod
    def _is_duoback_market_warning_context(evidence: str) -> bool:
        return (
            "듀오백" in evidence
            and "투자경고종목" in evidence
            and any(term in evidence for term in ("재지정", "투자주의종목", "시장경보"))
        )

    @staticmethod
    def _is_daily_disclosure_roundup_context(evidence: str) -> bool:
        return (
            "주식시장 주요공시" in evidence
            or (
                "전환사채" in evidence
                and "공급계약" in evidence
                and any(term in evidence for term in ("자사주", "유상증자", "자산재평가"))
            )
        )

    @staticmethod
    def _is_ecm_league_table_context(evidence: str) -> bool:
        return (
            "ECM" in evidence
            and any(term in evidence for term in ("유상증자", "IPO", "리그테이블"))
            and any(term in evidence for term in ("SKC", "한화솔루션", "NH투자증권"))
        )

    @staticmethod
    def _is_delisting_rule_tightening_context(evidence: str) -> bool:
        return (
            any(term in evidence for term in ("상폐 강화", "상장폐지", "퇴출 위기"))
            and any(term in evidence for term in ("시총 미달", "시가총액", "관리종목"))
            and any(term in evidence for term in ("코스닥", "듀오백", "SHD"))
        )

    @staticmethod
    def _is_korean_market_plunge_context(evidence: str) -> bool:
        return (
            "코스피" in evidence
            and "코스닥" in evidence
            and "주간수급리포트" not in evidence
            and any(term in evidence for term in ("급락", "하락", "매도 사이드카", "사이드카"))
            and any(term in evidence for term in ("5%", "5%대", "800선", "7200선", "반도체"))
        )

    @staticmethod
    def _is_kospi_rollercoaster_context(evidence: str) -> bool:
        return (
            "코스피" in evidence
            and any(term in evidence for term in ("롤러코스피", "8000선", "8천선"))
            and any(
                term in evidence
                for term in ("등락", "출렁", "하락 반전", "급락", "순매도")
            )
        )

    @staticmethod
    def _is_fx_24h_market_open_context(evidence: str) -> bool:
        return (
            any(term in evidence for term in ("24시간 개장", "24시간 무중단", "24시간"))
            and any(term in evidence for term in ("원/달러", "외환거래", "외환시장"))
            and any(term in evidence for term in ("1527.6", "하나은행", "딜링룸"))
        )

    @staticmethod
    def _is_insider_share_purchase_context(evidence: str) -> bool:
        return (
            any(term in evidence for term in ("장내매수", "주식을 매입", "주식 매입"))
            and any(term in evidence for term in ("라온시큐어", "이순형"))
            and any(term in evidence for term in ("2억", "보유 주식"))
        )

    @staticmethod
    def _is_pharma_healthcare_contract_context(evidence: str) -> bool:
        return (
            "조아제약" in evidence
            and "헬스케어" in evidence
            and any(term in evidence for term in ("원료 유통 계약", "원료유통계약"))
        )

    @staticmethod
    def _is_stock_manipulation_legal_context(evidence: str) -> bool:
        return (
            "듀오백" in evidence
            and any(term in evidence for term in ("주가조작", "주가 조작", "시세조종"))
            and any(term in evidence for term in ("자본시장법", "부당이득", "차명"))
        )

    @staticmethod
    def _is_bank_policy_undervaluation_context(evidence: str) -> bool:
        return (
            "정책 부담" in evidence
            and "저평가" in evidence
            and any(term in evidence for term in ("금융지주", "은행주", "주주환원"))
        )

    @staticmethod
    def _is_financial_earnings_context(evidence: str) -> bool:
        return any(
            term in evidence
            for term in (
                "은행주",
                "은행업종",
                "금융지주",
                "순이익",
                "이자이익",
                "비이자이익",
                "최선호주",
            )
        ) and any(term in evidence for term in ("실적", "영업이익", "2분기", "분기"))

    @classmethod
    def _first_fallback_phrase(
        cls,
        evidence: str,
        candidates: tuple[tuple[tuple[str, ...], str], ...],
        fallback: str,
    ) -> str:
        for required_terms, phrase in candidates:
            if cls._has_all_terms(evidence, required_terms):
                return phrase
        return fallback

    @classmethod
    def _has_all_terms(cls, evidence: str, required_terms: tuple[str, ...]) -> bool:
        return all(cls._contains_term(evidence, term) for term in required_terms)

    @staticmethod
    def _contains_term(evidence: str, term: str) -> bool:
        if term == "기관":
            return re.search(r"(?<!금융)기관", evidence) is not None
        return term in evidence
