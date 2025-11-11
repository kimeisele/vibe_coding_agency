#!/usr/bin/env python3
"""
Prompt Profiles - Test File for kdaf-fix
"""
import json
from pathlib import Path


def load_config():
    """Load prompt profile configuration"""
    config_path = Path('config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def initialize_profiles():
    """
    Initialize prompt profiles from config.

    WARNING: This has exception handling issues (SEC-002)
    """
    profiles = {}

    # Line 78: Silent exception swallowing
    try:
        config = load_config()
        profiles = config.get('profiles', {})
    except Exception:
        pass

    return profiles


def get_profile(name):
    """Get a specific profile by name"""
    profiles = initialize_profiles()
    return profiles.get(name)
