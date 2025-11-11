#!/bin/bash
# Example usage of the Quality Measurement Layer

echo "=========================================="
echo "Quality Measurement Layer - Usage Examples"
echo "=========================================="
echo ""

echo "1. Check a single component:"
echo "   python quality_gate.py agency-toolkit"
echo ""

echo "2. Check all components:"
echo "   python quality_gate.py --all"
echo ""

echo "3. Run in CI mode (strict enforcement):"
echo "   python quality_gate.py agency-toolkit --ci"
echo ""

echo "4. Custom output directory:"
echo "   python quality_gate.py agency-toolkit --output my_reports/"
echo ""

echo "5. View standards and thresholds:"
echo "   cat quality_standards.toml"
echo ""

echo "=========================================="
echo "Running a quick check on explore_agent..."
echo "=========================================="
echo ""

python quality_gate.py explore_agent --output quality_reports
