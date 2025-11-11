---
id: clear-framework
type: framework
category: ai-governance
tags: [ai-review, code-review, governance, clear]
related:
  - docs-template
  - small-cls-rule
  - code-review-practice
  - ai-as-junior-dev
version: 1.0.0
---

# CLEAR Framework for AI Code Review

## Problem Statement

Traditional code review processes **fail for AI-generated code** due to:

1. **Comprehension Gap** - Reviewer doesn't understand code they didn't write
2. **False Confidence** - "AI wrote it, must be good"
3. **Speed Mismatch** - AI generates code faster than humans can review
4. **Missing Context** - No commit history or incremental changes

## The Solution: CLEAR

**CLEAR** is a structured framework for reviewing AI-generated code.

## The CLEAR Acronym

### **C** - Context

**Review the original prompt and conversation.**

#### Why It Matters
AI output quality = Prompt quality. Bad prompt → Bad code.

#### Actions
- ✅ Read the original prompt that generated the code
- ✅ Review the entire conversation thread (if iterative)
- ✅ Verify the prompt contained necessary context
- ✅ Check if business requirements were clear

#### Red Flags
- ❌ Vague prompt: "Build authentication"
- ❌ Missing constraints: No mention of security requirements
- ❌ No examples: Prompt didn't include expected behavior

#### Example

```markdown
## Context Review

Original Prompt:
"Create a user authentication system"

❌ Issues Found:
- No security requirements specified
- No mention of password hashing
- No rate limiting requirements
- No session management strategy

✅ Recommendation:
Revise prompt to include:
- OWASP Top 10 compliance
- bcrypt password hashing
- JWT session management
- Rate limiting (5 attempts/hour)
```

---

### **L** - Layered

**Review in layers: Structure, Logic, Security.**

#### Why It Matters
Cognitive overload if you try to review everything at once.

#### Layers

**Layer 1: Structure**
- Is the code organized logically?
- Are there clear boundaries between concerns?
- Does it follow [[srp-single-responsibility|SRP]]?

**Layer 2: Logic**
- Does the code actually solve the problem?
- Are edge cases handled?
- Are there logical errors?

**Layer 3: Security**
- Are inputs validated?
- Are there injection vulnerabilities?
- Is sensitive data protected?

**Layer 4: Performance** (optional)
- Are there obvious inefficiencies?
- Will it scale?

#### Example

```python
# AI-Generated Code
def authenticate_user(username, password):
    user = db.query(f"SELECT * FROM users WHERE username='{username}'")
    if user and user.password == password:
        return user
    return None
```

**Layer 1 - Structure:** ✅ Simple function
**Layer 2 - Logic:** ❌ No handling for user not found
**Layer 3 - Security:**
- ❌ **CRITICAL**: SQL Injection vulnerability
- ❌ **CRITICAL**: Plain text password comparison
- ❌ No rate limiting

**Verdict:** **REJECT** - Critical security issues

---

### **E** - Explicit

**Verbalize and mentally execute the code.**

#### Why It Matters
Reading ≠ Understanding. Force yourself to trace execution.

#### Actions
- ✅ Read the code **out loud** (or write explanation)
- ✅ Trace execution with example inputs
- ✅ Explain what each block does
- ✅ If you can't explain it, **you don't understand it**

#### Technique: Rubber Duck Debugging

Explain the code to an imaginary rubber duck (or colleague).

If you stumble or say "it just works," you don't understand it.

#### Example

```python
def process_order(order_id):
    order = get_order(order_id)
    if order.status == 'pending':
        charge_card(order.payment_info)
        send_confirmation(order.user.email)
        update_inventory(order.items)
        order.status = 'completed'
        save_order(order)
```

**Explicit Review (talking through it):**

"This function processes an order. First, it fetches the order... wait, what if `get_order` returns None? There's no null check.

Next, it checks if status is pending... but what if the order was already processed? We'd charge the card twice!

Then it charges the card... what if that fails? We'd send a confirmation email for a failed payment!"

**Issues Found:**
- ❌ Missing null check
- ❌ No idempotency (can charge twice)
- ❌ No error handling for failed payment

---

### **A** - Alternative

**Is this the best solution, or just the first?**

#### Why It Matters
AI generates the **most common** solution, not necessarily the **best** solution.

#### Questions to Ask

1. **Is there a simpler approach?**
   - Can we use a library instead of custom code?
   - Is this over-engineered?

2. **Are there better patterns?**
   - Should this be async?
   - Should we use dependency injection?

3. **What did we reject?**
   - Did AI consider alternatives?
   - Why is this approach chosen?

#### Example

```python
# AI-Generated Code
class DataProcessor:
    def __init__(self):
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.loader = DataLoader()

    def process(self, data):
        validated = self.validator.validate(data)
        transformed = self.transformer.transform(validated)
        return self.loader.load(transformed)
```

**Alternative Review:**

"This is over-engineered. We don't need three classes for a simple pipeline."

**Better Alternative:**

```python
def process_data(data):
    """Process data: validate → transform → load."""
    validate(data)
    return load(transform(data))
```

**Simpler, clearer, same functionality.**

---

### **R** - Refactoring

**Ensure compliance with wiki standards.**

#### Why It Matters
AI doesn't know your team's conventions or [[common-language|common language]].

#### Actions
- ✅ Check against [[common-language]] style guide
- ✅ Verify naming conventions
- ✅ Ensure consistent error handling
- ✅ Apply [[boy-scout-rule]]: Leave it better than you found it

#### Checklist

- [ ] Follows team naming conventions?
- [ ] Uses team's error handling pattern?
- [ ] Includes appropriate tests?
- [ ] Documentation matches team format?
- [ ] No [[ai-slop-anatomy|AI Slop]] indicators?

#### Example

```python
# AI-Generated (doesn't match team style)
def getUserData(userId):
    try:
        return db.get(userId)
    except:
        return None

# Refactored (team conventions)
def get_user_data(user_id: int) -> Optional[User]:
    """
    Retrieve user data by ID.

    Args:
        user_id: User ID

    Returns:
        User object or None if not found

    Raises:
        DatabaseError: If database connection fails
    """
    try:
        return db.get(user_id)
    except RecordNotFound:
        return None
    except DatabaseError as e:
        logger.error(f"Database error fetching user {user_id}: {e}")
        raise
```

## CLEAR Checklist Template

See: [[clear-checklist]] in [[10-templates/]]

```markdown
## CLEAR Review: [Feature Name]

### ✅ Context
- [ ] Reviewed original prompt
- [ ] Prompt included necessary context
- [ ] Business requirements clear
- [ ] Constraints specified

### ✅ Layered
- [ ] Structure: Organized and follows SRP
- [ ] Logic: Handles edge cases correctly
- [ ] Security: No vulnerabilities found
- [ ] Performance: No obvious bottlenecks

### ✅ Explicit
- [ ] Can explain what code does
- [ ] Mentally traced execution
- [ ] No "magic" or unclear sections

### ✅ Alternative
- [ ] Considered simpler approaches
- [ ] Evaluated different patterns
- [ ] Documented why this approach chosen

### ✅ Refactoring
- [ ] Follows team conventions
- [ ] Naming consistent
- [ ] Error handling appropriate
- [ ] Tests included
- [ ] No AI Slop indicators

## Verdict: ✅ APPROVED / ⚠️ NEEDS REVISION / ❌ REJECTED

Notes: [Any additional comments]
```

## Integration with Vibe Coding OS

### In [[vibe-phase]]
- Developer generates code with AI
- Developer applies CLEAR before committing

### In [[audit-phase]]
- Auditor uses CLEAR to review AI-generated code
- Findings recorded in [[audit-grid-template]]

### In [[code-review-practice]]
- CLEAR is **required** for all AI-generated code
- Part of [[small-cls-rule]] workflow

## Success Metrics

| Metric | Before CLEAR | After CLEAR |
|--------|--------------|-------------|
| AI Code Bugs | High | Low |
| Security Issues | Common | Rare |
| Code Understanding | Poor | Good |
| Refactor Frequency | High | Low |

---

## References

- Google Engineering Practices: Code Review Guide
- OWASP: Secure Code Review Guide

**Last Updated:** 2025-11-10
**Maintainer:** Vibe Coding OS Project
