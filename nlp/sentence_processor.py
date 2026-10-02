"""
Sentence Processor Module for UNMUTE.
Orchestrates dual-language sign sequence transformations, capitalization,
sentence boundary punctuation, and phrase shortcut resolution.
"""

from typing import List, Union, Dict, Any, Optional
import re
from nlp.token_schema import Token
from nlp.token_normalizer import TokenNormalizer
from nlp.sequence_buffer import SequenceBuffer
from nlp.vocabulary import PHRASE_MAP, QUESTION_WORDS
from nlp.grammar_rules import ASLGrammarEngine, ISLGrammarEngine


class SentenceProcessor:
    """
    Processes sequence buffer tokens into fully formed, natural-language English sentences
    for both ASL and ISL sign language pipelines.
    """

    def __init__(self):
        self.normalizer = TokenNormalizer()
        self.asl_engine = ASLGrammarEngine()
        self.isl_engine = ISLGrammarEngine()

    def process_tokens(
        self,
        raw_inputs: List[Union[Token, Dict[str, Any], str]],
        language: str = "ASL"
    ) -> str:
        """
        Process a sequence of tokens into a formatted sentence string.
        """
        if not raw_inputs:
            return ""

        language_mode = str(language).strip().upper()

        # Convert raw inputs to normalized Tokens
        tokens: List[Token] = []
        for item in raw_inputs:
            if isinstance(item, Token):
                token_obj = item
            elif isinstance(item, dict):
                token_obj = Token.from_dict(item)
            elif isinstance(item, str):
                token_obj = Token(text=item, confidence=1.0, language=language_mode)
            else:
                continue

            token_obj.language = language_mode
            normalized = self.normalizer.normalize_token(token_obj)
            tokens.append(normalized)

        if not tokens:
            return ""

        # 1. Check direct static phrase map lookup
        token_texts = [t.text for t in tokens]
        joined_raw = " ".join(token_texts)
        if joined_raw in PHRASE_MAP:
            return PHRASE_MAP[joined_raw]

        # Single word static phrase
        if len(tokens) == 1 and token_texts[0] in PHRASE_MAP:
            return PHRASE_MAP[token_texts[0]]

        # 2. Language-specific grammar transformation
        if language_mode == "ISL":
            raw_sentence = self.isl_engine.transform(tokens)
        else:
            raw_sentence = self.asl_engine.transform(tokens)

        if not raw_sentence:
            return ""

        # 3. Capitalization & Punctuation Pipeline
        final_sentence = self._format_sentence(raw_sentence, token_texts)
        return final_sentence

    def process_buffer(self, sequence_buffer: SequenceBuffer) -> str:
        """
        Process tokens directly from a SequenceBuffer instance.
        """
        tokens = sequence_buffer.get_tokens()
        return self.process_tokens(tokens, language=sequence_buffer.language)

    def _format_sentence(self, text: str, original_tokens: List[str]) -> str:
        """
        Apply first-letter capitalization, standalone pronoun 'I' capitalization,
        and sentence-boundary punctuation (. or ?).
        """
        clean = text.strip()
        if not clean:
            return ""

        # Capitalize standalone 'i' to 'I'
        clean = re.sub(r'\bi\b', 'I', clean)

        # Capitalize first character
        clean = clean[0].upper() + clean[1:]

        # Determine terminal punctuation
        is_question = any(word in QUESTION_WORDS for word in original_tokens)
        punctuation = "?" if is_question else "."

        # Strip trailing punctuation before appending
        if clean.endswith((".", "?", "!")):
            return clean
        elif clean.endswith(","):
            return clean[:-1] + punctuation
        else:
            return clean + punctuation
