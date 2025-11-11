"""Global constants for Agency Toolkit.

Module-specific constants should be in their respective modules.
This file contains only truly global constants.
"""

# Image generation defaults (used across multiple modules)
DEFAULT_IMAGE_WIDTH = 1024
DEFAULT_IMAGE_HEIGHT = 1024

# API defaults
DEFAULT_MISTRAL_MODEL = "mistral-small-latest"
DEFAULT_MISTRAL_TEMPERATURE = 0.7
DEFAULT_MISTRAL_MAX_TOKENS = 1000

# Limits
MAX_MISTRAL_TOKENS_LIMIT = 100000

# Common validation
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 1.0
