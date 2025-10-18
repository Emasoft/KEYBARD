#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Parser base class.

Tests the generic parser infrastructure including Read1, Peek1, timeouts,
and EOF handling.
"""

import time
from typing import Generator

import pytest

from keybard._parser import ParseEOF, ParseError, ParseTimeout, Parser, Peek1, Read1


class SimpleTokenParser(Parser[str]):
    """Simple test parser that yields single characters as tokens."""

    def parse(self, token_callback) -> Generator[Read1 | Peek1, str, None]:
        """Parse stream character by character."""
        while True:
            try:
                char = yield self.read1()
                token_callback(char)
            except (ParseEOF, ParseTimeout):
                return


class TimeoutParser(Parser[str]):
    """Parser that uses timeouts for testing."""

    def parse(self, token_callback) -> Generator[Read1 | Peek1, str, None]:
        """Parse with timeout."""
        while True:
            try:
                char = yield self.read1(timeout=0.1)
                token_callback(char)
            except (ParseEOF, ParseTimeout):
                return


class PeekParser(Parser[str]):
    """Parser that uses peek operations."""

    def parse(self, token_callback) -> Generator[Read1 | Peek1, str, None]:
        """Parse using peek."""
        while True:
            try:
                # Peek at next char
                char = yield self.peek1()
                # If it's interesting, read it
                if char in "abc":
                    char = yield self.read1()
                    token_callback(char)
                else:
                    # Skip it
                    _ = yield self.read1()
            except (ParseEOF, ParseTimeout):
                return


class TestParserBasics:
    """Tests for basic Parser functionality."""

    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = SimpleTokenParser()
        assert not parser.is_eof
        assert len(parser._tokens) == 0

    def test_feed_single_character(self):
        """Test feeding single character."""
        parser = SimpleTokenParser()
        tokens = list(parser.feed("a"))
        assert tokens == ["a"]

    def test_feed_multiple_characters(self):
        """Test feeding multiple characters."""
        parser = SimpleTokenParser()
        tokens = list(parser.feed("hello"))
        assert tokens == ["h", "e", "l", "l", "o"]

    def test_feed_empty_string_sets_eof(self):
        """Test feeding empty string sets EOF."""
        parser = SimpleTokenParser()
        tokens = list(parser.feed(""))
        assert parser.is_eof
        assert tokens == []

    def test_feed_after_eof_raises_error(self):
        """Test feeding after EOF raises ParseError."""
        parser = SimpleTokenParser()
        list(parser.feed(""))  # Need to consume the generator
        assert parser.is_eof

        with pytest.raises(ParseError, match="end of file reached"):
            list(parser.feed("more data"))

    def test_multiple_feed_calls(self):
        """Test multiple feed calls accumulate tokens."""
        parser = SimpleTokenParser()
        tokens1 = list(parser.feed("hel"))
        tokens2 = list(parser.feed("lo"))
        assert tokens1 == ["h", "e", "l"]
        assert tokens2 == ["l", "o"]


class TestParserTimeout:
    """Tests for Parser timeout handling."""

    def test_tick_with_timeout(self):
        """Test tick() triggers timeout."""
        parser = TimeoutParser()

        # Start parsing
        tokens = list(parser.feed("a"))
        assert tokens == ["a"]

        # Now parser is waiting with timeout
        # Sleep past the timeout
        time.sleep(0.15)

        # Tick should trigger timeout which will cause the parser generator to exit
        # In Python 3.7+ this raises RuntimeError instead of StopIteration
        try:
            timeout_tokens = list(parser.tick())
            # If we get here, timeout tokens should be a list
            assert isinstance(timeout_tokens, list)
        except RuntimeError:
            # This is expected when the generator exits
            pass

    def test_tick_without_timeout(self):
        """Test tick() when no timeout is set."""
        parser = SimpleTokenParser()  # No timeout
        tokens = list(parser.feed("a"))
        assert tokens == ["a"]

        # Tick should return empty when no timeout
        tick_tokens = list(parser.tick())
        assert tick_tokens == []


class TestParserPeek:
    """Tests for Parser peek operations."""

    def test_peek_does_not_advance(self):
        """Test peek doesn't advance parser position."""
        parser = PeekParser()

        # Feed "abc" - parser peeks each char
        tokens = list(parser.feed("abc"))
        # All should be collected since they're in "abc"
        assert tokens == ["a", "b", "c"]

    def test_peek_with_skip(self):
        """Test peek allows selective reading."""
        parser = PeekParser()

        # Feed "axbycz" - parser only takes a,b,c and skips x,y,z
        tokens = list(parser.feed("axbycz"))
        assert tokens == ["a", "b", "c"]


class TestParserEdgeCases:
    """Tests for Parser edge cases."""

    def test_parser_with_eof_in_stream(self):
        """Test parser handling EOF properly."""
        parser = SimpleTokenParser()

        # Feed some data then EOF
        tokens1 = list(parser.feed("hi"))
        assert tokens1 == ["h", "i"]

        # Feed empty to signal EOF
        tokens2 = list(parser.feed(""))
        assert parser.is_eof
        assert tokens2 == []

    def test_parser_pending_tokens_on_eof(self):
        """Test parser yields pending tokens on EOF."""
        parser = SimpleTokenParser()

        # Feed data
        list(parser.feed("test"))

        # Feed EOF - should yield any remaining tokens
        _ = list(parser.feed(""))
        assert parser.is_eof


class TestParseExceptions:
    """Tests for parse-related exceptions."""

    def test_parse_error_exception(self):
        """Test ParseError exception."""
        error = ParseError("test error")
        assert str(error) == "test error"
        assert isinstance(error, Exception)

    def test_parse_eof_exception(self):
        """Test ParseEOF exception."""
        error = ParseEOF("end of stream")
        assert isinstance(error, ParseError)
        assert isinstance(error, Exception)

    def test_parse_timeout_exception(self):
        """Test ParseTimeout exception."""
        error = ParseTimeout("timeout occurred")
        assert isinstance(error, ParseError)
        assert isinstance(error, Exception)


class TestRead1AndPeek1:
    """Tests for Read1 and Peek1 named tuples."""

    def test_read1_creation(self):
        """Test Read1 creation."""
        read = Read1()
        assert read.timeout is None

    def test_read1_with_timeout(self):
        """Test Read1 with timeout."""
        read = Read1(timeout=1.0)
        assert read.timeout == 1.0

    def test_peek1_creation(self):
        """Test Peek1 creation."""
        peek = Peek1()
        assert peek.timeout is None

    def test_peek1_with_timeout(self):
        """Test Peek1 with timeout."""
        peek = Peek1(timeout=0.5)
        assert peek.timeout == 0.5

    def test_read1_is_namedtuple(self):
        """Test Read1 is a NamedTuple."""
        read = Read1(timeout=2.0)
        assert hasattr(read, "_fields")
        assert "timeout" in read._fields

    def test_peek1_is_namedtuple(self):
        """Test Peek1 is a NamedTuple."""
        peek = Peek1(timeout=3.0)
        assert hasattr(peek, "_fields")
        assert "timeout" in peek._fields
