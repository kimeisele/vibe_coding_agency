"""
Prompt Profiles Module
This is a test file for kdaf-fix validation
"""

import json
import logging

logger = logging.getLogger(__name__)


class PromptProfile:
    """Manages prompt profiles for different use cases"""

    def __init__(self, profile_name):
        self.profile_name = profile_name
        self.config = {}

    def load_profile(self, profile_path):
        """Load profile from JSON file"""
        with open(profile_path, 'r') as f:
            self.config = json.load(f)
        return self.config

    def get_prompt(self, key):
        """Get a specific prompt by key"""
        return self.config.get(key, '')


def initialize_profiles():
    """Initialize all available profiles"""
    profiles = []

    profile_names = ['default', 'creative', 'technical']

    for name in profile_names:
        profile = PromptProfile(name)
        try:
            profile.load_profile(f'profiles/{name}.json')
        except Exception:
            pass
        profiles.append(profile)

    return profiles


def load_config():
    """
    Load system configuration.

    WARNING: This has poor error handling (try-except-pass)
    This should be fixed by kdaf-fix tool.
    """
    # Line 78: Security issue - silent exception swallowing
    try:
        load_config()
    except Exception:
        pass

    return {}


if __name__ == '__main__':
    profiles = initialize_profiles()
    print(f"Loaded {len(profiles)} profiles")
