"""Default configuration constants for Agency Toolkit."""

from pathlib import Path

# Output
OUTPUT_DIR = Path("./output")

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = OUTPUT_DIR / "toolkit.log"

# Social Media
SOCIAL_STYLE = "modern"
SOCIAL_COLOR = "blue"
SOCIAL_FORMAT = "square"

# Social Styles
SOCIAL_STYLES = {
    "modern": "Clean, tech-forward, gradient background",
    "bold": "High-impact, solid color, large font",
    "minimal": "Whitespace, small font, elegant",
}

# Colors
COLORS = {
    "blue": "#2E5EAA",
    "red": "#D32F2F",
    "green": "#43A047",
    "purple": "#8E24AA",
}

# Image Formats (width, height)
FORMATS = {
    "square": (1080, 1080),
    "story": (1080, 1920),
    "landscape": (1200, 630),
}

# Paths
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
SOCIAL_TEMPLATES_DIR = TEMPLATES_DIR / "social"
BRIEFING_TEMPLATES_DIR = TEMPLATES_DIR / "briefing"
STRUCTURE_TEMPLATES_DIR = TEMPLATES_DIR / "folders"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# Mistral Profiles (v4.0)
# These are default profiles. Users can override in ~/.config/agency-toolkit/config.toml
MISTRAL_PROFILES = {
    "default": {
        "model": "mistral-medium",
        "temperature": 0.7,
        "system_prompt": "You are a helpful AI assistant for creative professionals. Provide clear, actionable answers. When asked for options, provide 3-5 varied suggestions. Be concise but thorough.",  # noqa: E501
    },
    "code": {
        "model": "mistral-small-latest",
        "temperature": 0.2,
        "system_prompt": "You are an expert software engineer and code reviewer. Analyze code for bugs, performance issues, security vulnerabilities, and adherence to best practices (DRY, SOLID, clean code). Provide specific, actionable feedback with examples. When suggesting fixes, explain WHY the change improves the code.",  # noqa: E501
    },
    "creative": {
        "model": "mistral-medium",
        "temperature": 0.85,
        "system_prompt": "You are a creative director and copywriter with expertise in advertising, branding, and social media. Generate multiple creative options (headlines, taglines, post ideas) that are bold, memorable, and on-brand. Consider tone, audience, and platform. Explain the thinking behind each option.",  # noqa: E501
    },
    "strategy": {
        "model": "mistral-large-latest",
        "temperature": 0.6,
        "system_prompt": "You are a senior marketing strategist and business consultant. Analyze situations holistically, consider multiple stakeholders, identify risks and opportunities. Provide strategic recommendations with clear reasoning. Think about short-term tactics AND long-term positioning.",  # noqa: E501
    },
    "client": {
        "model": "mistral-medium",
        "temperature": 0.5,
        "system_prompt": "You are a senior account manager with 10+ years of client relationship experience. Draft professional, empathetic, and clear client communications. Always: acknowledge their concern, provide transparent updates, set realistic expectations, and propose next steps. Use a warm but professional tone.",  # noqa: E501
    },
    "technical": {
        "model": "mistral-large-latest",
        "temperature": 0.3,
        "system_prompt": "You are a technical writer and developer advocate. Explain complex technical concepts clearly to both technical and non-technical audiences. Use analogies, examples, and step-by-step breakdowns. Assume the reader is intelligent but may not have domain expertise.",  # noqa: E501
    },
}
