from pathlib import Path
from typing import Any

import joblib
from sklearn.metrics.pairwise import cosine_similarity

from hannah_montana_ai.training.stock_universe import normalize_stock_term


class StockLinkerModelArtifactError(RuntimeError):
    pass


class StockLinkerModelArtifactNotFoundError(StockLinkerModelArtifactError):
    pass


class StockLinkerModelArtifactInvalidError(StockLinkerModelArtifactError):
    pass


class MachineLearningStockLinker:
    def __init__(self, model_path: Path) -> None:
        if not model_path.exists():
            raise StockLinkerModelArtifactNotFoundError(
                f"Stock linker model artifact not found: {model_path}"
            )
        try:
            payload: dict[str, Any] = joblib.load(model_path)
        except Exception as exception:
            message = f"Stock linker model artifact cannot be loaded: {model_path}"
            raise StockLinkerModelArtifactInvalidError(message) from exception

        self._validate_payload(payload, model_path)
        self.version = str(payload["version"])
        self.vectorizer = payload["vectorizer"]
        self.term_matrix = payload["term_matrix"]
        self.rows = tuple(payload["rows"])
        self.similarity_threshold = float(payload["similarity_threshold"])

    def predict_stock_code(self, text: str) -> str | None:
        prediction = self.predict_stock_code_with_score(text)
        if prediction is None:
            return None
        return prediction[0]

    def predict_stock_code_with_score(self, text: str) -> tuple[str, float] | None:
        normalized_text = normalize_stock_term(text)
        if not normalized_text:
            return None
        query_vector = self.vectorizer.transform([normalized_text])
        similarities = cosine_similarity(query_vector, self.term_matrix)[0]
        best_index = int(similarities.argmax())
        best_score = float(similarities[best_index])
        if best_score < self.similarity_threshold:
            return None
        return str(self.rows[best_index]["stock_code"]), best_score

    def _validate_payload(self, payload: dict[str, Any], model_path: Path) -> None:
        required_keys = {
            "version",
            "vectorizer",
            "term_matrix",
            "rows",
            "similarity_threshold",
        }
        missing_keys = sorted(required_keys - set(payload))
        if missing_keys:
            joined_keys = ", ".join(missing_keys)
            message = (
                "Stock linker model artifact is missing required keys: "
                f"{joined_keys} ({model_path})"
            )
            raise StockLinkerModelArtifactInvalidError(message)
