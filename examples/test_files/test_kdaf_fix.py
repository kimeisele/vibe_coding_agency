#!/usr/bin/env python3
"""
Unit tests for kdaf-fix apply_fix() function
"""
import json
import sys
import tempfile
from pathlib import Path
from shutil import copy2

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools'))

# Import the kdaf-fix module (need to load it dynamically since it has no .py extension)
import importlib.util
spec = importlib.util.spec_from_file_location("kdaf_fix", Path(__file__).parent.parent.parent / 'tools' / 'kdaf-fix')
kdaf_fix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kdaf_fix)

apply_fix = kdaf_fix.apply_fix


def test_successful_fix():
    """Test that a valid fix is applied correctly"""
    print("\n" + "="*80)
    print("TEST 1: Successful fix application")
    print("="*80)

    # Create temp file
    test_file = Path('examples/test_files/core/phoenix_config/loaders.py')

    # Create issue
    issue = {
        'file_path': str(test_file),
        'line_number': 25,
        'code_snippet': 'result = subprocess.run(user_command, shell=True, capture_output=True)',
        'suggested_fix': 'result = subprocess.run(shlex.split(user_command), shell=False, capture_output=True)'
    }

    # Read original content
    with open(test_file, 'r') as f:
        original = f.read()

    # Apply fix
    result = apply_fix(issue)

    # Read modified content
    with open(test_file, 'r') as f:
        modified = f.read()

    # Verify
    assert result == True, "Fix should succeed"
    assert 'shell=False' in modified, "Fix should be applied"
    assert 'shlex.split' in modified, "Fix should include shlex.split"

    # Restore original
    with open(test_file, 'w') as f:
        f.write(original)

    print("✅ PASSED: Fix applied successfully")


def test_line_number_out_of_range():
    """Test that out-of-range line numbers are caught"""
    print("\n" + "="*80)
    print("TEST 2: Line number validation")
    print("="*80)

    issue = {
        'file_path': 'examples/test_files/core/phoenix_config/loaders.py',
        'line_number': 9999,  # Way out of range
        'code_snippet': 'some code',
        'suggested_fix': 'fixed code'
    }

    result = apply_fix(issue)

    assert result == False, "Should fail for out-of-range line number"
    print("✅ PASSED: Out-of-range line number rejected")


def test_code_mismatch():
    """Test that code mismatches are detected"""
    print("\n" + "="*80)
    print("TEST 3: Code mismatch detection")
    print("="*80)

    issue = {
        'file_path': 'examples/test_files/core/phoenix_config/loaders.py',
        'line_number': 25,
        'code_snippet': 'THIS CODE DOES NOT EXIST IN THE FILE',
        'suggested_fix': 'fixed code'
    }

    result = apply_fix(issue)

    assert result == False, "Should fail for code mismatch"
    print("✅ PASSED: Code mismatch detected")


def test_missing_file():
    """Test that missing files are handled"""
    print("\n" + "="*80)
    print("TEST 4: Missing file handling")
    print("="*80)

    issue = {
        'file_path': 'examples/test_files/nonexistent/file.py',
        'line_number': 1,
        'code_snippet': 'some code',
        'suggested_fix': 'fixed code'
    }

    result = apply_fix(issue)

    assert result == False, "Should fail for missing file"
    print("✅ PASSED: Missing file detected")


def test_missing_fields():
    """Test that missing required fields are caught"""
    print("\n" + "="*80)
    print("TEST 5: Missing field validation")
    print("="*80)

    issue = {
        'file_path': 'examples/test_files/core/phoenix_config/loaders.py',
        # Missing line_number, code_snippet, suggested_fix
    }

    result = apply_fix(issue)

    assert result == False, "Should fail for missing fields"
    print("✅ PASSED: Missing fields detected")


def run_all_tests():
    """Run all tests"""
    print("\n" + "█"*80)
    print("KDAF-FIX VALIDATION TEST SUITE")
    print("█"*80)

    try:
        test_successful_fix()
        test_line_number_out_of_range()
        test_code_mismatch()
        test_missing_file()
        test_missing_fields()

        print("\n" + "█"*80)
        print("✅ ALL TESTS PASSED")
        print("█"*80 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    run_all_tests()
