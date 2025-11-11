#!/bin/bash
# Dogfooding E2E test for Mistral API integration
# This proves the feature works in real-world scenarios

set -e

echo "🧪 Agency Toolkit - Dogfooding Test"
echo "===================================="
echo ""

# Check API key
if [ -z "$MISTRAL_API_KEY" ]; then
    echo "❌ Error: MISTRAL_API_KEY not set"
    exit 1
fi
echo "✅ API key is set"
echo ""

# Test 1: Direct prompt
echo "Test 1: Direct prompt (short)"
echo "-----------------------------"
python -m agency_toolkit.cli_app mistral --prompt "Say 'Test passed!' in exactly 2 words." --max-tokens 50
echo ""
echo "✅ Test 1 passed"
echo ""

# Test 2: Prompt from file
echo "Test 2: Prompt from file"
echo "------------------------"
cat > /tmp/agency_toolkit_test_prompt.txt << 'PROMPT'
Analyze this CLI application structure and suggest ONE improvement in exactly one sentence:

Command structure:
- social: Generate social media posts
- briefing: Create project briefings
- structure: Setup project folders
- mistral: AI assistant

Respond with exactly one actionable suggestion.
PROMPT

python -m agency_toolkit.cli_app mistral --prompt-file /tmp/agency_toolkit_test_prompt.txt --max-tokens 100
echo ""
echo "✅ Test 2 passed"
rm /tmp/agency_toolkit_test_prompt.txt
echo ""

# Test 3: Stdin (pipe)
echo "Test 3: Stdin (pipe)"
echo "--------------------"
echo "Explain what 'dogfooding' means in software development in one sentence." | \
    python -m agency_toolkit.cli_app mistral --stdin --max-tokens 100
echo ""
echo "✅ Test 3 passed"
echo ""

# Test 4: JSON output
echo "Test 4: JSON output"
echo "-------------------"
python -m agency_toolkit.cli_app mistral \
    --prompt "Return JSON with two fields: status='success' and message='Dogfooding works'" \
    --json-output \
    --max-tokens 100
echo ""
echo "✅ Test 4 passed"
echo ""

echo "===================================="
echo "🎉 All dogfooding tests passed!"
echo "===================================="
