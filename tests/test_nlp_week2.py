"""
Unit Tests for Week 2 — Structured Sign Tokens and Sequence Interface.
Tests Token schema, TokenNormalizer, SequenceBuffer, and process_sign_sequence helper.
"""

import time
import pytest
from nlp.token_schema import Token
from nlp.token_normalizer import TokenNormalizer, ASL_LEXICON, ISL_LEXICON
from nlp.sequence_buffer import SequenceBuffer, process_sign_sequence


# ============================================================================
# Sub-task 2.1 Tests: Dual-Language Structured Token Schema
# ============================================================================

def test_token_instantiation_and_defaults():
    t = Token(text="hello", confidence=0.95)
    assert t.text == "HELLO"
    assert t.confidence == 0.95
    assert t.language == "ASL"
    assert t.sign_type == "letter"
    assert t.timestamp > 0


def test_token_validation_invalid_language():
    with pytest.raises(ValueError, match="Invalid language"):
        Token(text="A", confidence=0.8, language="FRENCH")


def test_token_validation_invalid_sign_type():
    with pytest.raises(ValueError, match="Invalid sign_type"):
        Token(text="A", confidence=0.8, sign_type="gesture")


def test_token_confidence_clamping():
    t1 = Token(text="A", confidence=1.5)
    assert t1.confidence == 1.0

    t2 = Token(text="A", confidence=-0.5)
    assert t2.confidence == 0.0


def test_token_dict_serialization():
    t = Token(text="NAMASTE", confidence=0.88, language="ISL", sign_type="phrase")
    d = t.to_dict()
    assert d["text"] == "NAMASTE"
    assert d["language"] == "ISL"
    assert d["sign_type"] == "phrase"

    t_reconstructed = Token.from_dict(d)
    assert t_reconstructed.text == "NAMASTE"
    assert t_reconstructed.language == "ISL"
    assert t_reconstructed.confidence == 0.88


# ============================================================================
# Sub-task 2.2 Tests: Token Normalization & Lexicon Mapping
# ============================================================================

def test_token_normalizer_synonyms():
    norm = TokenNormalizer()
    assert norm.normalize_text("hi") == "HELLO"
    assert norm.normalize_text("namaskar") == "NAMASTE"
    assert norm.normalize_text("thanks") == "THANK YOU"
    assert norm.normalize_text("ily") == "I LOVE YOU"


def test_token_normalizer_token_instance():
    norm = TokenNormalizer()
    raw = Token(text="hi", confidence=0.9, language="ASL")
    normalized = norm.normalize_token(raw)
    assert normalized.text == "HELLO"
    assert normalized.sign_type == "phrase"


def test_lexicon_validation_asl_and_isl():
    norm = TokenNormalizer()
    
    # ASL valid & invalid
    t_asl_valid = Token(text="HELLO", confidence=0.9, language="ASL")
    assert norm.is_valid_token(t_asl_valid) is True

    t_asl_invalid = Token(text="XYZ_UNKNOWN", confidence=0.9, language="ASL")
    assert norm.is_valid_token(t_asl_invalid) is False

    # ISL valid (e.g. NAMASTE)
    t_isl_valid = Token(text="NAMASTE", confidence=0.9, language="ISL")
    assert norm.is_valid_token(t_isl_valid) is True


# ============================================================================
# Sub-task 2.3 & 2.4 Tests: Sequence Buffer & Filtering
# ============================================================================

def test_sequence_buffer_add_and_retrieve():
    buf = SequenceBuffer(language="ASL", confidence_threshold=0.5, strict_lexicon_check=False)
    assert buf.add_token(Token(text="I", confidence=0.8)) is True
    assert buf.add_token(Token(text="GO", confidence=0.85)) is True
    assert buf.add_token(Token(text="HOME", confidence=0.9)) is True

    assert len(buf) == 3
    assert buf.get_token_texts() == ["I", "GO", "HOME"]


def test_sequence_buffer_confidence_filtering():
    buf = SequenceBuffer(language="ASL", confidence_threshold=0.6, strict_lexicon_check=False)
    
    # Below threshold -> rejected
    assert buf.add_token(Token(text="A", confidence=0.4)) is False
    assert len(buf) == 0

    # At or above threshold -> accepted
    assert buf.add_token(Token(text="A", confidence=0.65)) is True
    assert len(buf) == 1


def test_sequence_buffer_duplicate_suppression():
    buf = SequenceBuffer(language="ASL", deduplication_window=1.0, strict_lexicon_check=False)
    now = time.time()

    t1 = Token(text="A", confidence=0.9, timestamp=now)
    t2 = Token(text="A", confidence=0.9, timestamp=now + 0.3)  # Duplicate within 1.0s
    t3 = Token(text="B", confidence=0.9, timestamp=now + 0.5)  # Different token -> accepted
    t4 = Token(text="A", confidence=0.9, timestamp=now + 1.5)  # Same token after 1.5s -> accepted

    assert buf.add_token(t1) is True
    assert buf.add_token(t2) is False  # Suppressed duplicate chatter
    assert buf.add_token(t3) is True
    assert buf.add_token(t4) is True

    assert buf.get_token_texts() == ["A", "B", "A"]


def test_process_sign_sequence_decoupled_helper():
    seq = ["I", {"text": "GO", "confidence": 0.8}, Token(text="HOME", confidence=0.9)]
    processed = process_sign_sequence(seq, language="ASL")
    
    assert len(processed) == 3
    assert [t.text for t in processed] == ["I", "GO", "HOME"]


def test_sequence_buffer_language_switching():
    buf = SequenceBuffer(language="ASL", strict_lexicon_check=False)
    buf.add_token("A")
    assert len(buf) == 1

    # Switch to ISL -> clears buffer for new language context
    buf.set_language("ISL")
    assert len(buf) == 0
    assert buf.language == "ISL"
