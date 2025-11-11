#!/usr/bin/env python3
"""Basic usage example for Universal Config."""

from pathlib import Path
from phoenix_config import UniversalConfig

def main():
    print("=== Universal Config Basic Usage ===\n")
    
    # Create default configuration
    config = UniversalConfig.create_default()
    print("Default Configuration:")
    print(f"  Environment: {config.environment}")
    print(f"  Database URL: {config.database.url}")
    print(f"  API Host: {config.api.host}:{config.api.port}")
    print(f"  Log Level: {config.logging.level}")
    
    print("\n=== Environment-Specific Configs ===\n")
    
    # Development configuration
    dev_config = UniversalConfig.create_for_development(Path.cwd())
    print("Development Config:")
    print(f"  Debug: {dev_config.api.debug}")
    print(f"  Database Echo: {dev_config.database.echo}")
    print(f"  Log Format: {dev_config.logging.format}")
    
    # Production configuration
    prod_config = UniversalConfig.create_for_production()
    print("\nProduction Config:")
    print(f"  Debug: {prod_config.api.debug}")
    print(f"  Workers: {prod_config.api.workers}")
    print(f"  Log Format: {prod_config.logging.format}")
    print(f"  Caching: {prod_config.performance.enable_caching}")
    
    # Test configuration
    test_config = UniversalConfig.create_for_testing()
    print("\nTest Config:")
    print(f"  Database: {test_config.database.url}")
    print(f"  Caching: {test_config.performance.enable_caching}")
    print(f"  Log Level: {test_config.logging.level}")
    
    print("\n=== Configuration Methods ===\n")
    
    # Environment detection
    print("Environment Detection:")
    print(f"  Is Production: {prod_config.is_production()}")
    print(f"  Is Development: {dev_config.is_development()}")
    print(f"  Is Test: {test_config.is_test()}")
    
    # Database URL with substitution
    print(f"\nDatabase URL: {prod_config.get_database_url()}")
    
    # Convert to dict
    config_dict = prod_config.to_dict()
    print(f"\nConfig Keys: {list(config_dict.keys())}")
    
    print("\n=== Save Configuration ===\n")
    
    # Save to file
    prod_config.save_to_file("example_config.yaml")
    print("Configuration saved to example_config.yaml")
    
    # Load from file
    loaded_config = UniversalConfig.load_from_file("example_config.yaml")
    print(f"Loaded environment: {loaded_config.environment}")

if __name__ == "__main__":
    main()
