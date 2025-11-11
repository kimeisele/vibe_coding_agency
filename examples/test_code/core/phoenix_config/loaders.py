"""
Phoenix Config Loader Module
This is a test file for kdaf-fix validation
"""

import subprocess
import os


def load_user_config(config_path):
    """Load user configuration from path"""
    # Read config file
    with open(config_path, 'r') as f:
        config = f.read()
    return config


def execute_user_command(user_command):
    """
    Execute a user-provided command.

    WARNING: This has a security vulnerability (shell=True)
    This should be fixed by kdaf-fix tool.
    """
    # Line 42: Security issue - shell=True with user input
    result = subprocess.run(shlex.split(user_command), shell=False, capture_output=True)
    return result.stdout


def process_config(config_data):
    """Process configuration data"""
    processed = {}
    for key, value in config_data.items():
        processed[key] = str(value).upper()
    return processed


if __name__ == '__main__':
    config = load_user_config('config.yaml')
    print(config)
