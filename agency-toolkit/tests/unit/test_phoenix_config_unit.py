"""Unit tests for Phoenix Configuration System."""

import os
from unittest.mock import patch

import pytest

from agency_toolkit.core.phoenix_config.config_classes import (
    APIConfig,
    CacheConfig,
    DatabaseConfig,
    LoggingConfig,
    PerformanceConfig,
    SecurityConfig,
    ShellConfig,
    TaskConfig,
)
from agency_toolkit.core.phoenix_config.core import UniversalConfig
from agency_toolkit.core.phoenix_config.validators import ConfigurationError


class TestUniversalConfigDefaults:
    """Test UniversalConfig default values and initialization."""

    def test_default_config_initializes(self):
        """Test that default config can be instantiated."""
        config = UniversalConfig()

        assert config.environment == "production"
        assert config.database is not None
        assert config.api is not None
        assert config.shell is not None
        assert config.logging is not None

    def test_default_config_has_all_components(self):
        """Test that default config has all major components."""
        config = UniversalConfig()

        assert hasattr(config, "database")
        assert hasattr(config, "api")
        assert hasattr(config, "shell")
        assert hasattr(config, "logging")
        assert hasattr(config, "security")
        assert hasattr(config, "performance")
        assert hasattr(config, "cache")
        assert hasattr(config, "task")

    def test_config_validates_on_init(self):
        """Test that config validates on initialization."""
        with pytest.raises(ConfigurationError):
            # Invalid environment
            UniversalConfig(environment="invalid_env")

    def test_config_validates_shell_timeout(self):
        """Test that shell timeout must be positive."""
        with pytest.raises(ConfigurationError):
            UniversalConfig(shell=ShellConfig(timeout=-1))

    def test_config_validates_cache_settings(self):
        """Test that cache settings validate correctly."""
        with pytest.raises(ConfigurationError):
            UniversalConfig(cache=CacheConfig(ttl_seconds=-1))


class TestDatabaseConfig:
    """Test DatabaseConfig functionality."""

    def test_database_config_defaults(self):
        """Test DatabaseConfig default values."""
        db = DatabaseConfig()

        assert db.url is not None
        assert db.echo is False
        assert db.pool_size > 0
        assert db.max_overflow > 0

    def test_database_config_custom_values(self):
        """Test DatabaseConfig with custom values."""
        db = DatabaseConfig(
            url="sqlite:///test.db", echo=True, pool_size=10, max_overflow=20
        )

        assert db.url == "sqlite:///test.db"
        assert db.echo is True
        assert db.pool_size == 10
        assert db.max_overflow == 20


class TestAPIConfig:
    """Test APIConfig functionality."""

    def test_api_config_defaults(self):
        """Test APIConfig default values."""
        api = APIConfig()

        assert api.host == "localhost"
        assert api.port == 8000
        assert api.debug is False
        assert api.workers > 0

    def test_api_config_custom_values(self):
        """Test APIConfig with custom values."""
        api = APIConfig(host="0.0.0.0", port=9000, debug=True, workers=4)

        assert api.host == "0.0.0.0"
        assert api.port == 9000
        assert api.debug is True
        assert api.workers == 4


class TestShellConfig:
    """Test ShellConfig functionality."""

    def test_shell_config_defaults(self):
        """Test ShellConfig default values."""
        shell = ShellConfig()

        assert shell.timeout > 0
        assert shell.max_output_lines > 0
        assert shell.max_retries >= 0

    def test_shell_config_custom_values(self):
        """Test ShellConfig with custom values."""
        shell = ShellConfig(timeout=120, max_output_lines=2000, max_retries=5)

        assert shell.timeout == 120
        assert shell.max_output_lines == 2000
        assert shell.max_retries == 5


class TestLoggingConfig:
    """Test LoggingConfig functionality."""

    def test_logging_config_defaults(self):
        """Test LoggingConfig default values."""
        logging = LoggingConfig()

        assert logging.level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_logging_config_custom_values(self):
        """Test LoggingConfig with custom values."""
        logging = LoggingConfig(level="DEBUG", format="json", log_file="/tmp/test.log")

        assert logging.level == "DEBUG"
        assert logging.format == "json"
        assert logging.log_file == "/tmp/test.log"


class TestSecurityConfig:
    """Test SecurityConfig functionality."""

    def test_security_config_defaults(self):
        """Test SecurityConfig default values."""
        security = SecurityConfig()

        assert isinstance(security.enable_session_persistence, bool)
        assert security.audit_log_retention_days > 0

    def test_security_config_custom_values(self):
        """Test SecurityConfig with custom values."""
        security = SecurityConfig(
            enable_session_persistence=False, audit_log_retention_days=180
        )

        assert security.enable_session_persistence is False
        assert security.audit_log_retention_days == 180


class TestPerformanceConfig:
    """Test PerformanceConfig functionality."""

    def test_performance_config_defaults(self):
        """Test PerformanceConfig default values."""
        perf = PerformanceConfig()

        assert isinstance(perf.enable_caching, bool)
        assert perf.max_concurrent_operations > 0

    def test_performance_config_custom_values(self):
        """Test PerformanceConfig with custom values."""
        perf = PerformanceConfig(enable_caching=False, max_concurrent_operations=20)

        assert perf.enable_caching is False
        assert perf.max_concurrent_operations == 20


class TestCacheConfig:
    """Test CacheConfig functionality."""

    def test_cache_config_defaults(self):
        """Test CacheConfig default values."""
        cache = CacheConfig()

        assert cache.backend in ["memory", "redis", "memcached"]
        assert cache.ttl_seconds > 0
        assert cache.max_size > 0

    def test_cache_config_custom_values(self):
        """Test CacheConfig with custom values."""
        cache = CacheConfig(
            backend="redis",
            ttl_seconds=600,
            max_size=5000,
            url="redis://localhost:6379",
        )

        assert cache.backend == "redis"
        assert cache.ttl_seconds == 600
        assert cache.max_size == 5000
        assert cache.url == "redis://localhost:6379"


class TestTaskConfig:
    """Test TaskConfig functionality."""

    def test_task_config_defaults(self):
        """Test TaskConfig default values."""
        task = TaskConfig()

        assert task.max_workers > 0
        assert task.queue_size > 0
        assert task.retry_attempts >= 0

    def test_task_config_custom_values(self):
        """Test TaskConfig with custom values."""
        task = TaskConfig(max_workers=8, queue_size=2000, retry_attempts=5)

        assert task.max_workers == 8
        assert task.queue_size == 2000
        assert task.retry_attempts == 5


class TestEnvironmentVariables:
    """Test configuration from environment variables."""

    def test_environment_variable_defaults(self):
        """Test that missing env vars use defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = UniversalConfig.create_default()

            assert config.environment == "production"
            assert config.api.port == 8000
            assert config.logging.level == "INFO"

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        from agency_toolkit.core.phoenix_config.loaders import ConfigLoader

        env_vars = {
            "APP_ENV": "development",
            "API_PORT": "3000",
            "LOG_LEVEL": "DEBUG",
            "DATABASE_URL": "sqlite:///test.db",
            "API_HOST": "localhost",
        }
        with patch.dict(os.environ, env_vars):
            config = ConfigLoader.from_env()

            assert config.environment == "development"
            assert config.api.port == 3000
            assert config.logging.level == "DEBUG"

    def test_database_url_from_env(self):
        """Test database URL from environment."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://localhost/testdb"}):
            config = UniversalConfig.create_default()

            assert config.database.url == "postgresql://localhost/testdb"


class TestConfigValidation:
    """Test configuration validation."""

    def test_invalid_environment_raises_error(self):
        """Test that invalid environment raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            UniversalConfig(environment="staging")

    def test_negative_timeout_raises_error(self):
        """Test that negative timeout raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            UniversalConfig(shell=ShellConfig(timeout=-1))

    def test_zero_workers_raises_error(self):
        """Test that zero workers raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            UniversalConfig(task=TaskConfig(max_workers=0))

    def test_negative_cache_ttl_raises_error(self):
        """Test that negative cache TTL raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            UniversalConfig(cache=CacheConfig(ttl_seconds=-1))


class TestConfigCreation:
    """Test different ways to create config."""

    def test_create_default_returns_valid_config(self):
        """Test that create_default returns valid config."""
        config = UniversalConfig.create_default()

        assert config is not None
        assert isinstance(config, UniversalConfig)
        assert config.database is not None

    def test_create_production_config(self):
        """Test creating production config."""
        config = UniversalConfig(environment="production")

        assert config.environment == "production"
        assert config.logging.level == "INFO"

    def test_create_development_config(self):
        """Test creating development config."""
        config = UniversalConfig(environment="development")

        assert config.environment == "development"

    def test_create_test_config(self):
        """Test creating test config."""
        config = UniversalConfig(environment="test")

        assert config.environment == "test"
