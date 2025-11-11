"""Unit tests for social template relative layouts."""

import pytest

from agency_toolkit.models import SocialTemplate


class TestSocialTemplateRelativeLayouts:
    """Tests for SocialTemplate responsive layout calculations."""

    def test_font_size_ratio_calculation_standard(self):
        """Verify font size calculated from ratio (standard case)."""
        template = SocialTemplate(
            font_face="Arial",
            font_size_ratio=0.08,
            text_fill="#000000",
            background_type="solid",
        )

        # For 1080px height: 0.08 * 1080 = 86.4 ≈ 86
        assert template.calculate_font_size(1080) == 86

    def test_font_size_ratio_calculation_small_image(self):
        """Verify font size respects minimum even with small images."""
        template = SocialTemplate(
            font_face="Arial",
            font_size_ratio=0.05,
            text_fill="#000000",
            background_type="solid",
        )

        # For small height: 0.05 * 100 = 5, but min is 12
        assert template.calculate_font_size(100) == 12

    def test_font_size_ratio_calculation_large_image(self):
        """Verify font size scales for large images."""
        template = SocialTemplate(
            font_face="Arial",
            font_size_ratio=0.08,
            text_fill="#000000",
            background_type="solid",
        )

        # For 2160px height: 0.08 * 2160 = 172.8 ≈ 172
        assert template.calculate_font_size(2160) == 172

    def test_legacy_font_size_still_works(self):
        """Verify old fixed font_size still works (backward compat)."""
        template = SocialTemplate(
            font_face="Arial",
            font_size=48,
            text_fill="#000000",
            background_type="solid",
        )

        # Should use fixed font_size if font_size_ratio not provided
        assert template.calculate_font_size(1080) == 48

    def test_font_size_ratio_takes_precedence(self):
        """Verify font_size_ratio takes precedence over font_size."""
        template = SocialTemplate(
            font_face="Arial",
            font_size=48,
            font_size_ratio=0.08,
            text_fill="#000000",
            background_type="solid",
        )

        # Should use ratio, not fixed size
        assert template.calculate_font_size(1080) == 86

    def test_padding_calculation(self):
        """Verify padding calculated from ratio."""
        template = SocialTemplate(
            font_face="Arial",
            padding_ratio=0.1,
            text_fill="#000000",
            background_type="solid",
        )

        # For 1920x1080: 10% padding = 192 horizontal, 108 vertical
        h_pad, v_pad = template.calculate_padding(1920, 1080)
        assert h_pad == 192
        assert v_pad == 108

    def test_padding_calculation_different_ratios(self):
        """Verify padding with different ratio values."""
        template = SocialTemplate(
            font_face="Arial",
            padding_ratio=0.15,
            text_fill="#000000",
            background_type="solid",
        )

        # For 1000x1000: 15% padding = 150 both
        h_pad, v_pad = template.calculate_padding(1000, 1000)
        assert h_pad == 150
        assert v_pad == 150

    def test_text_position_center(self):
        """Verify text position when centered."""
        template = SocialTemplate(
            font_face="Arial",
            padding_ratio=0.1,
            text_x_ratio=0.5,
            text_y_ratio=0.5,
            h_align="center",
            v_align="middle",
            text_fill="#000000",
            background_type="solid",
        )

        # Image: 1920x1080, Text: 400x100
        x, y = template.calculate_text_position(1920, 1080, 400, 100)

        # Center: (1920 - 400) / 2 = 760
        assert x == 760
        # Middle: (1080 - 100) / 2 = 490
        assert y == 490

    def test_text_position_left_top(self):
        """Verify text position when top-left aligned."""
        template = SocialTemplate(
            font_face="Arial",
            padding_ratio=0.1,
            text_x_ratio=0.0,  # Not used for left align
            text_y_ratio=0.0,  # Not used for top align
            h_align="left",
            v_align="top",
            text_fill="#000000",
            background_type="solid",
        )

        # Image: 1920x1080, Text: 400x100
        x, y = template.calculate_text_position(1920, 1080, 400, 100)

        # Left: padding = 192 (10% of 1920)
        assert x == 192
        # Top: padding = 108 (10% of 1080)
        assert y == 108

    def test_text_position_right_bottom(self):
        """Verify text position when bottom-right aligned."""
        template = SocialTemplate(
            font_face="Arial",
            padding_ratio=0.1,
            h_align="right",
            v_align="bottom",
            text_fill="#000000",
            background_type="solid",
        )

        # Image: 1920x1080, Text: 400x100
        x, y = template.calculate_text_position(1920, 1080, 400, 100)

        # Right: width - text_width - padding = 1920 - 400 - 192 = 1328
        assert x == 1328
        # Bottom: height - text_height - padding = 1080 - 100 - 108 = 872
        assert y == 872

    def test_text_position_respects_padding_bounds(self):
        """Verify text position respects minimum padding."""
        template = SocialTemplate(
            font_face="Arial",
            padding_ratio=0.5,  # Very large padding
            h_align="center",
            v_align="middle",
            text_fill="#000000",
            background_type="solid",
        )

        # Image: 1000x1000, Text: 200x200
        x, y = template.calculate_text_position(1000, 1000, 200, 200)

        # Even with large padding, should not go below padding minimum
        assert x >= 500  # At least padding on left
        assert y >= 500  # At least padding on top

    def test_template_modern_ratios(self):
        """Verify modern template has reasonable ratios."""
        template = SocialTemplate(
            font_face="Roboto-Bold",
            font_size_ratio=0.08,
            text_x_ratio=0.5,
            text_y_ratio=0.5,
            padding_ratio=0.12,
            h_align="center",
            v_align="middle",
            line_spacing_ratio=1.3,
            text_fill="#FFFFFF",
            text_stroke=True,
            text_stroke_width=2,
            background_type="gradient",
            gradient_colors=["#2E5EAA", "#1A3A6E"],
            max_chars_per_line=25,
        )

        # Verify calculations work
        font_size = template.calculate_font_size(1080)
        assert font_size > 50  # Should be reasonably large
        assert font_size < 150  # But not huge

        h_pad, v_pad = template.calculate_padding(1080, 1080)
        assert h_pad == v_pad == 129  # 12% of 1080

    def test_template_minimal_ratios(self):
        """Verify minimal template has reasonable ratios."""
        template = SocialTemplate(
            font_face="Roboto-Bold",
            font_size_ratio=0.06,
            text_x_ratio=0.5,
            text_y_ratio=0.5,
            padding_ratio=0.15,
            h_align="center",
            v_align="middle",
            line_spacing_ratio=1.4,
            text_fill="#000000",
            text_stroke=False,
            background_type="solid",
            background_color="#FFFFFF",
        )

        # Verify calculations work
        font_size = template.calculate_font_size(1080)
        assert font_size > 40  # Smaller than modern
        assert font_size < 100

        h_pad, v_pad = template.calculate_padding(1080, 1080)
        assert h_pad == v_pad == 162  # 15% of 1080

    def test_line_spacing_ratio_validation(self):
        """Verify line_spacing_ratio is validated."""
        # Valid: between 0.8 and 2.0
        template = SocialTemplate(
            font_face="Arial",
            line_spacing_ratio=1.2,
            text_fill="#000000",
            background_type="solid",
        )
        assert template.line_spacing_ratio == 1.2

    def test_invalid_line_spacing_ratio_too_low(self):
        """Verify line_spacing_ratio below 0.8 is rejected."""
        with pytest.raises(ValueError):
            SocialTemplate(
                font_face="Arial",
                line_spacing_ratio=0.5,
                text_fill="#000000",
                background_type="solid",
            )

    def test_invalid_line_spacing_ratio_too_high(self):
        """Verify line_spacing_ratio above 2.0 is rejected."""
        with pytest.raises(ValueError):
            SocialTemplate(
                font_face="Arial",
                line_spacing_ratio=2.5,
                text_fill="#000000",
                background_type="solid",
            )

    def test_gradient_template_requires_colors(self):
        """Verify gradient background requires colors."""
        with pytest.raises(ValueError, match="gradient_colors required"):
            SocialTemplate(
                font_face="Arial",
                text_fill="#000000",
                background_type="gradient",
                gradient_colors=None,
            )

    def test_solid_template_optional_colors(self):
        """Verify solid background doesn't require gradient_colors."""
        template = SocialTemplate(
            font_face="Arial",
            text_fill="#000000",
            background_type="solid",
            background_color="#FFFFFF",
        )
        assert template.background_type == "solid"
        assert template.gradient_colors is None
