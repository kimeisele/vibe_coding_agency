"""Test configuration and fixtures."""

import pytest

from agency_toolkit.models import Config


@pytest.fixture
def tmp_output_dir(tmp_path) -> None:
    """Provide temporary output directory."""
    return tmp_path / "output"


@pytest.fixture
def mock_config(tmp_output_dir) -> None:
    """Provide mock configuration."""
    return Config(
        output_dir=tmp_output_dir,
        social_style="modern",
        social_color="blue",
    )


@pytest.fixture
def sample_social_text() -> None:
    """Provide sample social media text."""
    return "Hello World! Check out our amazing work 🚀"


@pytest.fixture
def sample_briefing_data() -> None:
    """Provide sample briefing data."""
    from datetime import date

    from agency_toolkit.core.briefing import BriefingData

    return BriefingData(
        client_name="Acme Corp",
        project_name="Website Redesign",
        project_type="Web",
        deadline=date(2024, 12, 31),
        budget=5000.0,
        objectives="Modernize digital presence",
        target_audience="B2B decision makers",
        deliverables=["Homepage", "Blog", "Contact page"],
        notes="Prefer modern design with dark theme",
    )
