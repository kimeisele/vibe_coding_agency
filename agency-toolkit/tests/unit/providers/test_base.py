"""Unit tests for base ImageProvider class."""

import pytest

from agency_toolkit.providers.base import ImageProvider


class ConcreteProvider(ImageProvider):
    """Concrete implementation for testing."""

    def generate(self, prompt, seed, width, height, config):
        """Mock generate method."""
        return {
            "path": "/fake/path.png",
            "cost": 0.001,
            "seed": seed,
            "model": "test",
            "provider": "test",
        }

    def estimate_cost(self):
        """Mock cost estimation."""
        return 0.001

    def supports_seed(self):
        """Mock seed support."""
        return True

    def max_dimensions(self):
        """Mock max dimensions."""
        return (1024, 1024)


class TestImageProviderAbstractClass:
    """Test ImageProvider abstract base class."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Should not be able to instantiate ImageProvider directly."""
        with pytest.raises(TypeError):
            ImageProvider()

    def test_concrete_subclass_can_be_instantiated(self) -> None:
        """Should be able to instantiate concrete subclass."""
        provider = ConcreteProvider()
        assert isinstance(provider, ImageProvider)


class TestImageProviderValidateDimensions:
    """Test ImageProvider.validate_dimensions() method."""

    @pytest.fixture
    def provider(self) -> ImageProvider:
        """Provide concrete provider instance."""
        return ConcreteProvider()

    def test_validate_dimensions_accepts_valid_width_height(
        self, provider: ImageProvider
    ) -> None:
        """Should accept dimensions within limits."""
        # Should not raise
        provider.validate_dimensions(512, 512)
        provider.validate_dimensions(1024, 1024)
        provider.validate_dimensions(100, 1024)
        provider.validate_dimensions(1024, 100)

    def test_validate_dimensions_rejects_width_exceeding_limit(
        self, provider: ImageProvider
    ) -> None:
        """Should reject width exceeding provider limit."""
        with pytest.raises(ValueError, match="exceed provider limit"):
            provider.validate_dimensions(2048, 512)

    def test_validate_dimensions_rejects_height_exceeding_limit(
        self, provider: ImageProvider
    ) -> None:
        """Should reject height exceeding provider limit."""
        with pytest.raises(ValueError, match="exceed provider limit"):
            provider.validate_dimensions(512, 2048)

    def test_validate_dimensions_rejects_both_exceeding_limit(
        self, provider: ImageProvider
    ) -> None:
        """Should reject both width and height exceeding limit."""
        with pytest.raises(ValueError, match="exceed provider limit"):
            provider.validate_dimensions(2048, 2048)

    def test_validate_dimensions_error_includes_limits(
        self, provider: ImageProvider
    ) -> None:
        """Error message should include provider limits."""
        with pytest.raises(ValueError) as exc_info:
            provider.validate_dimensions(2048, 512)

        error_msg = str(exc_info.value)
        assert "2048x512" in error_msg
        assert "1024x1024" in error_msg

    def test_validate_dimensions_at_boundary(self, provider: ImageProvider) -> None:
        """Should accept dimensions exactly at limit."""
        # Should not raise - at maximum limit
        provider.validate_dimensions(1024, 1024)


class TestImageProviderAbstractMethods:
    """Test that all abstract methods must be implemented."""

    def test_generate_is_abstract(self) -> None:
        """generate() must be implemented by subclass."""

        class IncompleteProvider1(ImageProvider):
            def estimate_cost(self):
                return 0.0

            def supports_seed(self):
                return True

            def max_dimensions(self):
                return (1024, 1024)

        # Should not be able to instantiate without implement generate
        with pytest.raises(TypeError):
            IncompleteProvider1()

    def test_estimate_cost_is_abstract(self) -> None:
        """estimate_cost() must be implemented by subclass."""

        class IncompleteProvider2(ImageProvider):
            def generate(self, prompt, seed, width, height, config):
                return {}

            def supports_seed(self):
                return True

            def max_dimensions(self):
                return (1024, 1024)

        # Should not be able to instantiate without implement estimate_cost
        with pytest.raises(TypeError):
            IncompleteProvider2()

    def test_supports_seed_is_abstract(self) -> None:
        """supports_seed() must be implemented by subclass."""

        class IncompleteProvider3(ImageProvider):
            def generate(self, prompt, seed, width, height, config):
                return {}

            def estimate_cost(self):
                return 0.0

            def max_dimensions(self):
                return (1024, 1024)

        # Should not be able to instantiate without implement supports_seed
        with pytest.raises(TypeError):
            IncompleteProvider3()

    def test_max_dimensions_is_abstract(self) -> None:
        """max_dimensions() must be implemented by subclass."""

        class IncompleteProvider4(ImageProvider):
            def generate(self, prompt, seed, width, height, config):
                return {}

            def estimate_cost(self):
                return 0.0

            def supports_seed(self):
                return True

        # Should not be able to instantiate without implement max_dimensions
        with pytest.raises(TypeError):
            IncompleteProvider4()


class TestImageProviderInterfaceContract:
    """Test that concrete implementations honor interface contract."""

    @pytest.fixture
    def provider(self) -> ImageProvider:
        """Provide concrete provider instance."""
        return ConcreteProvider()

    def test_estimate_cost_returns_float(self, provider: ImageProvider) -> None:
        """estimate_cost() should return float."""
        cost = provider.estimate_cost()
        assert isinstance(cost, float)

    def test_supports_seed_returns_bool(self, provider: ImageProvider) -> None:
        """supports_seed() should return bool."""
        supports = provider.supports_seed()
        assert isinstance(supports, bool)

    def test_max_dimensions_returns_tuple(self, provider: ImageProvider) -> None:
        """max_dimensions() should return tuple."""
        dims = provider.max_dimensions()
        assert isinstance(dims, tuple)
        assert len(dims) == 2
        assert all(isinstance(d, int) for d in dims)
