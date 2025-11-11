---
id: srp-single-responsibility
type: principle
category: principles
tags: [solid, srp, design-principle]
related:
  - god-object-pattern
  - large-class
  - clean-code
version: 1.0.0
---

# Single Responsibility Principle (SRP)

## Definition

> **A class should have only one reason to change.**

From **Robert C. Martin** (SOLID principles)

## What It Means

Each module, class, or function should be responsible for **one thing** and **one thing only**.

## The "Reason to Change" Test

Ask: **"Why would this class need to be modified?"**

If you can list 2+ reasons → **SRP violation**

## Example

### ❌ SRP Violation

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save_to_database(self):
        # Database logic
        pass

    def send_welcome_email(self):
        # Email logic
        pass

    def generate_report(self):
        # Reporting logic
        pass
```

**Reasons to change:**
1. User data structure changes
2. Database schema changes
3. Email template changes
4. Report format changes

**Result:** 4 reasons to change → Violates SRP

### ✅ SRP Compliant

```python
class User:
    """Represents user data."""
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    """Handles user persistence."""
    def save(self, user):
        pass

class EmailService:
    """Sends emails."""
    def send_welcome(self, user):
        pass

class ReportGenerator:
    """Generates reports."""
    def user_report(self, user):
        pass
```

**Each class has 1 reason to change.**

## Benefits

- **Easier to understand** - Clear purpose
- **Easier to test** - Focused tests
- **Easier to maintain** - Changes are localized
- **Lower coupling** - Classes don't depend on unrelated logic

## Connection to God Objects

[[god-object-pattern|God Objects]] are **extreme SRP violations**.

A God Object has 10+ reasons to change.

## Detection in Audit

Use [[audit-grid-template]]:

**SRP Violation column:**
- YES if class has >1 responsibility
- YES if class name contains "AND"
- YES if class name is vague ("Manager", "Utility")

---

**Last Updated:** 2025-11-10
