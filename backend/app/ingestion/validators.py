from typing import Dict, Any, List, Tuple

class DataIngestionValidator:
    """Validates raw row dictionaries before mapping to relational entities."""

    @staticmethod
    def validate_positive_number(val: Any, default: float = 0.0) -> float:
        try:
            num = float(val)
            return max(0.0, num)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def validate_positive_int(val: Any, default: int = 1) -> int:
        try:
            num = int(float(val))
            return max(1, num)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def validate_score_bounds(val: Any, min_val: float = 0.0, max_val: float = 100.0, default: float = 85.0) -> float:
        try:
            num = float(val)
            return max(min_val, min(max_val, num))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def validate_string(val: Any, default: str = "") -> str:
        if val is None or (isinstance(val, float) and str(val) == "nan"):
            return default
        return str(val).strip()
