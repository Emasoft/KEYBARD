#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for geometry module (Offset, Size, Region, Spacing).

This test suite covers the core geometry classes used throughout KEYBARD
for terminal coordinate and dimension management.
"""

import pytest

from keybard.geometry import Offset, Region, Size, Spacing, clamp


class TestClamp:
    """Tests for the clamp() function."""

    def test_clamp_within_range(self):
        """Test clamping a value already within range."""
        assert clamp(5, 0, 10) == 5
        assert clamp(5.5, 0.0, 10.0) == 5.5

    def test_clamp_below_minimum(self):
        """Test clamping a value below minimum."""
        assert clamp(-5, 0, 10) == 0
        assert clamp(-5.5, -2.0, 10.0) == -2.0

    def test_clamp_above_maximum(self):
        """Test clamping a value above maximum."""
        assert clamp(15, 0, 10) == 10
        assert clamp(15.5, 0.0, 10.0) == 10.0

    def test_clamp_reverse_order(self):
        """Test clamping with min/max in reverse order."""
        # Function should handle reversed min/max gracefully
        assert clamp(5, 10, 0) == 5  # Within reversed range
        assert clamp(-5, 10, 0) == 0  # Below min (which is max)
        assert clamp(15, 10, 0) == 10  # Above max (which is min)


class TestOffset:
    """Tests for the Offset class."""

    def test_offset_creation(self):
        """Test creating an offset."""
        offset = Offset(3, 5)
        assert offset.x == 3
        assert offset.y == 5

    def test_offset_default_values(self):
        """Test offset with default values."""
        offset = Offset()
        assert offset.x == 0
        assert offset.y == 0

    def test_is_origin(self):
        """Test is_origin property."""
        assert Offset(0, 0).is_origin
        assert not Offset(1, 0).is_origin
        assert not Offset(0, 1).is_origin

    def test_clamped(self):
        """Test clamped property."""
        assert Offset(-5, -10).clamped == Offset(0, 0)
        assert Offset(5, -10).clamped == Offset(5, 0)
        assert Offset(-5, 10).clamped == Offset(0, 10)
        assert Offset(5, 10).clamped == Offset(5, 10)

    def test_transpose(self):
        """Test transpose property."""
        assert Offset(3, 5).transpose == (5, 3)
        assert Offset(0, 0).transpose == (0, 0)

    def test_offset_bool(self):
        """Test boolean conversion."""
        assert not Offset(0, 0)
        assert Offset(1, 0)
        assert Offset(0, 1)
        assert Offset(1, 1)

    def test_offset_addition(self):
        """Test offset addition."""
        assert Offset(3, 5) + Offset(2, 1) == Offset(5, 6)
        assert Offset(3, 5) + (2, 1) == Offset(5, 6)

    def test_offset_subtraction(self):
        """Test offset subtraction."""
        assert Offset(5, 6) - Offset(2, 1) == Offset(3, 5)
        assert Offset(5, 6) - (2, 1) == Offset(3, 5)

    def test_offset_multiplication(self):
        """Test offset multiplication."""
        assert Offset(3, 5) * 2 == Offset(6, 10)
        assert Offset(3, 5) * 2.5 == Offset(7, 12)  # int() conversion
        assert Offset(3, 5) * (2, 3) == Offset(6, 15)

    def test_offset_negation(self):
        """Test offset negation."""
        assert -Offset(3, 5) == Offset(-3, -5)
        assert -Offset(-3, -5) == Offset(3, 5)

    def test_blend(self):
        """Test blend method."""
        start = Offset(0, 0)
        end = Offset(10, 10)
        assert start.blend(end, 0.0) == Offset(0, 0)
        assert start.blend(end, 0.5) == Offset(5, 5)
        assert start.blend(end, 1.0) == Offset(10, 10)

    def test_get_distance_to(self):
        """Test get_distance_to method."""
        assert Offset(0, 0).get_distance_to(Offset(3, 4)) == 5.0
        assert Offset(0, 0).get_distance_to(Offset(0, 0)) == 0.0

    def test_clamp_method(self):
        """Test clamp method."""
        assert Offset(15, 15).clamp(10, 10) == Offset(9, 9)
        assert Offset(5, 5).clamp(10, 10) == Offset(5, 5)
        assert Offset(-5, -5).clamp(10, 10) == Offset(0, 0)


class TestSize:
    """Tests for the Size class."""

    def test_size_creation(self):
        """Test creating a size."""
        size = Size(10, 20)
        assert size.width == 10
        assert size.height == 20

    def test_size_default_values(self):
        """Test size with default values."""
        size = Size()
        assert size.width == 0
        assert size.height == 0

    def test_size_bool(self):
        """Test boolean conversion."""
        assert not Size(0, 0)
        assert not Size(10, 0)  # No area
        assert not Size(0, 10)  # No area
        assert Size(10, 20)  # Has area

    def test_area(self):
        """Test area property."""
        assert Size(10, 20).area == 200
        assert Size(0, 0).area == 0

    def test_region_property(self):
        """Test region property."""
        region = Size(10, 20).region
        assert region == Region(0, 0, 10, 20)

    def test_line_range(self):
        """Test line_range property."""
        assert list(Size(10, 5).line_range) == [0, 1, 2, 3, 4]

    def test_with_width(self):
        """Test with_width method."""
        assert Size(10, 20).with_width(30) == Size(30, 20)

    def test_with_height(self):
        """Test with_height method."""
        assert Size(10, 20).with_height(30) == Size(10, 30)

    def test_size_addition(self):
        """Test size addition."""
        assert Size(10, 20) + Size(5, 10) == Size(15, 30)
        assert Size(10, 20) + (5, 10) == Size(15, 30)
        # Negative results clamp to 0
        assert Size(10, 20) + (-15, -25) == Size(0, 0)

    def test_size_subtraction(self):
        """Test size subtraction."""
        assert Size(10, 20) - Size(5, 10) == Size(5, 10)
        assert Size(10, 20) - (5, 10) == Size(5, 10)
        # Negative results clamp to 0
        assert Size(10, 20) - (15, 25) == Size(0, 0)

    def test_contains(self):
        """Test contains method."""
        size = Size(10, 20)
        assert size.contains(5, 10)
        assert size.contains(0, 0)
        assert size.contains(9, 19)
        assert not size.contains(10, 20)  # Not inclusive
        assert not size.contains(-1, 5)
        assert not size.contains(5, -1)

    def test_contains_point(self):
        """Test contains_point method."""
        size = Size(10, 20)
        assert size.contains_point((5, 10))
        assert size.contains_point((0, 0))
        assert not size.contains_point((10, 20))

    def test_contains_operator(self):
        """Test __contains__ operator."""
        size = Size(10, 20)
        assert (5, 10) in size
        assert (0, 0) in size
        assert (10, 20) not in size

    def test_clamp_offset(self):
        """Test clamp_offset method."""
        size = Size(10, 20)
        assert size.clamp_offset(Offset(5, 10)) == Offset(5, 10)
        assert size.clamp_offset(Offset(15, 25)) == Offset(9, 19)
        assert size.clamp_offset(Offset(-5, -10)) == Offset(0, 0)


class TestRegion:
    """Tests for the Region class."""

    def test_region_creation(self):
        """Test creating a region."""
        region = Region(5, 10, 20, 30)
        assert region.x == 5
        assert region.y == 10
        assert region.width == 20
        assert region.height == 30

    def test_region_default_values(self):
        """Test region with default values."""
        region = Region()
        assert region == Region(0, 0, 0, 0)

    def test_from_corners(self):
        """Test from_corners class method."""
        region = Region.from_corners(5, 10, 25, 40)
        assert region == Region(5, 10, 20, 30)

    def test_from_offset(self):
        """Test from_offset class method."""
        region = Region.from_offset((5, 10), (20, 30))
        assert region == Region(5, 10, 20, 30)

    def test_region_bool(self):
        """Test boolean conversion."""
        assert not Region(0, 0, 0, 0)
        assert not Region(5, 10, 0, 10)  # No area
        assert not Region(5, 10, 10, 0)  # No area
        assert Region(5, 10, 20, 30)  # Has area

    def test_column_span(self):
        """Test column_span property."""
        assert Region(5, 10, 20, 30).column_span == (5, 25)

    def test_line_span(self):
        """Test line_span property."""
        assert Region(5, 10, 20, 30).line_span == (10, 40)

    def test_right(self):
        """Test right property."""
        assert Region(5, 10, 20, 30).right == 25

    def test_bottom(self):
        """Test bottom property."""
        assert Region(5, 10, 20, 30).bottom == 40

    def test_area(self):
        """Test area property."""
        assert Region(5, 10, 20, 30).area == 600

    def test_offset_property(self):
        """Test offset property."""
        assert Region(5, 10, 20, 30).offset == Offset(5, 10)

    def test_size_property(self):
        """Test size property."""
        assert Region(5, 10, 20, 30).size == Size(20, 30)

    def test_corners(self):
        """Test corners property."""
        assert Region(5, 10, 20, 30).corners == (5, 10, 25, 40)

    def test_region_addition(self):
        """Test region addition (translation)."""
        assert Region(5, 10, 20, 30) + (2, 3) == Region(7, 13, 20, 30)
        assert Region(5, 10, 20, 30) + Offset(2, 3) == Region(7, 13, 20, 30)

    def test_region_subtraction(self):
        """Test region subtraction (translation)."""
        assert Region(5, 10, 20, 30) - (2, 3) == Region(3, 7, 20, 30)
        assert Region(5, 10, 20, 30) - Offset(2, 3) == Region(3, 7, 20, 30)

    def test_contains_method(self):
        """Test contains method."""
        region = Region(5, 10, 20, 30)
        assert region.contains(10, 20)
        assert region.contains(5, 10)  # Top left corner
        assert not region.contains(25, 40)  # Bottom right (not inclusive)
        assert not region.contains(0, 0)

    def test_contains_point_method(self):
        """Test contains_point method."""
        region = Region(5, 10, 20, 30)
        assert region.contains_point((10, 20))
        assert region.contains_point((5, 10))
        assert not region.contains_point((25, 40))

    def test_contains_operator(self):
        """Test __contains__ operator."""
        region = Region(5, 10, 20, 30)
        assert (10, 20) in region
        assert (5, 10) in region
        assert (25, 40) not in region

    def test_contains_region(self):
        """Test contains_region method."""
        outer = Region(0, 0, 100, 100)
        inner = Region(10, 10, 20, 20)
        assert outer.contains_region(inner)
        assert inner in outer  # Uses __contains__

        overlapping = Region(50, 50, 100, 100)
        assert not outer.contains_region(overlapping)

    def test_overlaps(self):
        """Test overlaps method."""
        region1 = Region(0, 0, 10, 10)
        region2 = Region(5, 5, 10, 10)
        region3 = Region(20, 20, 10, 10)

        assert region1.overlaps(region2)
        assert region2.overlaps(region1)
        assert not region1.overlaps(region3)

    def test_intersection(self):
        """Test intersection method."""
        region1 = Region(0, 0, 10, 10)
        region2 = Region(5, 5, 10, 10)
        intersection = region1.intersection(region2)
        assert intersection == Region(5, 5, 5, 5)

    def test_union(self):
        """Test union method."""
        region1 = Region(0, 0, 10, 10)
        region2 = Region(5, 5, 15, 15)
        union = region1.union(region2)
        assert union == Region(0, 0, 20, 20)

    def test_translate(self):
        """Test translate method."""
        region = Region(5, 10, 20, 30)
        translated = region.translate((3, 4))
        assert translated == Region(8, 14, 20, 30)

    def test_clip(self):
        """Test clip method."""
        region = Region(5, 10, 20, 30)
        clipped = region.clip(15, 25)
        assert clipped == Region(5, 10, 10, 15)

    def test_grow(self):
        """Test grow method."""
        region = Region(10, 10, 20, 20)
        grown = region.grow((2, 3, 4, 5))  # top, right, bottom, left
        assert grown == Region(5, 8, 28, 26)

    def test_shrink(self):
        """Test shrink method."""
        region = Region(10, 10, 20, 20)
        shrunk = region.shrink((2, 3, 4, 5))  # top, right, bottom, left
        assert shrunk == Region(15, 12, 12, 14)

    def test_split_vertical(self):
        """Test split_vertical method."""
        region = Region(0, 0, 10, 10)
        left, right = region.split_vertical(6)
        assert left == Region(0, 0, 6, 10)
        assert right == Region(6, 0, 4, 10)

    def test_split_horizontal(self):
        """Test split_horizontal method."""
        region = Region(0, 0, 10, 10)
        top, bottom = region.split_horizontal(6)
        assert top == Region(0, 0, 10, 6)
        assert bottom == Region(0, 6, 10, 4)

    def test_split(self):
        """Test split method (into 4 regions)."""
        region = Region(0, 0, 10, 10)
        tl, tr, bl, br = region.split(6, 7)
        assert tl == Region(0, 0, 6, 7)
        assert tr == Region(6, 0, 4, 7)
        assert bl == Region(0, 7, 6, 3)
        assert br == Region(6, 7, 4, 3)


class TestSpacing:
    """Tests for the Spacing class."""

    def test_spacing_creation(self):
        """Test creating spacing."""
        spacing = Spacing(1, 2, 3, 4)
        assert spacing.top == 1
        assert spacing.right == 2
        assert spacing.bottom == 3
        assert spacing.left == 4

    def test_spacing_default_values(self):
        """Test spacing with default values."""
        spacing = Spacing()
        assert spacing == Spacing(0, 0, 0, 0)

    def test_spacing_bool(self):
        """Test boolean conversion."""
        assert not Spacing(0, 0, 0, 0)
        assert Spacing(1, 0, 0, 0)
        assert Spacing(0, 1, 0, 0)
        assert Spacing(0, 0, 1, 0)
        assert Spacing(0, 0, 0, 1)

    def test_width(self):
        """Test width property."""
        assert Spacing(1, 2, 3, 4).width == 6  # left + right

    def test_height(self):
        """Test height property."""
        assert Spacing(1, 2, 3, 4).height == 4  # top + bottom

    def test_max_width(self):
        """Test max_width property."""
        assert Spacing(1, 2, 3, 4).max_width == 4  # max(left, right)
        assert Spacing(1, 5, 3, 2).max_width == 5

    def test_max_height(self):
        """Test max_height property."""
        assert Spacing(1, 2, 3, 4).max_height == 3  # max(top, bottom)
        assert Spacing(5, 2, 3, 4).max_height == 5

    def test_css_property(self):
        """Test css property."""
        assert Spacing(5, 5, 5, 5).css == "5"
        assert Spacing(5, 10, 5, 10).css == "5 10"
        assert Spacing(1, 2, 3, 4).css == "1 2 3 4"

    def test_unpack_single_value(self):
        """Test unpack with single value."""
        assert Spacing.unpack(5) == Spacing(5, 5, 5, 5)

    def test_unpack_tuple_one(self):
        """Test unpack with tuple of 1."""
        assert Spacing.unpack((5,)) == Spacing(5, 5, 5, 5)

    def test_unpack_tuple_two(self):
        """Test unpack with tuple of 2."""
        assert Spacing.unpack((5, 10)) == Spacing(5, 10, 5, 10)

    def test_unpack_tuple_four(self):
        """Test unpack with tuple of 4."""
        assert Spacing.unpack((1, 2, 3, 4)) == Spacing(1, 2, 3, 4)

    def test_unpack_invalid(self):
        """Test unpack with invalid input."""
        with pytest.raises(ValueError):
            Spacing.unpack((1, 2, 3))  # 3 values not allowed

    def test_vertical(self):
        """Test vertical class method."""
        assert Spacing.vertical(5) == Spacing(5, 0, 5, 0)

    def test_horizontal(self):
        """Test horizontal class method."""
        assert Spacing.horizontal(5) == Spacing(0, 5, 0, 5)

    def test_all_method(self):
        """Test all class method."""
        assert Spacing.all(5) == Spacing(5, 5, 5, 5)

    def test_spacing_addition(self):
        """Test spacing addition."""
        s1 = Spacing(1, 2, 3, 4)
        s2 = Spacing(5, 6, 7, 8)
        assert s1 + s2 == Spacing(6, 8, 10, 12)

    def test_spacing_subtraction(self):
        """Test spacing subtraction."""
        s1 = Spacing(10, 10, 10, 10)
        s2 = Spacing(1, 2, 3, 4)
        assert s1 - s2 == Spacing(9, 8, 7, 6)

    def test_grow_maximum(self):
        """Test grow_maximum method."""
        s1 = Spacing(5, 10, 15, 20)
        s2 = Spacing(10, 5, 20, 15)
        result = s1.grow_maximum(s2)
        assert result == Spacing(10, 10, 20, 20)
