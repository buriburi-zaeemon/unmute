"""
Unit Tests for Week 3 — Rule-Based Sentence Formation & Subtitle Formatting.
Tests ASLGrammarEngine, ISLGrammarEngine, SentenceProcessor, and Subtitle Exporters.
"""

import pytest
from nlp.token_schema import Token
from nlp.sequence_buffer import SequenceBuffer
from nlp.vocabulary import PHRASE_MAP, VERB_CONJUGATIONS, PRONOUN_MAP
from nlp.grammar_rules import ASLGrammarEngine, ISLGrammarEngine
from nlp.sentence_processor import SentenceProcessor
from sign_engine.video_processor import VideoProcessor, SubtitleSegment


# ============================================================================
# Task 3.4 Tests: ASL & ISL Rule-Based Grammar Engines
# ============================================================================

def test_asl_grammar_engine_past_tense():
    engine = ASLGrammarEngine()
    tokens = [
        Token(text="I", confidence=0.9),
        Token(text="GO", confidence=0.9),
        Token(text="HOME", confidence=0.9),
        Token(text="YESTERDAY", confidence=0.9),
    ]
    result = engine.transform(tokens)
    assert result == "I went home yesterday"


def test_asl_grammar_engine_future_tense():
    engine = ASLGrammarEngine()
    tokens = [
        Token(text="I", confidence=0.9),
        Token(text="HELP", confidence=0.9),
        Token(text="YOU", confidence=0.9),
        Token(text="TOMORROW", confidence=0.9),
    ]
    result = engine.transform(tokens)
    assert result == "I will help you tomorrow"


def test_isl_grammar_engine_sov_and_greetings():
    engine = ISLGrammarEngine()
    tokens = [
        Token(text="NAMASTE", confidence=0.9, language="ISL"),
        Token(text="I", confidence=0.9, language="ISL"),
        Token(text="YOU", confidence=0.9, language="ISL"),
        Token(text="HELP", confidence=0.9, language="ISL"),
    ]
    result = engine.transform(tokens)
    assert result == "Namaste, I will help you"


def test_isl_grammar_engine_sov_reordering():
    engine = ISLGrammarEngine()
    tokens = [
        Token(text="I", confidence=0.9, language="ISL"),
        Token(text="YOU", confidence=0.9, language="ISL"),
        Token(text="HELP", confidence=0.9, language="ISL"),
    ]
    result = engine.transform(tokens)
    assert result == "I help you"


# ============================================================================
# Task 3.5 Tests: Sentence Processor & Capitalization / Punctuation
# ============================================================================

def test_sentence_processor_phrase_shortcut():
    proc = SentenceProcessor()
    assert proc.process_tokens(["HELLO"], language="ASL") == "Hello."
    assert proc.process_tokens(["NAMASTE"], language="ISL") == "Namaste."
    assert proc.process_tokens(["THANK YOU"], language="ASL") == "Thank you."


def test_sentence_processor_question_punctuation():
    proc = SentenceProcessor()
    tokens = ["WHERE", "YOU", "GO"]
    res = proc.process_tokens(tokens, language="ASL")
    assert res.endswith("?")
    assert res.startswith("Where")


def test_sentence_processor_with_sequence_buffer():
    proc = SentenceProcessor()
    buf = SequenceBuffer(language="ASL", confidence_threshold=0.5, strict_lexicon_check=False)
    buf.add_token(Token(text="I", confidence=0.9))
    buf.add_token(Token(text="GO", confidence=0.9))
    buf.add_token(Token(text="HOME", confidence=0.9))
    buf.add_token(Token(text="YESTERDAY", confidence=0.9))

    sentence = proc.process_buffer(buf)
    assert sentence == "I went home yesterday."


# ============================================================================
# Task 3.3 Tests: Subtitle Exporter Format Validation
# ============================================================================

def test_video_processor_subtitle_exports():
    vp = VideoProcessor()
    segments = [
        SubtitleSegment(
            index=1,
            start_time=0.5,
            end_time=2.0,
            text="HELLO",
            confidence=0.95,
            sign_type="phrase"
        ),
        SubtitleSegment(
            index=2,
            start_time=2.5,
            end_time=4.0,
            text="THANK YOU",
            confidence=0.92,
            sign_type="phrase"
        ),
    ]

    srt = vp._generate_srt(segments)
    vtt = vp._generate_vtt(segments)

    assert "1" in srt
    assert "00:00:00,500 --> 00:00:02,000" in srt
    assert "HELLO" in srt

    assert "WEBVTT" in vtt
    assert "00:00:00.500 --> 00:00:02.000" in vtt
    assert "THANK YOU" in vtt
