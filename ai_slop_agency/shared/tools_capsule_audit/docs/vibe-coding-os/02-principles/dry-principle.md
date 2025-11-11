---
id: dry-principle
type: principle
category: principles
tags: [principle, maintainability, pragmatic-programmer]
related:
  - duplicate-code
  - boy-scout-rule
  - pragmatic-programmer
version: 1.0.0
---

# DRY: Don't Repeat Yourself

## Principle

> **"Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."**

From **The Pragmatic Programmer** (Hunt & Thomas)

## What It Means

- Don't duplicate logic
- Don't duplicate data
- Don't duplicate documentation

**Key:** Knowledge, not code. Similar code isn't always duplication.

## Example

### ❌ DRY Violation

```python
def format_user_name(user):
    return f"{user.first_name} {user.last_name}"

def display_user(user):
    name = f"{user.first_name} {user.last_name}"
    print(f"User: {name}")

def email_greeting(user):
    name = f"{user.first_name} {user.last_name}"
    return f"Hello, {name}!"
```

**Problem:** Logic for "full name" is duplicated 3 times.

### ✅ DRY Compliant

```python
def format_user_name(user):
    """Single source of truth for full name."""
    return f"{user.first_name} {user.last_name}"

def display_user(user):
    print(f"User: {format_user_name(user)}")

def email_greeting(user):
    return f"Hello, {format_user_name(user)}!"
```

## Why It Matters

**Scenario:** Business decides full name should be "Last, First"

**Without DRY:** Change 3 places (risk missing one)
**With DRY:** Change 1 place

## DRY vs WET

**WET:** "Write Everything Twice" or "We Enjoy Typing"

Anti-pattern of violating DRY.

## Audit

See: [[duplicate-code]] anti-pattern

Apply [[boy-scout-rule]]: When you see duplication, extract it.

---

**Last Updated:** 2025-11-10
