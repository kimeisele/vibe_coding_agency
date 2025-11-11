---
id: audit-grid-template
type: template
category: templates
tags: [audit, measurement, objective-data, code-health]
related:
  - thematic-analysis-method
  - heuristic-evaluation
  - god-object-pattern
  - prioritization-matrix
version: 1.0.0
---

# Audit Grid Template

## Purpose

Transform **subjective vibes** into **objective data**.

The Audit Grid makes code quality measurable and actionable.

## Template

### Spreadsheet Format

| Module/File | SRP Violation | God Object | AI Slop | Cognitive Load | Readability | Testability | Themes/Codes | Priority |
|-------------|---------------|------------|---------|----------------|-------------|-------------|--------------|----------|
| auth.py | NO | LOW | NO | 3/7 | 4/5 | 4/5 | Clean | LOW |
| app.py | YES | HIGH | YES | 7/7 | 2/5 | 1/5 | God Object, Bloat | CRITICAL |
| utils.py | YES | MED | YES | 5/7 | 3/5 | 3/5 | Kitchen Sink | HIGH |

### Column Definitions

#### 1. Module/File
**Type:** String
**Description:** File path or module name
**Example:** `src/services/user_service.py`

#### 2. SRP Violation
**Type:** Boolean (YES/NO)
**Description:** Does this module violate Single Responsibility Principle?
**Criteria:**
- YES if module has >1 reason to change
- YES if module name contains "AND" or is vague ("Manager", "Utility")

#### 3. God Object Indicator
**Type:** Enum (CRITICAL/HIGH/MED/LOW)
**Description:** Severity of God Object anti-pattern

**Scoring:**
- **CRITICAL:** >1000 lines OR >50 methods
- **HIGH:** >500 lines OR >20 methods OR multiple responsibilities
- **MED:** >200 lines OR >10 methods OR some coupling
- **LOW:** <200 lines AND <10 methods AND focused

#### 4. AI Slop Indicator
**Type:** Boolean (YES/NO)
**Description:** Exhibits characteristics of [[ai-slop-anatomy|AI Slop]]

**Criteria (any YES = YES):**
- Over-engineered (unnecessary abstractions)
- Verbose without clarity
- Missing edge case handling
- Hallucinated APIs/functions
- Copy-paste code blocks

#### 5. Cognitive Load
**Type:** Integer (1-7)
**Description:** Mental effort to understand module

**Scoring:** Based on **Miller's Law** (7±2 items in working memory)
- **1-3:** Easy to grasp (few concepts)
- **4-5:** Moderate effort
- **6-7:** Overwhelming (too many concepts)

**Factors:**
- Number of responsibilities
- Nesting depth
- Variable naming quality
- Control flow complexity

#### 6. Readability
**Type:** Integer (1-5)
**Description:** How easy is it to read?

**Scoring:**
- **5:** Self-documenting, clear names, simple logic
- **4:** Mostly clear with minor issues
- **3:** Requires some effort to understand
- **2:** Confusing, poor names, complex logic
- **1:** Nearly unreadable

#### 7. Testability
**Type:** Integer (1-5)
**Description:** How easy is it to test?

**Scoring:**
- **5:** Pure functions, dependency injection, easy to mock
- **4:** Mostly testable with minor setup
- **3:** Requires significant test setup
- **2:** Difficult to test (tight coupling, side effects)
- **1:** Untestable (God Object, global state)

#### 8. Qualitative Codes/Themes
**Type:** Tags (comma-separated)
**Description:** From [[thematic-analysis-method]]

**Examples:**
- `God Object`
- `Feature Envy`
- `Long Method`
- `Duplicate Code`
- `Tight Coupling`

#### 9. Priority
**Type:** Enum (CRITICAL/HIGH/MED/LOW)
**Description:** Refactoring priority from [[prioritization-matrix]]

**Factors:**
- Business Criticality
- Change Frequency (Code Churn)
- Risk and Inefficiency

## Example: Real Audit

### Project: E-commerce API

| Module | SRP | God Obj | AI Slop | Cog Load | Read | Test | Themes | Priority |
|--------|-----|---------|---------|----------|------|------|--------|----------|
| `api/main.py` | YES | **CRITICAL** | YES | 7/7 | 1/5 | 1/5 | God Object, Tight Coupling, Bloat | **CRITICAL** |
| `services/auth.py` | NO | LOW | NO | 3/7 | 4/5 | 5/5 | Clean, Well-Tested | LOW |
| `services/order.py` | YES | HIGH | YES | 6/7 | 2/5 | 2/5 | Long Methods, Duplicate Code | HIGH |
| `utils/helpers.py` | YES | MED | YES | 5/7 | 3/5 | 3/5 | Kitchen Sink, Unclear Purpose | MED |
| `models/user.py` | NO | LOW | NO | 2/7 | 5/5 | 5/5 | Clean Data Model | LOW |

### Analysis

**Critical Issues:** 1 file (`api/main.py`)
**High Priority:** 1 file (`services/order.py`)
**Total Technical Debt:** 2 files require immediate refactoring

**Action Plan:**
1. Refactor `api/main.py` (God Object) → Extract services
2. Refactor `services/order.py` (Long Methods) → Extract functions
3. Review `utils/helpers.py` (Kitchen Sink) → Consider splitting

## Usage in Vibe Coding OS

### Integration Points

1. **[[audit-phase]]** - Fill grid during systematic audit
2. **[[thematic-analysis-method]]** - Generate Themes/Codes column
3. **[[prioritization-matrix]]** - Determine Priority column
4. **[[boy-scout-workflow]]** - Track improvements over time

### Workflow

```
1. Run [[thematic-analysis-method]]
   ↓
2. Fill Audit Grid
   ↓
3. Apply [[prioritization-matrix]]
   ↓
4. Generate Code Health Report
   ↓
5. Create Refactoring Backlog
```

## Output: Code Health Report

### Summary Section

```
📊 Code Health Report - Project: E-commerce API
Generated: 2025-11-10

Total Files Audited: 25
God Objects: 1 (CRITICAL)
High Priority Issues: 3
AI Slop Detected: 8 files

Overall Health Score: 6.2/10
```

### Detailed Findings

```
🚨 CRITICAL Issues:
- api/main.py: God Object (1,247 lines, 63 methods)
  → Extract UserService, OrderService, PaymentService

⚠️ HIGH Priority:
- services/order.py: Long Methods + Duplicate Code
  → Apply Extract Method refactoring
```

## Tips

### 1. Be Consistent
Use same scoring criteria across entire codebase.

### 2. Involve Team
Have 2-3 people score independently, then discuss discrepancies.

### 3. Track Over Time
Re-run audit quarterly to measure improvement.

### 4. Focus on Patterns
Look for systemic issues, not just individual files.

## Tools

### Automated Metrics
- **Cyclomatic Complexity:** `radon cc`
- **Lines of Code:** `cloc`
- **Code Churn:** `git log --numstat`

### Manual Review
- Cognitive Load (human judgment)
- Readability (human judgment)
- Thematic Analysis (human judgment)

## Template Files

### CSV Template

```csv
Module,SRP_Violation,God_Object,AI_Slop,Cognitive_Load,Readability,Testability,Themes,Priority
file1.py,NO,LOW,NO,3,4,4,Clean,LOW
file2.py,YES,HIGH,YES,7,2,1,"God Object,Bloat",CRITICAL
```

### Google Sheets Template

[Link to template] (TODO: Create shareable template)

---

**Last Updated:** 2025-11-10
**Maintainer:** Vibe Coding OS Project
