---
id: god-object-pattern
type: anti-pattern
category: audit
severity: critical
tags: [god-object, srp-violation, maintainability, the-blob, code-smell]
related:
  - srp-single-responsibility
  - large-class
  - feature-envy
  - thematic-analysis-method
  - audit-grid-template
sources:
  - "Riel, Arthur J. (1996). Object-Oriented Design Heuristics"
  - "Brown et al. (1998). AntiPatterns: Refactoring Software"
version: 1.0.0
---

# God Object (The Blob)

## Definition

An object that **knows too much or does too much**.

**Also known as:**
- The Blob
- Winnebago
- Swiss Army Knife Class
- Kitchen Sink Object

## Pathology

| Aspect | Impact |
|--------|--------|
| **SRP Violation** | Does multiple unrelated things |
| **Tight Coupling** | Everything depends on it |
| **Low Maintainability** | Changes break unrelated features |
| **Low Testability** | Impossible to unit test in isolation |
| **High Cognitive Load** | Cannot hold entire class in working memory |

## Detection Heuristics

### Quantitative Signals

⚠️ **High Method Count**
- \>20 public methods
- \>50 total methods

⚠️ **High Line Count**
- \>500 lines
- \>1000 lines (critical)

⚠️ **High Cyclomatic Complexity**
- Per-method complexity \>10
- Total class complexity \>100

### Qualitative Signals

⚠️ **Multiple Responsibilities**
- Class name contains "AND": `UserAndOrderManager`
- Class name is vague: `Manager`, `Handler`, `Processor`, `Utility`
- Docstring lists multiple unrelated purposes

⚠️ **Feature Envy**
- Other classes mostly interact with this one
- This class accesses other classes' data frequently

⚠️ **Change Frequency**
- Every feature requires changing this class
- Git blame shows constant modifications

## Example: Python

### ❌ God Object (Before)

```python
class Application:
    """Main application class."""

    def __init__(self):
        self.db = Database()
        self.cache = Cache()
        self.logger = Logger()
        self.config = Config()

    # User Management
    def create_user(self, data): ...
    def update_user(self, id, data): ...
    def delete_user(self, id): ...
    def authenticate_user(self, username, password): ...
    def reset_password(self, email): ...

    # Order Processing
    def create_order(self, user_id, items): ...
    def process_payment(self, order_id, card): ...
    def ship_order(self, order_id): ...
    def cancel_order(self, order_id): ...

    # Reporting
    def generate_sales_report(self, start, end): ...
    def generate_user_report(self): ...
    def export_to_csv(self, data): ...

    # Email
    def send_welcome_email(self, user): ...
    def send_order_confirmation(self, order): ...
    def send_password_reset(self, email): ...

    # UI Rendering
    def render_dashboard(self): ...
    def render_user_profile(self, user_id): ...

    # Database
    def connect_to_database(self): ...
    def execute_query(self, sql): ...
    def backup_database(self): ...

    # ... 30 more methods
```

**Problems:**
- 50+ methods
- 7 distinct responsibilities
- Every change touches this file
- Impossible to test in isolation
- Cannot understand without reading all 2000 lines

### ✅ Refactored (After)

```python
# Separated into focused classes

class UserService:
    """Handles user lifecycle and authentication."""
    def create(self, data): ...
    def update(self, id, data): ...
    def delete(self, id): ...
    def authenticate(self, username, password): ...

class OrderService:
    """Handles order processing and payment."""
    def create_order(self, user_id, items): ...
    def process_payment(self, order_id, card): ...
    def ship(self, order_id): ...

class ReportGenerator:
    """Generates business reports."""
    def sales_report(self, start, end): ...
    def user_report(self): ...

class EmailService:
    """Sends transactional emails."""
    def welcome(self, user): ...
    def order_confirmation(self, order): ...

class Application:
    """Coordinates services."""
    def __init__(self):
        self.users = UserService()
        self.orders = OrderService()
        self.reports = ReportGenerator()
        self.emails = EmailService()
```

**Benefits:**
- Each class has ~5-10 methods
- Single Responsibility Principle
- Easy to test
- Easy to understand
- Changes are localized

## Causality: Vibe Coding → God Objects

> **"Vibe coding (lacking systems thinking) is a God Object factory."**

### Why AI Creates God Objects

1. **No Architectural Vision**
   - AI generates code that "works"
   - Doesn't consider class boundaries

2. **Feature Accretion**
   - New feature → Add method to existing class
   - No one refactors (don't understand it)

3. **Lack of [[srp-single-responsibility|SRP]] Awareness**
   - AI doesn't enforce Single Responsibility
   - Human doesn't review for architecture

### The Vibe Coding Pipeline

```
Vibe Coding Session 1: Add user management
   ↓
Application class: 10 methods

Vibe Coding Session 2: Add orders
   ↓
Application class: 20 methods

Vibe Coding Session 3: Add reports
   ↓
Application class: 35 methods

Vibe Coding Session 10: Add everything
   ↓
Application class: 100 methods ← GOD OBJECT
```

## Refactoring Strategy

See: [[thematic-analysis-method]] for systematic identification

### 1. Extract Classes

Apply **Extract Class** refactoring:

```python
# Identify cohesive groups of methods
User methods → UserService
Order methods → OrderService
```

### 2. Apply SRP

Each class should have **one reason to change**.

See: [[srp-single-responsibility]]

### 3. Use Dependency Injection

Decouple classes:

```python
class Application:
    def __init__(self, user_service, order_service):
        self.users = user_service
        self.orders = order_service
```

## Audit Action

Use [[audit-grid-template]] to score:

| Metric | Score |
|--------|-------|
| **SRP Violation** | YES |
| **God Object Indicator** | HIGH / CRITICAL |
| **Cognitive Load** | 7/7 (too high) |
| **Maintainability** | 1/5 (very low) |
| **Testability** | 1/5 (very low) |

**Priority:** **CRITICAL** - Refactor immediately.

Use [[prioritization-matrix]] to determine order if multiple God Objects exist.

## Prevention

### In Shape Phase
See: [[shape-phase]]

- Define class boundaries **before** coding
- Identify responsibilities upfront
- Create architecture diagram

### In Vibe Phase
See: [[vibe-phase]]

- Provide context-rich prompts
- Include SRP in prompt: "Create focused classes, each with single responsibility"

### In Audit Phase
See: [[audit-phase]]

- Run [[thematic-analysis-method]]
- Use [[audit-grid-template]]
- Catch God Objects early

---

## References

- Martin, Robert C. "Clean Architecture" (2017)
- Fowler, Martin. "Refactoring" (2019)
- Brown et al. "AntiPatterns" (1998)

**Last Updated:** 2025-11-10
**Maintainer:** Vibe Coding OS Project
