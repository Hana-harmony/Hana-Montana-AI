from __future__ import annotations

import re

_CHOSEONG = (
    "g",
    "kk",
    "n",
    "d",
    "tt",
    "r",
    "m",
    "b",
    "pp",
    "s",
    "ss",
    "",
    "j",
    "jj",
    "ch",
    "k",
    "t",
    "p",
    "h",
)
_JUNGSEONG = (
    "a",
    "ae",
    "ya",
    "yae",
    "eo",
    "e",
    "yeo",
    "ye",
    "o",
    "wa",
    "wae",
    "oe",
    "yo",
    "u",
    "wo",
    "we",
    "wi",
    "yu",
    "eu",
    "ui",
    "i",
)
_JONGSEONG = (
    "",
    "k",
    "k",
    "ks",
    "n",
    "nj",
    "nh",
    "t",
    "l",
    "lk",
    "lm",
    "lb",
    "ls",
    "lt",
    "lp",
    "lh",
    "m",
    "p",
    "ps",
    "t",
    "t",
    "ng",
    "t",
    "t",
    "k",
    "t",
    "p",
    "h",
)
_COMPANY_TERMS = {
    "삼성": "Samsung",
    "현대": "Hyundai",
    "기아": "Kia",
    "하나": "Hana",
    "신한": "Shinhan",
    "우리": "Woori",
    "카카오": "Kakao",
    "네이버": "NAVER",
    "셀트리온": "Celltrion",
    "두산": "Doosan",
    "엘지": "LG",
}
_COMPANY_SUFFIXES = {
    "네트웍스": "Networks",
    "모터스": "Motors",
    "바이오": "Bio",
    "홀딩스": "Holdings",
    "지주": "Holdings",
    "제약": "Pharmaceutical",
    "화재": "Fire & Marine Insurance",
    "생명": "Life Insurance",
    "증권": "Securities",
    "건설": "Engineering & Construction",
    "전선": "Cable",
    "전자": "Electronics",
    "전기": "Electric",
    "금융": "Financial",
    "에너지": "Energy",
    "텔레콤": "Telecom",
    "화학": "Chemical",
    "은행": "Bank",
    "게임즈": "Games",
    "페이": "Pay",
}
_PREFERRED_SUFFIX = re.compile(r"(.+?)(\d?우B?|우)$")


def resolve_english_company_name(*, stock_code: str, stock_name: str, stock_name_en: str) -> str:
    """검증된 영문명을 우선하고 없을 때만 표시용 영문명을 생성한다."""
    verified = stock_name_en.strip()
    if verified and not contains_hangul(verified):
        return verified
    local_name = stock_name.strip()
    if local_name and not contains_hangul(local_name):
        return local_name
    generated = _transliterate_company_name(local_name)
    return generated or f"KRX {stock_code}"


def contains_hangul(value: str) -> bool:
    return bool(re.search(r"[가-힣]", value))


def _transliterate_company_name(value: str) -> str:
    preferred = ""
    match = _PREFERRED_SUFFIX.fullmatch(value)
    if match:
        value = match.group(1)
        order = match.group(2).replace("우", "").replace("B", "")
        preferred = " Preferred" + (f" {order}" if order else "")
    parts = re.findall(r"[가-힣]+|[A-Za-z0-9]+", value)
    return (" ".join(_transliterate_token(part) for part in parts) + preferred).strip()


def _transliterate_token(token: str) -> str:
    if token in _COMPANY_TERMS:
        return _COMPANY_TERMS[token]
    for suffix, english_suffix in _COMPANY_SUFFIXES.items():
        if token.endswith(suffix):
            prefix = token[: -len(suffix)]
            english_prefix = _COMPANY_TERMS.get(prefix) or _title_case(_romanize(prefix))
            return f"{english_prefix} {english_suffix}".strip()
    return _title_case(_romanize(token)) if contains_hangul(token) else token


def _romanize(value: str) -> str:
    result: list[str] = []
    for char in value:
        code_point = ord(char)
        if not 0xAC00 <= code_point <= 0xD7A3:
            result.append(char)
            continue
        syllable = code_point - 0xAC00
        jong = syllable % 28
        jung = (syllable // 28) % 21
        cho = syllable // (28 * 21)
        result.append(_CHOSEONG[cho] + _JUNGSEONG[jung] + _JONGSEONG[jong])
    return "".join(result)


def _title_case(value: str) -> str:
    return " ".join(part[:1].upper() + part[1:].lower() for part in value.split())
