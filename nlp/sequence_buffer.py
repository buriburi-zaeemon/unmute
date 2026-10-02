"""
Sequence Buffer Module for UNMUTE.
Buffers incoming sign tokens, applies confidence filtering, suppresses duplicate token chatter,
and exposes process_sign_sequence() for downstream NLP sentence formation.
"""

from typing import List, Dict, Any, Union, Optional
import time
from nlp.token_schema import Token
from nlp.token_normalizer import TokenNormalizer


class SequenceBuffer:
    """
    Manages a sliding window of normalized sign tokens with confidence thresholding,
    duplicate suppression, and language mode isolation.
    """

    def __init__(
        self,
        language: str = "ASL",
        confidence_threshold: float = 0.60,
        deduplication_window: float = 1.0,
        max_buffer_size: int = 50,
        strict_lexicon_check: bool = True,
    ):
        self.language = language.upper()
        self.confidence_threshold = max(0.0, min(1.0, float(confidence_threshold)))
        self.deduplication_window = max(0.0, float(deduplication_window))
        self.max_buffer_size = max(1, int(max_buffer_size))
        self.strict_lexicon_check = strict_lexicon_check

        self.normalizer = TokenNormalizer()
        self._buffer: List[Token] = []
        self._last_added_token: Optional[Token] = None
        self._last_added_timestamp: float = 0.0

    def set_language(self, language: str) -> None:
        """Switch active language mode ('ASL' or 'ISL'). Clears buffer on switch."""
        new_lang = str(language).strip().upper()
        if new_lang != self.language:
            self.language = new_lang
            self.clear()

    def add_token(self, token_input: Union[Token, Dict[str, Any], str]) -> bool:
        """
        Add a new token to the sequence buffer.
        Returns True if accepted and appended, False if rejected (low confidence, duplicate chatter, or invalid).
        """
        # Convert input to Token
        if isinstance(token_input, Token):
            raw_token = token_input
        elif isinstance(token_input, dict):
            raw_token = Token.from_dict(token_input)
        elif isinstance(token_input, str):
            raw_token = Token(text=token_input, confidence=1.0, language=self.language)
        else:
            return False

        # Ensure language matches buffer mode or update token
        if raw_token.language != self.language:
            raw_token.language = self.language

        # Normalize token
        norm_token = self.normalizer.normalize_token(raw_token)

        # 1. Confidence threshold check
        if norm_token.confidence < self.confidence_threshold:
            return False

        # 2. Strict lexicon validation check
        if self.strict_lexicon_check and not self.normalizer.is_valid_token(norm_token):
            return False

        # 3. Duplicate chatter suppression within window
        current_time = norm_token.timestamp or time.time()
        if (
            self._last_added_token is not None
            and self._last_added_token.text == norm_token.text
            and (current_time - self._last_added_timestamp) < self.deduplication_window
        ):
            return False

        # Append to buffer
        self._buffer.append(norm_token)
        self._last_added_token = norm_token
        self._last_added_timestamp = current_time

        # Trim buffer if exceeding max_buffer_size
        if len(self._buffer) > self.max_buffer_size:
            self._buffer.pop(0)

        return True

    def get_tokens(self) -> List[Token]:
        """Return a copy of current buffer tokens."""
        return list(self._buffer)

    def get_token_texts(self) -> List[str]:
        """Return list of normalized token text strings."""
        return [t.text for t in self._buffer]

    def clear(self) -> None:
        """Reset sequence buffer state."""
        self._buffer.clear()
        self._last_added_token = None
        self._last_added_timestamp = 0.0

    def __len__(self) -> int:
        return len(self._buffer)


def process_sign_sequence(
    sequence: List[Union[Token, Dict[str, Any], str]],
    language: str = "ASL",
    confidence_threshold: float = 0.60,
    deduplication_window: float = 1.0,
) -> List[Token]:
    """
    Decoupled helper function to process a list of raw sign tokens or strings into a clean,
    normalized, deduplicated Token sequence.
    """
    buf = SequenceBuffer(
        language=language,
        confidence_threshold=confidence_threshold,
        deduplication_window=deduplication_window,
        strict_lexicon_check=False,
    )

    for item in sequence:
        buf.add_token(item)

    return buf.get_tokens()
