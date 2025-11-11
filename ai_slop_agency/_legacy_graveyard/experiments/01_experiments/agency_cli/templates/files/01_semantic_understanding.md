# Semantic Understanding Protocol
Date: {date}
Project: {project_name}

## Step 1: Extract Facts

RAW CLIENT INPUT:
```
{client_input}
```

EXTRACTED FACTS:
- Technology: [FILL: What tech stack was mentioned?]
- Problem Type: [FILL: Performance/Bug/Feature/Refactor/New?]
- Explicit Constraints: [FILL: Budget/Timeline/Tech mentioned?]
- Implicit Context: [FILL: What's NOT said but matters?]

## Step 2: Identify Knowledge Gaps

CRITICAL UNKNOWNS (answer before proceeding):
- [ ] Tech stack versions?
- [ ] Environment (local/staging/production)?
- [ ] Scale (users/requests)?
- [ ] Timeline expectations?
- [ ] Budget constraints?
- [ ] [Add more...]

## Step 3: Classification

PROBLEM CATEGORY: [Performance/Security/Architecture/Feature/Bug/Analysis]

REQUIRED KNOWLEDGE DOMAINS:
- [Domain 1: e.g. "Django ORM optimization"]
- [Domain 2: e.g. "PostgreSQL indexing"]
- [Add more...]

## Step 4: Research Questions

BEFORE researching, what must we find out?

TECHNICAL QUESTIONS:
- "What's current best practice for [X] in 2024?"
- "What tools exist to detect/solve [PROBLEM]?"
- [Add more...]

VALIDATION QUESTIONS:
- "How can we MEASURE if [X] is the problem?"
- "What metrics prove [Y] is working?"
- [Add more...]

## Next Steps
- [ ] Run: `agency research "[topic]"` for each domain
- [ ] Fill knowledge gaps by talking to client
- [ ] Proceed to Knowledge Acquisition phase
