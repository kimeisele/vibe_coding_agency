#!/bin/bash

# Gather Script - Vibe Coding Agency Structure
# Sammelt alle relevanten Files für Analyse
# Ausführung: bash gather.sh > agency_structure.txt 2>&1

set -e

BASEDIR="/Users/ss/projects/ai_slop_agency"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="agency_structure_${TIMESTAMP}.md"

echo "🔍 Gathering Vibe Coding Agency Structure..."
echo "📁 Base Directory: $BASEDIR"
echo "📝 Output File: $OUTPUT_FILE"
echo ""

# Funktion zum Sammeln von Files
gather_file() {
    local filepath=$1
    local section_title=$2
    
    if [ -f "$filepath" ]; then
        echo "---"
        echo "## $section_title"
        echo "**File:** \`$filepath\`"
        echo ""
        echo "\`\`\`"
        cat "$filepath" 2>/dev/null || echo "⚠️ Could not read file"
        echo "\`\`\`"
        echo ""
    else
        echo "⚠️ File not found: $filepath"
        echo ""
    fi
}

# Funktion zum Sammeln von Verzeichnis-Struktur
gather_tree() {
    local dirpath=$1
    local section_title=$2
    
    if [ -d "$dirpath" ]; then
        echo "---"
        echo "## $section_title - Directory Tree"
        echo "**Directory:** \`$dirpath\`"
        echo ""
        echo "\`\`\`"
        find "$dirpath" -type f -name "*.py" -o -name "*.md" -o -name "*.ipynb" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" | head -50 | sort
        echo "\`\`\`"
        echo ""
    else
        echo "⚠️ Directory not found: $dirpath"
        echo ""
    fi
}

# Header
cat > "$OUTPUT_FILE" << 'EOF'
# 🔍 Vibe Coding Agency - Complete Structure Dump

**Generated:** $(date)
**Base:** /Users/ss/projects/ai_slop_agency

---

EOF

# 1. ROOT Level Files
echo "📋 Gathering ROOT level files..." >&2
gather_file "$BASEDIR/START_HERE.md" "1. START_HERE.md" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/MONOREPO.md" "2. MONOREPO.md" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/SYSTEM_ARCHITECTURE.md" "3. SYSTEM_ARCHITECTURE.md" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/.gitignore" "4. .gitignore" >> "$OUTPUT_FILE"

# 2. SIMPLE_MOTOR
echo "📋 Gathering simple_motor..." >&2
gather_tree "$BASEDIR/simple_motor" "2. simple_motor Directory Structure" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/simple_motor/README.md" "2a. simple_motor/README.md" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/simple_motor/PHILOSOPHY.md" "2b. simple_motor/PHILOSOPHY.md" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/simple_motor/demo.py" "2c. simple_motor/demo.py" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/simple_motor/orchestrator.py" "2d. simple_motor/orchestrator.py" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/simple_motor/workflow.ipynb" "2e. simple_motor/workflow.ipynb" >> "$OUTPUT_FILE"

# 3. AGENCY_KNOWLEDGE_BASE
echo "📋 Gathering agency_knowledge_base..." >&2
gather_tree "$BASEDIR/agency_knowledge_base" "3. agency_knowledge_base Directory Structure" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/agency_knowledge_base/00_THE_CORE_PROTOCOL.md" "3a. Core Protocol" >> "$OUTPUT_FILE"
for file in "$BASEDIR/agency_knowledge_base/01_PROTOCOLS"/*.md; do
    [ -f "$file" ] && gather_file "$file" "3b. $(basename $file)" >> "$OUTPUT_FILE"
done

# 4. VIBE_CODING_AGENCY
echo "📋 Gathering vibe_coding_agency..." >&2
gather_tree "$BASEDIR/vibe_coding_agency" "4. vibe_coding_agency Directory Structure" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/vibe_coding_agency/README.md" "4a. vibe_coding_agency/README.md" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/vibe_coding_agency/agency.py" "4b. vibe_coding_agency/agency.py" >> "$OUTPUT_FILE"

# 5. AGENCY_SYSTEM_COMPLETE
echo "📋 Gathering agency-system-complete..." >&2
gather_tree "$BASEDIR/agency-system-complete" "5. agency-system-complete Directory Structure" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/agency-system-complete/README.md" "5a. agency-system-complete/README.md" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/agency-system-complete/agency-system/cli/main.py" "5b. agency-system/cli/main.py" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/agency-system-complete/requirements.txt" "5c. agency-system-complete/requirements.txt" >> "$OUTPUT_FILE"

# 6. ZUSÄTZLICHE CONFIG FILES
echo "📋 Gathering config files..." >&2
gather_file "$BASEDIR/requirements.txt" "6a. Root requirements.txt" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/pyproject.toml" "6b. pyproject.toml" >> "$OUTPUT_FILE"
gather_file "$BASEDIR/setup.py" "6c. setup.py" >> "$OUTPUT_FILE"

# Summary
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "## 📊 Summary" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**Generated at:** $(date)" >> "$OUTPUT_FILE"
echo "**Total Python files:** $(find "$BASEDIR" -name "*.py" | wc -l)" >> "$OUTPUT_FILE"
echo "**Total Markdown files:** $(find "$BASEDIR" -name "*.md" | wc -l)" >> "$OUTPUT_FILE"
echo "**Total Notebooks:** $(find "$BASEDIR" -name "*.ipynb" | wc -l)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "✅ Gathering complete!" >> "$OUTPUT_FILE"

echo ""
echo "✅ Done! Output saved to: $OUTPUT_FILE"
echo ""
echo "📊 Statistics:"
echo "   Python files: $(find "$BASEDIR" -name "*.py" -type f | wc -l)"
echo "   Markdown files: $(find "$BASEDIR" -name "*.md" -type f | wc -l)"
echo "   Notebook files: $(find "$BASEDIR" -name "*.ipynb" -type f | wc -l)"
echo ""
echo "📤 Next: Upload $OUTPUT_FILE to Claude"