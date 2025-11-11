#!/usr/bin/env python3
"""
Edge case tests for kdaf-fix validation
"""
from pathlib import Path


def apply_fix_logic(issue):
    """Replicate apply_fix logic for testing"""
    file_path = issue.get('file_path')
    line_number = issue.get('line_number')
    old_code = issue.get('code_snippet')
    new_code = issue.get('suggested_fix')

    # Validate inputs
    if not file_path or old_code is None or new_code is None:
        return False, "Missing required fields"

    if line_number is None:
        return False, "Missing line_number field"

    # Convert to Path
    file_path = Path(file_path)

    # Check if file exists
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return False, f"Error reading file: {e}"

    # Validate line number
    if line_number < 1 or line_number > len(lines):
        return False, f"Line {line_number} out of range (file has {len(lines)} lines)"

    # Get actual line
    actual_line = lines[line_number - 1]

    # Validate code snippet
    if old_code.strip() not in actual_line:
        return False, "Code mismatch - file may have changed"

    return True, "OK"


def run_edge_case_tests():
    """Run all edge case tests"""
    print("="*80)
    print("KDAF-FIX EDGE CASE TESTS")
    print("="*80 + "\n")

    tests = [
        {
            "name": "Missing file",
            "issue": {
                "file_path": "examples/test_files/nonexistent.py",
                "line_number": 1,
                "code_snippet": "some code",
                "suggested_fix": "fixed code"
            },
            "should_fail": True,
            "expected_error": "File not found"
        },
        {
            "name": "Line number out of range (too high)",
            "issue": {
                "file_path": "examples/test_files/utils/api_client.py",
                "line_number": 99999,
                "code_snippet": "some code",
                "suggested_fix": "fixed code"
            },
            "should_fail": True,
            "expected_error": "out of range"
        },
        {
            "name": "Line number out of range (zero)",
            "issue": {
                "file_path": "examples/test_files/utils/api_client.py",
                "line_number": 0,
                "code_snippet": "some code",
                "suggested_fix": "fixed code"
            },
            "should_fail": True,
            "expected_error": "out of range"
        },
        {
            "name": "Line number out of range (negative)",
            "issue": {
                "file_path": "examples/test_files/utils/api_client.py",
                "line_number": -5,
                "code_snippet": "some code",
                "suggested_fix": "fixed code"
            },
            "should_fail": True,
            "expected_error": "out of range"
        },
        {
            "name": "Code mismatch",
            "issue": {
                "file_path": "examples/test_files/utils/api_client.py",
                "line_number": 9,
                "code_snippet": "THIS CODE DOES NOT EXIST",
                "suggested_fix": "fixed code"
            },
            "should_fail": True,
            "expected_error": "Code mismatch"
        },
        {
            "name": "Missing file_path field",
            "issue": {
                "line_number": 9,
                "code_snippet": "some code",
                "suggested_fix": "fixed code"
            },
            "should_fail": True,
            "expected_error": "Missing required fields"
        },
        {
            "name": "Missing line_number field",
            "issue": {
                "file_path": "examples/test_files/utils/api_client.py",
                "code_snippet": "some code",
                "suggested_fix": "fixed code"
            },
            "should_fail": True,
            "expected_error": "Missing line_number field"
        },
        {
            "name": "Valid fix (should pass)",
            "issue": {
                "file_path": "examples/test_files/utils/api_client.py",
                "line_number": 9,
                "code_snippet": "API_KEY = 'sk-1234567890abcdef'",
                "suggested_fix": "API_KEY = os.getenv('API_KEY')"
            },
            "should_fail": False,
            "expected_error": None
        }
    ]

    passed = 0
    failed = 0

    for test in tests:
        success, error = apply_fix_logic(test['issue'])

        # Check if result matches expectation
        if test['should_fail']:
            if not success and test['expected_error'] in error:
                print(f"✓ {test['name']}")
                print(f"  → Correctly rejected: {error}")
                passed += 1
            else:
                print(f"✗ {test['name']}")
                print(f"  → Expected failure with '{test['expected_error']}', got: {error}")
                failed += 1
        else:
            if success:
                print(f"✓ {test['name']}")
                print(f"  → Correctly accepted")
                passed += 1
            else:
                print(f"✗ {test['name']}")
                print(f"  → Expected success, got error: {error}")
                failed += 1

        print()

    print("="*80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*80)

    if failed == 0:
        print("✅ ALL EDGE CASE TESTS PASSED\n")
        return True
    else:
        print("❌ SOME TESTS FAILED\n")
        return False


if __name__ == '__main__':
    import sys
    success = run_edge_case_tests()
    sys.exit(0 if success else 1)
