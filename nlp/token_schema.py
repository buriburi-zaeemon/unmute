"""
Token Schema Module for UNMUTE.
Defines the standard, dual-language structured Token contract between sign recognition layers and sentence processing.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Set
import time

VALID_LANGUAGES: Set[str] = {"ASL", "ISL"}
VALID_SIGN_TYPES: Set[str] = {"letter", "number", "phrase", "dynamic", "control"}


@dataclass
class Token:
    """
    Standardized sign token representation passed from ML predictors into the sequence buffer and NLP pipeline.
    """
    text: str
    confidence: float
    language: str = "ASL"
    sign_type: str = "letter"
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        # Clean and normalize string fields
        self.text = str(self.text).strip().upper()
        self.language = str(self.language).strip().upper()
        self.sign_type = str(self.sign_type).strip().lower()

        # Validate language
        if self.language not in VALID_LANGUAGES:
            raise ValueError(f"Invalid language '{self.language}'. Must be one of {VALID_LANGUAGES}")

        # Validate sign_type
        if self.sign_type not in VALID_SIGN_TYPES:
            raise ValueError(f"Invalid sign_type '{self.sign_type}'. Must be one of {VALID_SIGN_TYPES}")

        # Clamp confidence to [0.0, 1.0]
        self.confidence = max(0.0, min(1.0, float(self.confidence)))

    def to_dict(self) -> Dict[str, Any]:
        """Convert token instance to serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Token":
        """Construct Token instance from a dictionary."""
        return cls(
            text=data.get("text", ""),
            confidence=float(data.get("confidence", 1.0)),
            language=data.get("language", "ASL"),
            sign_type=data.get("sign_type", "letter"),
            timestamp=float(data.get("timestamp", time.time())),
        )
