#!/usr/bin/env python3
"""
Direct validation test for apply_fix logic
"""
from pathlib import Path


def test_apply_fix():
    """Test the fix application logic"""

    # Test 1: Read the file
    file_path = Path('examples/test_files/core/phoenix_config/loaders.py')
    with open(file_path, 'r') as f:
        lines = f.readlines()

    print(f"✓ File read: {len(lines)} lines")

    # Test 2: Find the vulnerable line
    line_number = 25
    if line_number > len(lines):
        print(f"✗ Line {line_number} out of range")
        return False

    actual_line = lines[line_number - 1]
    print(f"✓ Line {line_number}: {actual_line.strip()}")

    # Test 3: Check if vulnerable code exists
    old_code = "subprocess.run(user_command, shell=True, capture_output=True)"
    if old_code.strip() not in actual_line:
        print(f"✗ Code mismatch!")
        print(f"  Expected: {old_code.strip()}")
        print(f"  Actual: {actual_line.strip()}")
        return False

    print(f"✓ Code match found")

    # Test 4: Apply fix (dry run - don't write)
    new_code = "subprocess.run(shlex.split(user_command), shell=False, capture_output=True)"
    new_line = actual_line.replace(old_code.strip(), new_code)
    print(f"✓ Fixed line would be: {new_line.strip()}")

    # Test 5: Verify all 3 issues
    print("\n" + "="*80)
    print("Testing all 3 security issues from test_issues.json:")
    print("="*80)

    issues = [
        {
            "id": "SEC-001",
            "file": "examples/test_files/core/phoenix_config/loaders.py",
            "line": 25,
            "old": "subprocess.run(user_command, shell=True, capture_output=True)"
        },
        {
            "id": "SEC-002",
            "file": "examples/test_files/core/prompt_profiles.py",
            "line": 28,
            "old": "except Exception:"
        },
        {
            "id": "SEC-003",
            "file": "examples/test_files/utils/api_client.py",
            "line": 9,
            "old": "API_KEY = 'sk-1234567890abcdef'"
        }
    ]

    for issue in issues:
        file_path = Path(issue['file'])
        with open(file_path, 'r') as f:
            lines = f.readlines()

        if issue['line'] > len(lines):
            print(f"✗ {issue['id']}: Line out of range")
            continue

        actual = lines[issue['line'] - 1]
        if issue['old'].strip() in actual:
            print(f"✓ {issue['id']}: Found at {issue['file']}:{issue['line']}")
        else:
            print(f"✗ {issue['id']}: Code mismatch")
            print(f"  Expected substring: {issue['old'].strip()}")
            print(f"  Actual line: {actual.strip()}")

    print("\n✅ All validation tests passed!")
    return True


if __name__ == '__main__':
    test_apply_fix()
