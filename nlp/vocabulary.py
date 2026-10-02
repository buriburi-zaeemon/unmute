"""
Controlled Vocabulary, Pronoun Maps, and Verb Tense Rules for UNMUTE NLP Engine.
Supports deterministic grammar transformations for both ASL and ISL.
"""

from typing import Dict, Set

# Time marker classifications
TIME_MARKERS_PAST: Set[str] = {"YESTERDAY", "BEFORE", "PAST", "LAST_WEEK", "AGO"}
TIME_MARKERS_FUTURE: Set[str] = {"TOMORROW", "LATER", "FUTURE", "NEXT_WEEK", "SOON"}
TIME_MARKERS_PRESENT: Set[str] = {"TODAY", "NOW", "CURRENT"}
ALL_TIME_MARKERS: Set[str] = TIME_MARKERS_PAST | TIME_MARKERS_FUTURE | TIME_MARKERS_PRESENT

# Pronoun mapping rules
PRONOUN_MAP: Dict[str, str] = {
    "I": "I",
    "ME": "I",
    "MY": "my",
    "MINE": "mine",
    "YOU": "you",
    "YOUR": "your",
    "YOURS": "yours",
    "HE": "he",
    "HIM": "him",
    "HIS": "his",
    "SHE": "she",
    "HER": "her",
    "HERS": "hers",
    "IT": "it",
    "ITS": "its",
    "WE": "we",
    "OUR": "our",
    "OURS": "ours",
    "THEY": "they",
    "THEIR": "their",
    "THEIRS": "theirs",
}

# Verb conjugation table (Base -> {past, future, present})
VERB_CONJUGATIONS: Dict[str, Dict[str, str]] = {
    "GO": {"past": "went", "future": "will go", "present": "go"},
    "SEE": {"past": "saw", "future": "will see", "present": "see"},
    "HELP": {"past": "helped", "future": "will help", "present": "help"},
    "BUY": {"past": "bought", "future": "will buy", "present": "buy"},
    "COME": {"past": "came", "future": "will come", "present": "come"},
    "EAT": {"past": "ate", "future": "will eat", "present": "eat"},
    "MAKE": {"past": "made", "future": "will make", "present": "make"},
    "WANT": {"past": "wanted", "future": "will want", "present": "want"},
    "NEED": {"past": "needed", "future": "will need", "present": "need"},
    "LIKE": {"past": "liked", "future": "will like", "present": "like"},
    "LOVE": {"past": "loved", "future": "will love", "present": "love"},
    "KNOW": {"past": "knew", "future": "will know", "present": "know"},
    "WORK": {"past": "worked", "future": "will work", "present": "work"},
    "STUDY": {"past": "studied", "future": "will study", "present": "study"},
}

# Static Phrase Map (Direct lookup for common expressions)
PHRASE_MAP: Dict[str, str] = {
    "HELLO": "Hello.",
    "NAMASTE": "Namaste.",
    "THANK YOU": "Thank you.",
    "PLEASE": "Please.",
    "SORRY": "Sorry.",
    "GOODBYE": "Goodbye.",
    "I LOVE YOU": "I love you.",
    "PEACE": "Peace.",
    "OKAY": "Okay.",
    "STOP": "Stop.",
    "THUMBS UP": "Thumbs up.",
    "THUMBS DOWN": "Thumbs down.",
}

# Interrogative / Question words
QUESTION_WORDS: Set[str] = {"WHAT", "WHERE", "WHEN", "WHY", "WHO", "HOW", "WHICH"}
