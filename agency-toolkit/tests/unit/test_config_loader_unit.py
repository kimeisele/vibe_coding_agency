"""Unit tests for Phoenix Configuration Loader."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from agency_toolkit.core.phoenix_config.loaders import ConfigLoader
from agency_toolkit.core.phoenix_config.validators import ConfigurationError


class TestConfigLoaderFromFile:
    """Test ConfigLoader.from_file functionality."""

    def test_from_file_loads_yaml_config(self, tmp_path):
        """Test loading configuration from YAML file."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "environment": "development",
            "database": {"url": "sqlite:///test.db"},
            "api": {"port": 3000, "host": "0.0.0.0"},
            "logging": {"level": "DEBUG"},
        }
        config_file.write_text(yaml.dump(config_data))

        config = ConfigLoader.from_file(config_file)

        assert config.environment == "development"
        assert config.database.url == "sqlite:///test.db"
        assert config.api.port == 3000
        assert config.logging.level == "DEBUG"

    def test_from_file_raises_error_for_missing_file(self):
        """Test that from_file raises error for missing file."""
        with pytest.raises(ConfigurationError, match="not found"):
            ConfigLoader.from_file("/nonexistent/config.yaml")

    def test_from_file_raises_error_for_invalid_yaml(self, tmp_path):
        """Test that from_file raises error for invalid YAML."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content:")

        with pytest.raises(ConfigurationError):
            ConfigLoader.from_file(config_file)

    def test_from_file_uses_defaults_for_missing_fields(self, tmp_path):
        """Test that missing fields use defaults."""
        config_file = tmp_path / "partial.yaml"
        config_data = {"environment": "test"}
        config_file.write_text(yaml.dump(config_data))

        config = ConfigLoader.from_file(config_file)

        assert config.environment == "test"
        assert config.database is not None  # Uses default
        assert config.api is not None  # Uses default


class TestConfigLoaderFromEnv:
    """Test ConfigLoader.from_env functionality."""

    def test_from_env_uses_environment_variables(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            "APP_ENV": "development",
            "DATABASE_URL": "postgresql://localhost/testdb",
            "API_HOST": "0.0.0.0",
            "API_PORT": "3000",
            "LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, env_vars):
            config = ConfigLoader.from_env()

            assert config.environment == "development"
            assert config.database.url == "postgresql://localhost/testdb"
            assert config.api.host == "0.0.0.0"
            assert config.api.port == 3000
            assert config.logging.level == "DEBUG"

    def test_from_env_uses_defaults_for_missing_vars(self):
        """Test that missing env vars use defaults."""
        # Clear all but keep essential vars that have no defaults
        minimal_env = {
            "DATABASE_URL": "sqlite:///app.db",
            "API_HOST": "localhost",
        }
        with patch.dict(os.environ, minimal_env, clear=True):
            config = ConfigLoader.from_env()

            assert config.environment == "production"  # Default
            assert config.api.port == 8000  # Default
            assert config.logging.level == "INFO"  # Default

    def test_from_env_parses_boolean_vars(self):
        """Test that boolean environment variables are parsed correctly."""
        env_vars = {
            "DATABASE_URL": "sqlite:///app.db",
            "API_HOST": "localhost",
            "DB_ECHO": "true",
            "DEBUG": "false",
            "ENABLE_CACHING": "true",
        }

        with patch.dict(os.environ, env_vars):
            config = ConfigLoader.from_env()

            assert config.database.echo is True
            assert config.api.debug is False
            assert config.performance.enable_caching is True

    def test_from_env_parses_integer_vars(self):
        """Test that integer environment variables are parsed correctly."""
        env_vars = {
            "DATABASE_URL": "sqlite:///app.db",
            "API_HOST": "localhost",
            "API_PORT": "9000",
            "DB_POOL_SIZE": "20",
            "SHELL_TIMEOUT": "120",
            "CACHE_TTL": "600",
        }

        with patch.dict(os.environ, env_vars):
            config = ConfigLoader.from_env()

            assert config.api.port == 9000
            assert config.database.pool_size == 20
            assert config.shell.timeout == 120
            assert config.cache.ttl_seconds == 600


class TestConfigLoaderFromDict:
    """Test ConfigLoader._from_dict functionality."""

    def test_from_dict_creates_config(self):
        """Test creating config from dictionary."""
        config_dict = {
            "environment": "development",
            "database": {"url": "sqlite:///test.db", "pool_size": 10},
            "api": {"host": "localhost", "port": 5000},
            "logging": {"level": "DEBUG"},
        }

        config = ConfigLoader._from_dict(config_dict)

        assert config.environment == "development"
        assert config.database.url == "sqlite:///test.db"
        assert config.database.pool_size == 10
        assert config.api.port == 5000

    def test_from_dict_validates_config(self):
        """Test that _from_dict validates the created config."""
        invalid_config = {
            "environment": "invalid_env",
        }

        with pytest.raises(ConfigurationError):
            ConfigLoader._from_dict(invalid_config)

    def test_from_dict_with_empty_components(self):
        """Test _from_dict with minimal configuration."""
        config_dict = {}

        config = ConfigLoader._from_dict(config_dict)

        assert config is not None
        assert config.environment == "production"  # Default
        assert config.database is not None  # Created with defaults


class TestConfigLoaderIntegration:
    """Integration tests for ConfigLoader."""

    def test_config_priority_file_over_defaults(self, tmp_path):
        """Test that file config overrides defaults."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "environment": "test",
            "api": {"port": 7000},
        }
        config_file.write_text(yaml.dump(config_data))

        config = ConfigLoader.from_file(config_file)

        # File values
        assert config.environment == "test"
        assert config.api.port == 7000

        # Defaults preserved
        assert config.database is not None

    def test_config_with_nested_objects(self, tmp_path):
        """Test loading config with nested configuration objects."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "environment": "production",
            "database": {
                "url": "postgresql://prod.example.com/db",
                "echo": False,
                "pool_size": 20,
                "max_overflow": 30,
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8080,
                "debug": False,
                "workers": 4,
            },
            "logging": {
                "level": "WARNING",
                "format": "json",
            },
            "cache": {
                "backend": "redis",
                "ttl_seconds": 600,
                "max_size": 10000,
                "url": "redis://localhost:6379",
            },
        }
        config_file.write_text(yaml.dump(config_data))

        config = ConfigLoader.from_file(config_file)

        assert config.database.url == "postgresql://prod.example.com/db"
        assert config.database.pool_size == 20
        assert config.api.workers == 4
        assert config.cache.backend == "redis"
        assert config.cache.ttl_seconds == 600


class TestEnvironmentIntegration:
    """Test environment variable integration."""

    def test_all_database_vars(self):
        """Test loading all database configuration from env."""
        env_vars = {
            "DATABASE_URL": "postgresql://localhost/mydb",
            "DB_ECHO": "true",
            "DB_POOL_SIZE": "15",
            "DB_MAX_OVERFLOW": "25",
        }

        with patch.dict(os.environ, env_vars):
            config = ConfigLoader.from_env()

            assert config.database.url == "postgresql://localhost/mydb"
            assert config.database.echo is True
            assert config.database.pool_size == 15
            assert config.database.max_overflow == 25

    def test_all_api_vars(self):
        """Test loading all API configuration from env."""
        env_vars = {
            "DATABASE_URL": "sqlite:///app.db",
            "API_HOST": "api.example.com",
            "API_PORT": "443",
            "DEBUG": "true",
            "API_WORKERS": "8",
        }

        with patch.dict(os.environ, env_vars):
            config = ConfigLoader.from_env()

            assert config.api.host == "api.example.com"
            assert config.api.port == 443
            assert config.api.debug is True
            assert config.api.workers == 8

    def test_all_shell_vars(self):
        """Test loading all shell configuration from env."""
        env_vars = {
            "DATABASE_URL": "sqlite:///app.db",
            "API_HOST": "localhost",
            "SHELL_TIMEOUT": "300",
            "MAX_OUTPUT_LINES": "5000",
        }

        with patch.dict(os.environ, env_vars):
            config = ConfigLoader.from_env()

            assert config.shell.timeout == 300
            assert config.shell.max_output_lines == 5000

    def test_all_logging_vars(self):
        """Test loading all logging configuration from env."""
        env_vars = {
            "DATABASE_URL": "sqlite:///app.db",
            "API_HOST": "localhost",
            "LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, env_vars):
            config = ConfigLoader.from_env()

            assert config.logging.level == "DEBUG"


class TestConfigLoaderErrorHandling:
    """Test error handling in ConfigLoader."""

    def test_from_file_with_permission_error(self, tmp_path):
        """Test handling of permission errors."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("test: data")

        # Make file unreadable (if possible)
        try:
            config_file.chmod(0o000)
            with pytest.raises(ConfigurationError):
                ConfigLoader.from_file(config_file)
        finally:
            config_file.chmod(0o644)

    def test_from_file_with_corrupted_yaml(self, tmp_path):
        """Test handling of corrupted YAML."""
        config_file = tmp_path / "bad.yaml"
        config_file.write_text("{ invalid yaml [ content ]")

        with pytest.raises(ConfigurationError):
            ConfigLoader.from_file(config_file)

    def test_from_dict_preserves_config_file_path(self):
        """Test that config file path is preserved."""
        config_dict = {
            "config_file": "/etc/config/app.yaml",
            "environment": "production",
        }

        config = ConfigLoader._from_dict(config_dict)

        assert config.config_file == Path("/etc/config/app.yaml")
