#!/usr/bin/env python3
"""
Integration test - Actually apply fixes and verify results
"""
import json
import subprocess
from pathlib import Path
from shutil import copy2


def backup_files():
    """Create backups of test files"""
    files = [
        'examples/test_files/core/phoenix_config/loaders.py',
        'examples/test_files/core/prompt_profiles.py',
        'examples/test_files/utils/api_client.py'
    ]
    for f in files:
        copy2(f, f + '.backup')
    print("✓ Backed up test files")


def restore_files():
    """Restore original test files from backup"""
    files = [
        'examples/test_files/core/phoenix_config/loaders.py',
        'examples/test_files/core/prompt_profiles.py',
        'examples/test_files/utils/api_client.py'
    ]
    for f in files:
        backup = f + '.backup'
        if Path(backup).exists():
            copy2(backup, f)
            Path(backup).unlink()
    print("✓ Restored original files")


def apply_single_fix(issue):
    """Apply a single fix using the logic from kdaf-fix"""
    from pathlib import Path

    file_path = Path(issue['file_path'])
    line_number = issue['line_number']
    old_code = issue['code_snippet']
    new_code = issue['suggested_fix']

    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Validate line number
    if line_number < 1 or line_number > len(lines):
        print(f"✗ {issue['id']}: Line {line_number} out of range")
        return False

    # Get actual line
    actual_line = lines[line_number - 1]

    # Validate code snippet
    if old_code.strip() not in actual_line:
        print(f"✗ {issue['id']}: Code mismatch")
        return False

    # Apply fix
    lines[line_number - 1] = actual_line.replace(old_code.strip(), new_code)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"✓ {issue['id']}: Applied fix to {file_path}:{line_number}")
    return True


def verify_fixes():
    """Verify that all fixes were applied correctly"""
    checks = [
        {
            "id": "SEC-001",
            "file": "examples/test_files/core/phoenix_config/loaders.py",
            "should_contain": "shell=False",
            "should_not_contain": "shell=True"
        },
        {
            "id": "SEC-002",
            "file": "examples/test_files/core/prompt_profiles.py",
            "should_contain": "except (FileNotFoundError, json.JSONDecodeError)",
            "should_not_contain": "except Exception:"
        },
        {
            "id": "SEC-003",
            "file": "examples/test_files/utils/api_client.py",
            "should_contain": "os.getenv('API_KEY')",
            "should_not_contain": "API_KEY = 'sk-1234567890abcdef'"
        }
    ]

    all_passed = True
    for check in checks:
        with open(check['file'], 'r') as f:
            content = f.read()

        passed = check['should_contain'] in content
        if 'should_not_contain' in check:
            passed = passed and (check['should_not_contain'] not in content)

        if passed:
            print(f"✓ {check['id']}: Verification passed")
        else:
            print(f"✗ {check['id']}: Verification FAILED")
            all_passed = False

    return all_passed


def main():
    print("="*80)
    print("KDAF-FIX INTEGRATION TEST")
    print("="*80 + "\n")

    # Load test issues
    with open('examples/test_files/test_issues.json', 'r') as f:
        data = json.load(f)

    issues = data['issues']

    try:
        # Backup
        print("\n[1] Creating backups...")
        backup_files()

        # Apply fixes
        print("\n[2] Applying fixes...")
        for issue in issues:
            apply_single_fix(issue)

        # Verify
        print("\n[3] Verifying fixes...")
        if verify_fixes():
            print("\n" + "="*80)
            print("✅ INTEGRATION TEST PASSED")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("❌ INTEGRATION TEST FAILED")
            print("="*80)

        # Show git diff
        print("\n[4] Git diff of changes:")
        print("-"*80)
        for issue in issues:
            file_path = issue['file_path']
            result = subprocess.run(['git', 'diff', file_path], capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)

    finally:
        # Restore
        print("\n[5] Restoring original files...")
        restore_files()
        print("\n✓ Test complete. Files restored to original state.")


if __name__ == '__main__':
    main()
