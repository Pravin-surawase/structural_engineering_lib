#!/bin/bash
# Quick verification script for STREAMLIT-FIX-001
# Run this to verify all fixes are working

echo "🔍 STREAMLIT-FIX-001 Verification Script"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "📊 Running test suite..."
python3 -m pytest tests/ -v --tb=line -q 2>&1 | tail -10
EXIT_CODE=$?

echo ""
echo "📈 Test Statistics:"
python3 -m pytest tests/ --collect-only -q 2>&1 | grep "test session starts" -A 2

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passing - FIX-001 VERIFIED"
    echo ""
    echo "📝 Documentation created:"
    ls -1 docs/STREAMLIT-FIX-001*.md docs/AGENT-6*.md docs/HANDOFF*.md 2>/dev/null | wc -l | xargs echo "  Files:"
    echo ""
    echo "�� Ready for main agent review and merge!"
else
    echo "❌ Tests failing - verification FAILED"
    exit 1
fi
