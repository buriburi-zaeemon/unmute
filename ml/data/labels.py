"""
UNMUTE - Authoritative Label Mappings & Token Contract
Supports both American Sign Language (ASL) and Indian Sign Language (ISL).
Provides bidirectional class lookups, structured token metadata, and category mappings.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union


class SignLanguage(str, Enum):
    ASL = "ASL"
    ISL = "ISL"


# ==============================================================================
# 1. AMERICAN SIGN LANGUAGE (ASL) CONTROLLED STATIC VOCABULARY
# ==============================================================================
ASL_ALPHABETS = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y"
]  # 24 classes (J and Z are dynamic)

ASL_NUMERALS = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
]  # 10 classes

ASL_PHRASES = [
    "I LOVE YOU",
    "OKAY",
    "PEACE",
    "STOP",
    "THUMBS DOWN",
    "THUMBS UP",
]  # 6 classes

ASL_CONTROLS = ["SPACE"]  # 1 class

# Canonical ASL Classes (Ordered alphabetically / numerically: 41 classes)
ASL_CLASSES: List[str] = sorted(ASL_ALPHABETS + ASL_NUMERALS + ASL_PHRASES + ASL_CONTROLS)

# Dynamic ASL Signs (Reserved for Contributor 2 sequence tracking)
ASL_DYNAMIC_SIGNS: List[str] = [
    "HELLO",
    "THANK YOU",
    "YES",
    "NO",
    "PLEASE",
    "J",
    "Z"
]


# ==============================================================================
# 2. INDIAN SIGN LANGUAGE (ISL) CONTROLLED STATIC VOCABULARY (ISLRTC-ALIGNED)
# ==============================================================================
ISL_ALPHABETS = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
]  # 26 classes (ISLRTC standard bimanual & unimanual static letters)

ISL_NUMERALS = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
]  # 10 classes

ISL_PHRASES = [
    "NAMASTE",
    "I LOVE YOU",
    "PEACE",
    "OKAY",
    "THUMBS UP",
    "THUMBS DOWN",
    "STOP",
]  # 7 classes

ISL_CONTROLS = ["SPACE"]  # 1 class

# Canonical ISL Classes (Ordered alphabetically / numerically: 44 classes)
ISL_CLASSES: List[str] = sorted(ISL_ALPHABETS + ISL_NUMERALS + ISL_PHRASES + ISL_CONTROLS)

# Dynamic ISL Signs (Reserved for Contributor 2 sequence tracking)
ISL_DYNAMIC_SIGNS: List[str] = [
    "HELLO",
    "THANK YOU",
    "YES",
    "NO",
    "PLEASE",
    "HELP",
    "WATER"
]


# ==============================================================================
# 3. BIDIRECTIONAL LOOKUPS & FACTORIES
# ==============================================================================
def _normalize_lang(language: Union[SignLanguage, str]) -> SignLanguage:
    if isinstance(language, str):
        return SignLanguage(language.upper())
    return language


def get_classes(language: Union[SignLanguage, str] = SignLanguage.ASL) -> List[str]:
    """Returns canonical class list for the specified sign language."""
    lang = _normalize_lang(language)
    return list(ASL_CLASSES if lang == SignLanguage.ASL else ISL_CLASSES)


def get_num_classes(language: Union[SignLanguage, str] = SignLanguage.ASL) -> int:
    """Returns the total number of classes for the specified sign language."""
    return len(get_classes(language))


def label_to_id(label: str, language: Union[SignLanguage, str] = SignLanguage.ASL) -> int:
    """Converts a string sign label into its continuous zero-indexed integer ID."""
    classes = get_classes(language)
    clean_label = str(label).strip().upper()
    try:
        return classes.index(clean_label)
    except ValueError:
        raise KeyError(
            f"Label '{label}' not recognized in {language} static vocabulary. "
            f"Supported classes: {classes}"
        )


def id_to_label(class_id: int, language: Union[SignLanguage, str] = SignLanguage.ASL) -> str:
    """Converts a zero-indexed integer ID into its canonical string sign label."""
    classes = get_classes(language)
    if 0 <= class_id < len(classes):
        return classes[class_id]
    raise IndexError(
        f"Class ID {class_id} is out of bounds for {language} (0..{len(classes)-1})."
    )


class SignType(str, Enum):
    LETTER = "letter"
    NUMBER = "number"
    STATIC_PHRASE = "static_phrase"
    DYNAMIC = "dynamic"
    CONTROL = "control"
    UNKNOWN = "unknown"


def get_sign_type(label: str, language: Union[SignLanguage, str] = SignLanguage.ASL) -> SignType:
    """Returns the strongly-typed SignType enum for a given label."""
    clean = str(label).strip().upper()
    lang = _normalize_lang(language)

    if lang == SignLanguage.ASL:
        if clean in ASL_ALPHABETS:
            return SignType.LETTER
        if clean in ASL_NUMERALS:
            return SignType.NUMBER
        if clean in ASL_PHRASES:
            return SignType.STATIC_PHRASE
        if clean in ASL_CONTROLS:
            return SignType.CONTROL
        if clean in ASL_DYNAMIC_SIGNS:
            return SignType.DYNAMIC
    else:
        if clean in ISL_ALPHABETS:
            return SignType.LETTER
        if clean in ISL_NUMERALS:
            return SignType.NUMBER
        if clean in ISL_PHRASES:
            return SignType.STATIC_PHRASE
        if clean in ISL_CONTROLS:
            return SignType.CONTROL
        if clean in ISL_DYNAMIC_SIGNS:
            return SignType.DYNAMIC

    return SignType.UNKNOWN


def get_sign_category(label: str, language: Union[SignLanguage, str] = SignLanguage.ASL) -> str:
    """Identifies the syntactic/lexical category of a sign label."""
    st = get_sign_type(label, language)
    mapping = {
        SignType.LETTER: "Alphabet",
        SignType.NUMBER: "Numeral",
        SignType.STATIC_PHRASE: "Phrase",
        SignType.DYNAMIC: "Dynamic",
        SignType.CONTROL: "Control",
        SignType.UNKNOWN: "Unknown",
    }
    return mapping.get(st, "Unknown")


def is_dynamic_token(label: str, language: Union[SignLanguage, str] = SignLanguage.ASL) -> bool:
    """Returns True if the label is a sequence-based dynamic sign (handled by Contributor 2)."""
    return get_sign_type(label, language) == SignType.DYNAMIC


def is_bimanual_sign(label: str, language: Union[SignLanguage, str] = SignLanguage.ASL) -> bool:
    """Returns True if the sign requires both hands (typical for ISL alphabets and NAMASTE)."""
    clean = str(label).strip().upper()
    lang = _normalize_lang(language)
    if lang == SignLanguage.ASL:
        return False  # ASL static vocabulary is unimanual
    # In ISL, all alphabets except unimanual 'C' and 'L' are bimanual, plus NAMASTE
    if clean in ("C", "L"):
        return False
    if clean in ISL_NUMERALS:
        return False
    return True

