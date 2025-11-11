"""Custom exception classes for Agency Toolkit."""


class TemplateNotFoundError(FileNotFoundError):
    """Raised when a template file cannot be found."""

    pass


class TemplateValidationError(ValueError):
    """Raised when template fails JSON Schema validation."""

    pass


class ConfigurationError(ValueError):
    """Raised when configuration has invalid values."""

    pass


class OutputPathError(OSError):
    """Raised when output directory creation fails."""

    pass


class ImageProviderError(RuntimeError):
    """Raised when image generation provider fails."""

    pass


class MistralAPIError(RuntimeError):
    """Raised when Mistral API call fails."""

    pass


class AIProviderError(RuntimeError):
    """Raised when AI provider call fails."""

    pass


class RenderingError(RuntimeError):
    """Raised when image rendering fails."""

    pass


class ValidationError(ValueError):
    """Raised when data validation fails."""

    pass
