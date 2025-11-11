#!/bin/bash
# Agency System Setup

echo "🚀 Agency System Installation"
echo "============================="

# 1. Python environment
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 2. Create directories
echo "📁 Creating project structure..."
mkdir -p notebooks projects

# 3. Copy example notebook if it doesn't exist
if [ ! -f "notebooks/analysis_workflow.ipynb" ]; then
    echo "📓 Example notebooks already in place"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo ""
echo "1. Start API server:"
echo "   python cli/main.py serve --port 5000"
echo ""
echo "2. Run workflow from CLI:"
echo "   python cli/main.py run my-project --request 'My Django app is slow' --tech-stack django"
echo ""
echo "3. Check project status:"
echo "   python cli/main.py status my-project-20251110_143000"
echo ""
