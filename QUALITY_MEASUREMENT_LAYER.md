# Quality Measurement Layer

**Systematic quality control for all tools in the Vibe Coding Agency monorepo.**

## Overview

The Quality Measurement Layer (Option C) implements automated quality gates using objective metrics to control code quality across all components. No more manual reviews - the CI/CD pipeline automatically blocks bad code.

## Components

### 1. Quality Standards (`quality_standards.toml`)

Centralized configuration defining quality thresholds for all tools:

- **Complexity thresholds** - Max cyclomatic complexity per function/module
- **Security thresholds** - Max severity issues allowed
- **Coverage requirements** - Minimum test coverage percentages
- **Code quality standards** - Linting and type checking requirements
- **Component-specific overrides** - Different standards per tool

### 2. Quality Gate Script (`quality_gate.py`)

Python script that collects objective quality metrics using industry-standard tools:

**Tools Used:**
- **Radon** - Cyclomatic complexity and maintainability index
- **Bandit** - Security vulnerability scanning
- **Pylint** - Code quality and style analysis
- **Pytest** - Test coverage and pass rate

**Scoring System (0-100):**
- Complexity: 20 points
- Security: 20 points
- Code Quality: 20 points
- Coverage: 20 points
- Test Pass Rate: 20 points

### 3. CI/CD Workflow (`.github/workflows/quality-gate.yml`)

GitHub Actions workflow that:
- Runs on all PRs and pushes to main branches
- Executes quality gate for each component
- Generates comprehensive reports
- Posts summary to PR comments
- **Blocks merge if quality gates fail**

## Usage

### Run Locally

```bash
# Analyze a specific component
python quality_gate.py agency-toolkit

# Analyze all components
python quality_gate.py --all

# CI mode (strict enforcement)
python quality_gate.py agency-toolkit --ci

# Custom output directory
python quality_gate.py agency-toolkit --output my_reports/
```

### View Reports

Reports are saved to `quality_reports/` directory:
- `quality_report_{component}.json` - Detailed metrics in JSON format
- Quality summary printed to console

### Interpret Results

**Quality Score Breakdown:**
- **80-100**: Excellent - Production ready
- **60-79**: Good - Some improvements needed
- **40-59**: Fair - Significant issues
- **0-39**: Poor - Major refactoring needed

**Minimum Threshold:** 80/100 (configurable in `quality_standards.toml`)

## Quality Metrics Explained

### 1. Cyclomatic Complexity

Measures code complexity based on number of decision points.

**Thresholds:**
- Per function: Max 10 (configurable)
- Per module: Max 50 (configurable)
- Average: Max 5.0 (configurable)

**Grades:**
- A: 0-5 (excellent)
- B: 6-10 (good)
- C: 11-20 (moderate)
- D: 21-30 (high)
- F: 31+ (very high)

### 2. Security Issues

Scanned by Bandit for common security vulnerabilities.

**Severity Levels:**
- **Critical**: Immediate security risk (0 allowed)
- **High**: Serious vulnerability (0 allowed)
- **Medium**: Potential issue (5 allowed)
- **Low**: Minor concern (20 allowed)

### 3. Code Quality

Analyzed by Pylint for style and best practices.

**Score:** 0-10 scale
- **7.0+**: Required minimum
- **8.0+**: Good quality
- **9.0+**: Excellent quality

### 4. Test Coverage

Percentage of code covered by tests.

**Thresholds:**
- Agency-Toolkit: 80% (core tool)
- Meta-Audit: 75%
- Explore-Agent: 70% (new tool)

### 5. Test Pass Rate

Percentage of tests that pass.

**Requirement:** 100% (all tests must pass)

## Component-Specific Standards

### Agency-Toolkit
- Higher coverage requirement (80%)
- Core production tool with strict standards

### Meta-Audit
- Standard coverage requirement (75%)
- Analysis engine with moderate standards

### Explore-Agent
- Lower initial coverage (70%)
- New tool, building up test coverage
- Currently non-blocking in CI

## CI/CD Integration

### Quality Gate Behavior

**On Pull Request:**
- Runs quality gate for all components
- Posts summary comment to PR
- Allows manual override for explore-agent
- **Blocks merge if agency-toolkit or meta-audit fail**

**On Push to Main:**
- Same checks as PR
- Stricter enforcement
- No manual overrides

### Customizing Standards

Edit `quality_standards.toml` to adjust thresholds:

```toml
[thresholds]
minimum_quality_score = 80
minimum_coverage = 75.0
max_function_complexity = 10
# ... etc
```

### Adding New Components

1. Add component section to `quality_standards.toml`:

```toml
[components.my-new-tool]
description = "My new tool"
path = "my_new_tool"
minimum_coverage = 70.0
```

2. Add job to `.github/workflows/quality-gate.yml`:

```yaml
- name: Run Quality Gate - My New Tool
  continue-on-error: false  # Set to true initially
  run: |
    python quality_gate.py my_new_tool --ci --output quality_reports
```

## Benefits

### ✅ Automated Quality Control
No more manual code reviews for basic quality issues - let the tools do it.

### ✅ Objective Metrics
All measurements come from industry-standard tools, not opinions.

### ✅ Early Detection
Catch issues in CI before they reach production.

### ✅ Consistent Standards
All tools held to the same quality bar.

### ✅ Visible Progress
Track quality improvements over time via reports.

### ✅ Blocks Bad Code
CI/CD gate prevents low-quality code from being merged.

## Development Workflow

### Before Committing

```bash
# Run quality check locally
python quality_gate.py agency-toolkit

# Fix any issues found
# Re-run until passing
```

### During PR Review

1. Quality gate runs automatically
2. Review the quality report comment
3. Address any failures
4. Push fixes
5. Gate re-runs automatically

### After Merge

Quality metrics are preserved in artifacts for historical tracking.

## Troubleshooting

### "Tool not installed" warnings

Install missing tools:
```bash
pip install radon bandit pylint pytest pytest-cov tomli
```

### Quality gate failing on coverage

Add more tests or adjust threshold in `quality_standards.toml`.

### Complexity violations

Refactor large functions into smaller ones (< 10 CC per function).

### Security issues

Review Bandit report and fix vulnerabilities or mark false positives.

### Lint errors

Run pylint locally and fix reported issues:
```bash
pylint agency_toolkit/
```

## Future Enhancements

- [ ] Historical trend tracking
- [ ] Quality badges for README
- [ ] Automatic issue creation for failures
- [ ] Integration with code review tools
- [ ] Custom quality rules per component
- [ ] Performance benchmarking

## Related Documentation

- `quality_standards.toml` - Quality thresholds configuration
- `quality_gate.py` - Main quality gate implementation
- `.github/workflows/quality-gate.yml` - CI/CD integration
- `agency-toolkit/.github/workflows/quality.yml` - Component-specific quality checks

---

**Last Updated:** 2025-11-11
**Maintainers:** Vibe Coding Agency Team
