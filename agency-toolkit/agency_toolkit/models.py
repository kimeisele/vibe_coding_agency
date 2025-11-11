"""Pydantic validation models for agency toolkit.

All validation logic is centralized here to fail fast with clear errors.
"""

from datetime import date
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agency_toolkit.constants import (
    DEFAULT_IMAGE_HEIGHT,
    DEFAULT_IMAGE_WIDTH,
    DEFAULT_MISTRAL_MAX_TOKENS,
    DEFAULT_MISTRAL_MODEL,
    DEFAULT_MISTRAL_TEMPERATURE,
    MAX_MISTRAL_TOKENS_LIMIT,
    MAX_TEMPERATURE,
    MIN_TEMPERATURE,
)


class ImageGenerationConfig(BaseModel):
    """Image generation configuration model."""

    model_config = ConfigDict(extra="forbid")

    provider: str = Field(default="pollinations")  # FREE default!
    replicate_model: str = Field(
        default="stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf"
    )
    default_width: int = Field(default=DEFAULT_IMAGE_WIDTH, gt=0)
    default_height: int = Field(default=DEFAULT_IMAGE_HEIGHT, gt=0)
    enable_cost_tracking: bool = Field(default=True)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider is supported."""
        supported_providers = ["replicate", "pollinations"]
        if v not in supported_providers:
            raise ValueError(
                f"Unsupported provider '{v}'. "
                f"Supported: {', '.join(supported_providers)}"
            )
        return v


class Config(BaseModel):
    """Application configuration model."""

    output_dir: Path = Field(default=Path("./output"))
    social_style: str = Field(default="modern")
    social_color: str = Field(default="blue")
    social_format: str = Field(default="square")
    briefing_type: str = Field(default="default")
    mistral_model: str = Field(default=DEFAULT_MISTRAL_MODEL)
    mistral_temperature: float = Field(
        default=DEFAULT_MISTRAL_TEMPERATURE, ge=MIN_TEMPERATURE, le=MAX_TEMPERATURE
    )
    mistral_max_tokens: int = Field(default=DEFAULT_MISTRAL_MAX_TOKENS, gt=0)
    json_output: bool = Field(default=False)
    image: ImageGenerationConfig = Field(default_factory=ImageGenerationConfig)

    @field_validator("social_style")
    @classmethod
    def validate_social_style(cls, v: str) -> str:
        """Validate social media style."""
        valid_styles = ["modern", "minimal", "bold"]
        if v not in valid_styles:
            raise ValueError(
                f"Invalid social_style: {v}. Valid options: {', '.join(valid_styles)}"
            )
        return v

    @field_validator("social_format")
    @classmethod
    def validate_social_format(cls, v: str) -> str:
        """Validate social media format."""
        valid_formats = ["square", "story", "landscape"]
        if v not in valid_formats:
            raise ValueError(
                f"Invalid social_format: {v}. Valid options: {', '.join(valid_formats)}"
            )
        return v


class SocialTemplate(BaseModel):
    """Social media template validation model (v5.0) - Relative Layouts.

    Supports both legacy fixed sizing and new relative sizing for responsive layouts.
    """

    # Font configuration
    font_face: str
    font_size: int | None = Field(default=None, gt=0)  # DEPRECATED: use font_size_ratio
    font_size_ratio: float | None = Field(
        default=None, ge=0.01, le=0.5
    )  # 0.06 = 6% of image height

    # Text positioning (supports both legacy and new)
    text_position_xy: tuple[int, int] | None = Field(
        default=None
    )  # DEPRECATED: use text_x_ratio/text_y_ratio
    text_x_ratio: float = Field(default=0.5, ge=0.0, le=1.0)  # 0.5 = center
    text_y_ratio: float = Field(default=0.5, ge=0.0, le=1.0)  # 0.5 = center

    # Padding for margins
    padding_ratio: float = Field(default=0.1, ge=0.0, le=0.5)  # 0.1 = 10% margin

    # Text styling
    text_fill: str
    text_stroke: bool = Field(default=False)
    text_stroke_width: int = Field(default=2, ge=0)

    # Line spacing
    line_spacing_ratio: float = Field(default=1.2, ge=0.8, le=2.0)

    # Layout alignment
    v_align: str = Field(default="middle")  # 'top', 'middle', 'bottom'
    h_align: str = Field(default="center")  # 'left', 'center', 'right'

    # Background
    background_type: str
    background_color: str | None = None
    gradient_colors: list[str] | None = None

    # Text wrapping
    max_chars_per_line: int | None = None

    @field_validator("background_type")
    @classmethod
    def validate_background_type(cls, v: str) -> str:
        """Validate background type."""
        valid_types = ["gradient", "solid"]
        if v not in valid_types:
            raise ValueError(
                f"Invalid background_type: {v}. Valid options: {', '.join(valid_types)}"
            )
        return v

    @field_validator("gradient_colors")
    @classmethod
    def validate_gradient_colors(
        cls, v: list[str] | None, info: Any
    ) -> list[str] | None:
        """Validate gradient colors if background_type is gradient."""
        if info.data.get("background_type") == "gradient" and not v:
            raise ValueError("gradient_colors required when background_type='gradient'")
        return v

    @field_validator("v_align")
    @classmethod
    def validate_v_align(cls, v: str) -> str:
        """Validate vertical alignment."""
        valid_aligns = ["top", "middle", "bottom"]
        if v not in valid_aligns:
            raise ValueError(
                f"Invalid v_align: {v}. Valid options: {', '.join(valid_aligns)}"
            )
        return v

    @field_validator("h_align")
    @classmethod
    def validate_h_align(cls, v: str) -> str:
        """Validate horizontal alignment."""
        valid_aligns = ["left", "center", "right"]
        if v not in valid_aligns:
            raise ValueError(
                f"Invalid h_align: {v}. Valid options: {', '.join(valid_aligns)}"
            )
        return v

    # Helper methods for responsive layout calculations
    def calculate_font_size(self, image_height: int) -> int:
        """Calculate actual font size from ratio or fallback to fixed size.

        Args:
            image_height: Image height in pixels

        Returns:
            Actual font size in points
        """
        if self.font_size_ratio is not None:
            return max(12, int(image_height * self.font_size_ratio))
        elif self.font_size is not None:
            return self.font_size
        else:
            # Fallback: 5% of image height
            return max(12, int(image_height * 0.05))

    def calculate_padding(self, image_width: int, image_height: int) -> tuple[int, int]:
        """Calculate actual padding from ratio.

        Args:
            image_width: Image width in pixels
            image_height: Image height in pixels

        Returns:
            Tuple of (horizontal_padding, vertical_padding) in pixels
        """
        return (
            int(image_width * self.padding_ratio),
            int(image_height * self.padding_ratio),
        )

    def calculate_text_position(
        self, image_width: int, image_height: int, text_width: int, text_height: int
    ) -> tuple[int, int]:
        """Calculate text position based on alignment and ratio.

        Args:
            image_width: Image width in pixels
            image_height: Image height in pixels
            text_width: Rendered text width in pixels
            text_height: Rendered text height in pixels

        Returns:
            Tuple of (x, y) position for text
        """
        h_pad, v_pad = self.calculate_padding(image_width, image_height)

        # Horizontal position
        if self.h_align == "left":
            x = h_pad
        elif self.h_align == "right":
            x = max(h_pad, image_width - text_width - h_pad)
        else:  # center
            x = max(h_pad, (image_width - text_width) // 2)

        # Vertical position
        if self.v_align == "top":
            y = v_pad
        elif self.v_align == "bottom":
            y = max(v_pad, image_height - text_height - v_pad)
        else:  # middle
            y = max(v_pad, (image_height - text_height) // 2)

        return (x, y)


class BriefingData(BaseModel):
    """Project briefing data validation model."""

    client_name: str = Field(min_length=1)
    project_name: str = Field(min_length=1)
    project_type: str
    deadline: date
    budget: float | None = Field(default=None, gt=0)
    objectives: str | None = None
    target_audience: str | None = None
    deliverables: list[str] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v: str) -> str:
        """Validate project type."""
        valid_types = ["Print", "Web", "Social", "Video", "Other"]
        if v not in valid_types:
            raise ValueError(
                f"Invalid project_type: {v}. Valid options: {', '.join(valid_types)}"
            )
        return v

    @field_validator("deliverables")
    @classmethod
    def filter_empty_deliverables(cls, v: list[str]) -> list[str]:
        """Remove empty strings from deliverables."""
        return [d.strip() for d in v if d.strip()]


class MistralConfig(BaseModel):
    """Mistral API configuration model."""

    model: str = Field(default=DEFAULT_MISTRAL_MODEL)
    temperature: float = Field(
        default=DEFAULT_MISTRAL_TEMPERATURE, ge=MIN_TEMPERATURE, le=MAX_TEMPERATURE
    )
    max_tokens: int = Field(
        default=DEFAULT_MISTRAL_MAX_TOKENS, gt=0, le=MAX_MISTRAL_TOKENS_LIMIT
    )
    json_output: bool = Field(default=False)

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate Mistral model name."""
        valid_models = [
            "mistral-tiny",
            "mistral-small-latest",
            "mistral-medium",
            "mistral-large-latest",
        ]
        if v not in valid_models:
            raise ValueError(
                f"Invalid model: {v}. Valid options: {', '.join(valid_models)}"
            )
        return v
