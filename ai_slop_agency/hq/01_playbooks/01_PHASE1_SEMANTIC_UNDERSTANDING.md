# Phase 1: Semantic Understanding Protocol

**Purpose:** Transform ambiguous client request into verifiable, actionable scope

**Core Rule:** NO ASSUMPTIONS. If unclear, mark as CRITICAL UNKNOWN.

---

## Step 1: Request Classification

Identify project type:
- **Audit:** Analyze existing codebase
- **Build:** Create new feature/system
- **Refactor:** Improve existing code
- **Investigation:** Diagnose issue

## Step 2: Extract Facts ONLY

List objective facts from request:
- Technologies mentioned
- Explicit requirements
- Stated constraints
- Specific pain points

**Anti-Pattern:** "The client probably wants..." → STOP. That's speculation.

## Step 3: Identify Knowledge Gaps

What information is MISSING to proceed?

Categories:
- **Technical:** What technologies/versions?
- **Scope:** What's included/excluded?
- **Success Criteria:** How is success measured?
- **Constraints:** Budget? Timeline? Team size?

**These become research questions in Phase 2.**

## Step 4: Generate Pre-Research Questions

For each knowledge gap, create investigative questions:

1. **Technical Questions:** "What is current Django version?"
2. **Validation Questions:** "How can we MEASURE performance improvement?"
3. **Scope Questions:** "Is frontend in scope or backend only?"
4. **Risk Questions:** "What are known security issues with this stack?"

## Step 5: Anti-Bullshit Check

Before proceeding to Phase 2:

- □ No assumptions made
- □ Facts vs interpretations separated
- □ Knowledge gaps explicitly listed
- □ Validation method identified (how to prove success)

---

## Example: BAD vs GOOD

### ❌ BAD (Speculation)
> "Client wants to improve their Django app. It's probably slow because of N+1 queries. We should refactor the ORM and maybe add caching."

**Problems:**
- Assumes performance issue
- Assumes root cause (N+1)
- Jumps to solution
- No validation plan

### ✅ GOOD (Semantic Understanding)
> **Request Classification:** Audit + Investigation
>
> **Facts Extracted:**
> 1. Django application (version unknown)
> 2. Client reports "slow performance" (no metrics provided)
> 3. Backend only
>
> **Knowledge Gaps:**
> 1. What Django version?
> 2. What specific operations are slow?
> 3. Current response times? (baseline metrics)
> 4. Database type and size?
>
> **Pre-Research Questions:**
> - Technical: Django version, database type, current architecture
> - Validation: How to MEASURE performance? (need profiling tools)
> - Scope: Which endpoints/operations to audit?
>
> **Next Step:** Phase 2 research on Django profiling tools, performance best practices

---

## Template Location

`00_scoping_and_research/01_input_analysis.md`

Generated automatically by:
```bash
vibe new-project --client <name> --name <project>
```
