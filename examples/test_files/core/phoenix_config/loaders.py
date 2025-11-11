#!/usr/bin/env python3
"""
Phoenix Config Loader - Test File for kdaf-fix
"""
import subprocess
import sys


def load_user_config(config_path):
    """Load user configuration with validation"""
    # Read config
    with open(config_path, 'r') as f:
        config = f.read()

    return config


def execute_user_command(user_command):
    """
    Execute a user-provided command.

    WARNING: This has a security vulnerability (SEC-001)
    """
    # Line 42: Command injection vulnerability
    result = subprocess.run(user_command, shell=True, capture_output=True)
    return result.stdout.decode('utf-8')


def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        output = execute_user_command(cmd)
        print(output)


if __name__ == '__main__':
    main()
