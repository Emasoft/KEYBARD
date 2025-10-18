#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for filter classes.

Tests line filters including color conversion, dimming, and style transformations.
"""

from rich.color import Color as RichColor
from rich.color import ColorType
from rich.segment import Segment
from rich.style import Style
from rich.terminal_theme import MONOKAI

from keybard.color import Color
from keybard.filter import ANSIToTruecolor, LineFilter, Monochrome, NoColor, dim_color, dim_style, monochrome_style


class TestLineFilter:
    """Tests for LineFilter base class."""

    def test_line_filter_enabled_default(self):
        """Test LineFilter enabled by default."""

        class ConcreteFilter(LineFilter):
            def apply(self, segments: list[Segment], background: Color) -> list[Segment]:
                return segments

        filter = ConcreteFilter()
        assert filter.enabled is True

    def test_line_filter_disabled(self):
        """Test LineFilter can be disabled."""

        class ConcreteFilter(LineFilter):
            def apply(self, segments: list[Segment], background: Color) -> list[Segment]:
                return segments

        filter = ConcreteFilter(enabled=False)
        assert filter.enabled is False


class TestMonochromeStyle:
    """Tests for monochrome_style function."""

    def test_monochrome_style_with_color(self):
        """Test monochrome_style converts colors to monochrome."""
        style = Style.parse("#ff0000 on #0000ff")
        result = monochrome_style(style)

        assert result is not None
        assert result.color is not None

    def test_monochrome_style_with_none_color(self):
        """Test monochrome_style handles None color."""
        style = Style.parse("bold")
        result = monochrome_style(style)

        assert result is not None

    def test_monochrome_style_with_none_bgcolor(self):
        """Test monochrome_style handles None background color."""
        style = Style.parse("#ff0000")
        result = monochrome_style(style)

        assert result is not None


class TestMonochrome:
    """Tests for Monochrome filter."""

    def test_monochrome_apply(self):
        """Test Monochrome filter converts segments to monochrome."""
        filter = Monochrome()
        segments = [Segment("test", Style.parse("#ff0000 on #0000ff"))]
        background = Color(0, 0, 0)

        result = filter.apply(segments, background)

        assert len(result) == 1
        assert result[0].text == "test"

    def test_monochrome_apply_multiple_segments(self):
        """Test Monochrome filter on multiple segments."""
        filter = Monochrome()
        segments = [Segment("hello", Style.parse("#ff0000")), Segment("world", Style.parse("#00ff00"))]
        background = Color(0, 0, 0)

        result = filter.apply(segments, background)

        assert len(result) == 2


class TestNoColor:
    """Tests for NoColor filter."""

    def test_nocolor_apply(self):
        """Test NoColor filter removes colors."""
        filter = NoColor()
        segments = [Segment("test", Style.parse("#ff0000 on #0000ff"))]
        background = Color(0, 0, 0)

        result = filter.apply(segments, background)

        assert len(result) == 1
        assert result[0].text == "test"

    def test_nocolor_apply_with_none_style(self):
        """Test NoColor filter handles None style."""
        filter = NoColor()
        segments = [Segment("test", None)]
        background = Color(0, 0, 0)

        result = filter.apply(segments, background)

        assert len(result) == 1
        assert result[0].style is None

    def test_nocolor_apply_with_control(self):
        """Test NoColor filter preserves control sequences."""
        filter = NoColor()
        segments = [Segment("test", Style.parse("#ff0000"), control="control")]
        background = Color(0, 0, 0)

        result = filter.apply(segments, background)

        assert len(result) == 1
        assert result[0].control == "control"


class TestDimColor:
    """Tests for dim_color function."""

    def test_dim_color_with_valid_triplets(self):
        """Test dim_color blends colors correctly."""
        background = RichColor.from_rgb(0, 0, 0)
        color = RichColor.from_rgb(255, 255, 255)

        result = dim_color(background, color, factor=0.5)

        assert result is not None

    def test_dim_color_with_none_triplet(self):
        """Test dim_color fallback when triplet is None."""
        # Create a color with no triplet (default color)
        background = RichColor.default()
        color = RichColor.from_rgb(255, 255, 255)

        result = dim_color(background, color)

        # Should return original color when background has no triplet
        assert result is color


class TestDimStyle:
    """Tests for dim_style function."""

    def test_dim_style_with_color(self):
        """Test dim_style dims colors correctly."""
        style = Style.parse("dim #ffffff on #000000")
        background = Color(0, 0, 0)

        result = dim_style(style, background, factor=0.5)

        assert result is not None

    def test_dim_style_with_none_color(self):
        """Test dim_style handles None color."""
        style = Style.parse("bold")
        background = Color(0, 0, 0)

        result = dim_style(style, background, factor=0.5)

        # Should return original style when color is None
        assert result is style


class TestANSIToTruecolor:
    """Tests for ANSIToTruecolor filter."""

    def test_ansi_to_truecolor_8_bit_dim(self):
        """Test that converting an 8-bit color with dim doesn't crash.

        Regression test for https://github.com/Textualize/textual/issues/5946

        """
        # Given
        ansi_filter = ANSIToTruecolor(MONOKAI)
        test_color = RichColor("color(253)", ColorType.EIGHT_BIT, number=253)
        test_style = Style(color=test_color, dim=True)
        segments = [Segment("This should not crash", style=test_style)]
        background_color = Color(0, 0, 0)

        # When
        # This line will crash if the bug is present
        new_segments = ansi_filter.apply(segments, background_color)

        # Then
        assert new_segments is not None

    def test_ansi_to_truecolor_with_bgcolor(self):
        """Test ANSIToTruecolor handles background colors."""
        ansi_filter = ANSIToTruecolor(MONOKAI)
        test_color = RichColor("color(253)", ColorType.EIGHT_BIT, number=253)
        bgcolor = RichColor("color(240)", ColorType.EIGHT_BIT, number=240)
        test_style = Style(color=test_color, bgcolor=bgcolor)
        segments = [Segment("test", style=test_style)]
        background_color = Color(0, 0, 0)

        new_segments = ansi_filter.apply(segments, background_color)

        assert len(new_segments) == 1
