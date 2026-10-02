"""
Grammar Rules Engine for UNMUTE.
Provides deterministic, explainable grammar transformations for ASL (Time-Topic-Comment)
and ISL (Subject-Object-Verb / SOV) token sequences.
"""

from typing import List, Optional, Tuple, Set
from nlp.token_schema import Token
from nlp.vocabulary import (
    TIME_MARKERS_PAST,
    TIME_MARKERS_FUTURE,
    TIME_MARKERS_PRESENT,
    ALL_TIME_MARKERS,
    PRONOUN_MAP,
    VERB_CONJUGATIONS,
    QUESTION_WORDS,
)


class ASLGrammarEngine:
    """
    Grammar engine for ASL (Topic-Time-Comment structure).
    Extracts time markers, determines sentence tense, inflects verbs,
    and formats English SVO sentence order.
    """

    def transform(self, tokens: List[Token]) -> str:
        if not tokens:
            return ""

        raw_texts = [t.text for t in tokens]
        
        # 1. Check for time markers
        found_time_marker: Optional[str] = None
        tense_mode = "present"
        clean_words: List[str] = []

        for word in raw_texts:
            if word in ALL_TIME_MARKERS:
                found_time_marker = word.lower()
                if word in TIME_MARKERS_PAST:
                    tense_mode = "past"
                elif word in TIME_MARKERS_FUTURE:
                    tense_mode = "future"
                elif word in TIME_MARKERS_PRESENT:
                    tense_mode = "present"
            else:
                clean_words.append(word)

        if not clean_words and found_time_marker:
            return found_time_marker.capitalize()

        # 2. Process words: map pronouns, inflect verbs
        transformed_words: List[str] = []
        for word in clean_words:
            if word in PRONOUN_MAP:
                transformed_words.append(PRONOUN_MAP[word])
            elif word in VERB_CONJUGATIONS:
                verb_forms = VERB_CONJUGATIONS[word]
                transformed_words.append(verb_forms.get(tense_mode, word.lower()))
            else:
                transformed_words.append(word.lower())

        # 3. Append time marker at end if present
        if found_time_marker and found_time_marker not in transformed_words:
            transformed_words.append(found_time_marker)

        return " ".join(transformed_words)


class ISLGrammarEngine:
    """
    Grammar engine for ISL (Subject-Object-Verb / SOV structure & Cultural Greetings).
    Handles opening greetings ('NAMASTE'), reorders SOV patterns into fluent English,
    and applies modal/verb transformations.
    """

    def transform(self, tokens: List[Token]) -> str:
        if not tokens:
            return ""

        raw_texts = [t.text for t in tokens]
        
        # 1. Handle opening greetings (e.g. NAMASTE, HELLO)
        greeting_prefix = ""
        words_to_process = list(raw_texts)

        if words_to_process and words_to_process[0] in ("NAMASTE", "HELLO"):
            greeting_prefix = words_to_process.pop(0).capitalize() + ","

        if not words_to_process:
            return greeting_prefix.rstrip(",") if greeting_prefix else ""

        # 2. Check for SOV order: e.g. ["I", "YOU", "HELP"] or ["I", "HELP", "YOU"]
        # If last word is a verb and second-to-last is a pronoun/noun (Object), reorder to SVO
        subject: Optional[str] = None
        object_word: Optional[str] = None
        verb_word: Optional[str] = None

        if len(words_to_process) == 3:
            w1, w2, w3 = words_to_process[0], words_to_process[1], words_to_process[2]
            if w1 in PRONOUN_MAP and w2 in PRONOUN_MAP and w3 in VERB_CONJUGATIONS:
                # SOV pattern -> SVO (e.g. ["I", "YOU", "HELP"] -> Subject: I, Verb: HELP, Object: YOU)
                subject = PRONOUN_MAP[w1]
                object_word = PRONOUN_MAP[w2]
                verb_word = VERB_CONJUGATIONS[w3]["future" if greeting_prefix else "present"]
                core_sentence = f"{subject} {verb_word} {object_word}"
                return f"{greeting_prefix} {core_sentence}".strip()

        # Fallback standard transformation
        transformed_words: List[str] = []
        for word in words_to_process:
            if word in PRONOUN_MAP:
                transformed_words.append(PRONOUN_MAP[word])
            elif word in VERB_CONJUGATIONS:
                # Default to future/helper if greeting present, else present
                tense = "future" if greeting_prefix else "present"
                transformed_words.append(VERB_CONJUGATIONS[word][tense])
            else:
                transformed_words.append(word.lower())

        core_sentence = " ".join(transformed_words)
        return f"{greeting_prefix} {core_sentence}".strip()
