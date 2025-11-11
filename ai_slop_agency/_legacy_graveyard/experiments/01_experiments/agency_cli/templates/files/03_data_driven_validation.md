# Data-Driven Validation Protocol
Date: {date}
Project: {project_name}

## Tools Executed

### Code Quality Analysis
Tool: [Name]
Command: `[actual command run]`
Date: {date}

RAW OUTPUT:
```
[PASTE TOOL OUTPUT HERE - UNMODIFIED]
```

SUMMARY (HUMAN ANALYSIS):
- Critical issues: [Count + list]
- Warnings: [Count]
- Most severe: [Describe]

### Security Scan
Tool: [Name]
Command: `[actual command]`

RAW OUTPUT:
```
[PASTE OUTPUT]
```

SUMMARY:
- Vulnerabilities: High [X], Medium [Y], Low [Z]
- Critical findings: [List]

### Performance Profiling
Tool: [Name]
Command: `[actual command]`

RAW OUTPUT:
```
[PASTE OUTPUT]
```

SUMMARY:
- Slowest functions: [List with times]
- Memory usage: [Measured value]
- Database queries: [Count + slow queries]

### Dependency Check
Tool: [Name]
Command: `[actual command]`

RAW OUTPUT:
```
[PASTE OUTPUT]
```

SUMMARY:
- Outdated packages: [Count]
- Vulnerable packages: [List]
- Recommended updates: [List]

## Validation Results

### Finding 1: [Title]
**Evidence:** [Tool name] found [specific issue]
**Severity:** [Critical/High/Medium/Low]
**Source:** Tool output line [X-Y]
**Confidence:** HIGH (measured with tool)

### Finding 2: [Title]
[Same structure...]

## Reality Check (HUMAN ANALYSIS)

DO THESE FINDINGS MAKE SENSE?
- Does this align with client's reported issues?
- Are there contradictions in the data?
- What are we still missing?

PRIORITIZATION (BUSINESS IMPACT):
1. [Finding X] - Why critical: [Business reason]
2. [Finding Y] - Why important: [Reason]

## Next Steps
- [ ] Synthesize all findings (Human task)
- [ ] Run: `agency report` to generate client document
- [ ] Identify areas needing expert validation
