# CLI Examples & Workflows

**Practical examples for common meta-audit workflows.**

---

## Example 1: Analyze Single Project

### Scenario
You want to audit your Python microservice for security and complexity issues.

### Commands
```bash
# Step 1: Navigate to your project
cd /path/to/my_microservice

# Step 2: Run analysis (takes ~2-5 seconds)
meta-audit analyze --path . --format table

# Output: Terminal table with findings

# Step 3: Save detailed report
meta-audit analyze --path . --format json --output-file report.json

# Step 4: Review in your favorite tool
cat report.json | jq '.findings | length'  # Count total findings
cat report.json | jq '.summary'              # See summary
```

### Expected Output
```
Meta-Audit Report
================================================================================
Critical:   1 | High:   3 | Medium:   8 | Low:  15 | Total:  27
Execution time: 2.45s
Generated: 2025-11-10T12:30:28.415588

Severity  Category        Analyzer   File                       Line  Message
────────  ──────────────  ─────────  ────────────────────────   ────  ─────────────────────────────
CRITICAL  security        bandit     src/auth.py                 42   Use of hardcoded password
HIGH      code_structure  radon      src/api/models.py          105   Cyclomatic complexity 15
HIGH      security        bandit     src/db/queries.py           88   Potential SQL injection
MEDIUM    code_structure  radon      src/utils/helpers.py        20   High McCabe complexity
...
```

---

## Example 2: Create Capsule & Analyze Later

### Scenario
Archive a project snapshot for offline analysis or team review.

### Commands
```bash
# Step 1: Create ProjectCapsule (efficient snapshot)
meta-audit capsule create --path /legacy/project --mode hotspot

# Output: /legacy/project/legacy_project.capsule.json (~150 KB)

# Step 2: Share capsule
gsutil cp legacy_project.capsule.json gs://my-bucket/archive/2025-11-10/

# Step 3: Later, analyze from archive
meta-audit analyze \
  --capsule gs://my-bucket/archive/2025-11-10/legacy_project.capsule.json \
  --format json \
  --output-file legacy_report.json

# Step 4: Compare with current version
meta-audit capsule create --path /legacy/project --mode hotspot --output current.json
# ... analyze current.json same way ...
# Compare reports to see improvements over time
```

---

## Example 3: Multi-Project Corpus Analysis

### Scenario
Audit 5 microservices to find systemic issues (duplicate vulnerabilities, common patterns).

### Commands
```bash
# Step 1: Create capsules for all projects
for service in auth api gateway worker database; do
  echo "Creating capsule for $service..."
  meta-audit capsule create \
    --path /services/$service \
    --mode hotspot \
    --output ${service}.capsule.json
done

# Step 2: Analyze entire corpus
meta-audit analyze \
  --capsule auth.capsule.json \
  --capsule api.capsule.json \
  --capsule gateway.capsule.json \
  --capsule worker.capsule.json \
  --capsule database.capsule.json \
  --format json \
  --output-file corpus_analysis.json

# Step 3: Extract cross-project patterns
cat corpus_analysis.json | jq '.cross_project_patterns'

# Expected output:
[
  {
    "pattern_type": "sql_injection",
    "severity": "HIGH",
    "projects_count": 3,
    "projects": ["api", "gateway", "database"],
    "message": "SQL injection vulnerability found in 3 projects"
  },
  {
    "pattern_type": "missing_input_validation",
    "severity": "HIGH",
    "projects_count": 4,
    "projects": ["auth", "api", "gateway", "worker"]
  }
]

# Step 4: Create action items
echo "Systemic Issues Found:"
cat corpus_analysis.json | jq -r '.cross_project_patterns[] | "\(.projects_count) projects: \(.message)"'

# Output:
# 3 projects: SQL injection vulnerability found in 3 projects
# 4 projects: Security vulnerability affecting 4 projects
```

---

## Example 4: Continuous Integration / CI Pipeline

### Scenario
Integrate meta-audit into GitHub Actions to catch issues in PRs.

### Setup (`.github/workflows/audit.yml`)
```yaml
name: Meta-Audit

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install meta-audit
        run: pip install meta-audit

      - name: Run analysis
        run: meta-audit analyze --path . --format json --output-file report.json

      - name: Check for CRITICAL issues
        run: |
          CRITICAL=$(jq '.summary.CRITICAL' report.json)
          if [ "$CRITICAL" -gt 0 ]; then
            echo "❌ Found $CRITICAL CRITICAL issues"
            exit 1
          fi
          echo "✅ No CRITICAL issues found"

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        run: |
          SUMMARY=$(jq '.summary' report.json)
          echo "### Meta-Audit Report" >> $GITHUB_STEP_SUMMARY
          echo "$SUMMARY" >> $GITHUB_STEP_SUMMARY

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: report.json
```

### Usage
```bash
# After PR is created, workflow automatically runs
# Blocks merge if CRITICAL issues found
# Comments summary on PR
```

---

## Example 5: Compare Two Versions

### Scenario
Track improvements: "Did we fix the security issues since last release?"

### Commands
```bash
# Previous release analysis (from capsule archive)
meta-audit analyze \
  --capsule v1.0.capsule.json \
  --format json \
  --output-file v1.0_report.json

# Current HEAD analysis
meta-audit analyze \
  --path . \
  --format json \
  --output-file current_report.json

# Compare
python3 << 'EOF'
import json

with open('v1.0_report.json') as f:
    v1 = json.load(f)
with open('current_report.json') as f:
    current = json.load(f)

print("Improvement Summary:")
print(f"CRITICAL: {v1['summary']['CRITICAL']} → {current['summary']['CRITICAL']}")
print(f"HIGH:     {v1['summary']['HIGH']} → {current['summary']['HIGH']}")
print(f"MEDIUM:   {v1['summary']['MEDIUM']} → {current['summary']['MEDIUM']}")
print(f"TOTAL:    {v1['summary']['TOTAL']} → {current['summary']['TOTAL']}")

# Specific improvements
fixed = v1['summary']['CRITICAL'] - current['summary']['CRITICAL']
print(f"\n✅ Fixed {fixed} CRITICAL issues")
EOF

# Output:
# Improvement Summary:
# CRITICAL: 5 → 2
# HIGH:     12 → 8
# MEDIUM:   28 → 22
# TOTAL:    45 → 32
#
# ✅ Fixed 3 CRITICAL issues
```

---

## Example 6: Focus on Specific Severity Level

### Scenario
You're in a sprint focused on security. Show only HIGH and CRITICAL findings.

### Commands
```bash
# Run analysis and filter
meta-audit analyze --path . --format json | \
  jq '.findings[] | select(.severity | . == "CRITICAL" or . == "HIGH")'

# Or save first
meta-audit analyze --path . --format json --output-file full_report.json

# Then filter
jq '.findings[] | select(.severity == "HIGH") | {file: .file, line: .line, message: .message}' \
  full_report.json

# Output:
# {
#   "file": "src/auth.py",
#   "line": 42,
#   "message": "Use of hardcoded password"
# }
```

---

## Example 7: Team Review Workflow

### Scenario
Share audit results with non-technical stakeholders (project manager, QA).

### Commands
```bash
# Generate human-readable table report
meta-audit analyze --path . --format table > audit_summary.txt

# Also generate JSON for archival
meta-audit analyze --path . --format json --output-file audit_detail.json

# Create simple HTML summary (using jq)
cat audit_detail.json | jq -r '
  "# Audit Report\n\n" +
  "**Total Issues:** \(.summary.TOTAL)\n\n" +
  "## Breakdown\n" +
  "- Critical: \(.summary.CRITICAL)\n" +
  "- High: \(.summary.HIGH)\n" +
  "- Medium: \(.summary.MEDIUM)\n" +
  "- Low: \(.summary.LOW)\n\n" +
  "**Generated:** \(.timestamp)"
' > AUDIT_REPORT.md

# Share with team
# - audit_summary.txt → Slack
# - AUDIT_REPORT.md → GitHub README
# - audit_detail.json → Archive in S3
```

---

## Example 8: Automated Daily Audit

### Scenario
Daily batch analysis of all services, tracking trends over time.

### Setup (Cron Job)
```bash
#!/bin/bash
# daily_audit.sh

DATE=$(date +%Y-%m-%d)
RESULTS_DIR=/var/log/audits/$DATE

mkdir -p $RESULTS_DIR

# Audit each service
for service in auth api worker gateway; do
  meta-audit analyze \
    --path /services/$service \
    --format json \
    --output-file $RESULTS_DIR/${service}_report.json
done

# Create daily summary
jq -s 'map(.summary) | add' $RESULTS_DIR/*.json > $RESULTS_DIR/daily_summary.json

# Upload to monitoring system
curl -X POST https://metrics.example.com/audit \
  -d @$RESULTS_DIR/daily_summary.json

echo "✅ Daily audit complete: $DATE"
```

### Crontab
```bash
# Run daily at 2 AM
0 2 * * * /scripts/daily_audit.sh >> /var/log/audit_cron.log 2>&1
```

---

## Troubleshooting Commands

### Debug: Which files are being analyzed?
```bash
# Add verbose logging
meta-audit analyze --path . --verbose 2>&1 | grep -E "(Analyzing|Processing|File)"
```

### Debug: View raw findings before aggregation
```bash
# Export JSON and examine findings array
meta-audit analyze --path . --format json | jq '.findings | length'
meta-audit analyze --path . --format json | jq '.findings[0]'
```

### Debug: Check capsule contents
```bash
meta-audit capsule show my_project.capsule.json

# Output:
# ProjectCapsule: my_project
# Version: 2
# Created: 2025-11-10T12:30:28.415588
# Python: 3.11
# Files: 47
# Size: 234.5 KB
#
# Sample files:
#   src/main.py (450 bytes)
#   src/auth/password.py (1.2 KB)
#   ...
```

### Debug: Performance profiling
```bash
# Time each analysis phase
time meta-audit analyze --path . --format json > /dev/null

# Output:
# real    0m2.456s
# user    0m2.234s
# sys     0m0.156s
```

---

## Pro Tips

1. **Archive Capsules Regularly**
   ```bash
   # Monthly archive for trend analysis
   meta-audit capsule create --path . --mode hotspot \
     --output ./archive/$(date +%Y-%m-01)_capsule.json
   ```

2. **Use `jq` for Custom Reports**
   ```bash
   # Top 5 files by issue count
   jq '.findings | group_by(.file) | map({file: .[0].file, count: length}) | sort_by(-.count) | .[0:5]' report.json
   ```

3. **Combine with grep for Quick Lookups**
   ```bash
   # Find all SQL injection findings
   jq '.findings[] | select(.message | contains("SQL"))' report.json
   ```

4. **Track Over Time**
   ```bash
   # Compare week-to-week improvement
   for week in {1..4}; do
     echo "Week $week:"
     cat reports/week_${week}_report.json | jq '.summary.TOTAL'
   done
   ```

---

See `USER_GUIDE.md` for more detailed documentation.
