"""Chaos Testing Suite (Epic 4.0.3)

Tests extreme inputs, edge cases, and failure modes to ensure the system
fails gracefully with clear error messages instead of cryptic exceptions.

Every chaos test follows the pattern:
1. Create invalid/extreme condition
2. Attempt operation
3. Verify graceful failure with clear error message
4. Assert NO crashes, hangs, or stack overflows
"""
