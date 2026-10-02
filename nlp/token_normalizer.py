"""
Token Normalization & Lexicon Mapping Module for UNMUTE.
Handles case normalization, synonym resolution, handshape alias mapping, and dual-language (ASL/ISL) lexicon validation.
"""

from typing import Dict, Optional, Set
from nlp.token_schema import Token

# Synonym and greeting mappings
SYNONYM_MAP: Dict[str, str] = {
    # Greetings & Phrases
    "HI": "HELLO",
    "HEY": "HELLO",
    "NAMASKAR": "NAMASTE",
    "NAMASTHE": "NAMASTE",
    "THANKS": "THANK YOU",
    "TY": "THANK YOU",
    "PLY": "PLEASE",
    "PLS": "PLEASE",
    "BYE": "GOODBYE",
    "ILY": "I LOVE YOU",
    "LOVE YOU": "I LOVE YOU",
    "THUMB UP": "THUMBS UP",
    "THUMB DOWN": "THUMBS DOWN",
    "LIKE": "THUMBS UP",
    "DISLIKE": "THUMBS DOWN",
}

# Handshape number/letter/alias mappings
ALIAS_MAP: Dict[str, str] = {
    "PEACE": "V",
    "OKAY": "F",
    "STOP": "5",
}

# ASL Lexicon (Static letters, numbers, key phrases)
ASL_LEXICON: Set[str] = {
    # Letters (A-Z)
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    # Numbers (0-9)
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    # Common Static Phrases & Words
    "HELLO", "THANK YOU", "PLEASE", "SORRY", "YES", "NO", "GOODBYE",
    "I LOVE YOU", "PEACE", "OKAY", "STOP", "HELP", "HOME", "GO",
    "YESTERDAY", "TODAY", "TOMORROW", "NAME", "ME", "YOU", "WE", "THEY",
}

# ISL Lexicon (Bimanual static phrases, full alphabet, numbers, cultural greetings)
ISL_LEXICON: Set[str] = {
    # Letters (A-Z, full bimanual & 1-hand representations)
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    # Numbers (0-9)
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    # Culturally Distinct ISL Phrases & Static Gestures
    "NAMASTE", "HELLO", "THANK YOU", "PLEASE", "SORRY", "YES", "NO",
    "GOODBYE", "I LOVE YOU", "PEACE", "OKAY", "STOP", "THUMBS UP",
    "THUMBS DOWN", "HELP", "HOME", "GO", "NAME", "ME", "YOU", "WE",
}


class TokenNormalizer:
    """
    Normalizes token text, maps synonyms, resolves handshape aliases,
    and validates tokens against active ASL/ISL lexicons.
    """

    def __init__(self, synonym_map: Optional[Dict[str, str]] = None, alias_map: Optional[Dict[str, str]] = None):
        self.synonym_map = synonym_map if synonym_map is not None else SYNONYM_MAP.copy()
        self.alias_map = alias_map if alias_map is not None else ALIAS_MAP.copy()

    def normalize_text(self, text: str) -> str:
        """
        Normalize raw text string: uppercase, strip whitespace, map synonyms and aliases.
        """
        if not text:
            return ""

        clean = str(text).strip().upper()

        # Check synonym map first
        if clean in self.synonym_map:
            clean = self.synonym_map[clean]

        return clean

    def normalize_token(self, token: Token) -> Token:
        """
        Produce a new normalized Token instance.
        """
        normalized_text = self.normalize_text(token.text)
        
        # Determine sign_type if phrase
        sign_type = token.sign_type
        if len(normalized_text) > 1 and normalized_text not in ("PEACE", "OKAY", "STOP"):
            sign_type = "phrase"

        return Token(
            text=normalized_text,
            confidence=token.confidence,
            language=token.language,
            sign_type=sign_type,
            timestamp=token.timestamp,
        )

    def is_valid_token(self, token: Token) -> bool:
        """
        Check if a token's normalized text belongs to the supported lexicon for its language mode.
        """
        normalized = self.normalize_text(token.text)
        if not normalized:
            return False

        if token.language == "ISL":
            return normalized in ISL_LEXICON
        return normalized in ASL_LEXICON
