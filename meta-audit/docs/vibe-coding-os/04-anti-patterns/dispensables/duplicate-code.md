---
id: duplicate-code
type: anti-pattern
category: anti-patterns
severity: medium
tags: [dispensable, dry-violation, maintainability]
related:
  - dry-principle
  - boy-scout-rule
version: 1.0.0
---

# Duplicate Code

## Definition

Same or similar code appears in multiple places.

## Detection

- Copy-pasted blocks
- Similar method names with slight variations
- Repeated logic across files

## Problems

- Violates [[dry-principle|DRY]] (Don't Repeat Yourself)
- Bug fixes must be applied multiple times
- Inconsistency risk
- Higher maintenance cost

## Example

```python
# ❌ Duplicate Code
def calculate_order_total(order):
    total = sum(item.price * item.quantity for item in order.items)
    tax = total * 0.08
    return total + tax

def calculate_invoice_total(invoice):
    total = sum(line.price * line.qty for line in invoice.lines)
    tax = total * 0.08
    return total + tax
```

## Refactoring

```python
# ✅ DRY
def calculate_total_with_tax(items, tax_rate=0.08):
    """Calculate total with tax for any item collection."""
    total = sum(item.price * item.quantity for item in items)
    return total * (1 + tax_rate)

def calculate_order_total(order):
    return calculate_total_with_tax(order.items)

def calculate_invoice_total(invoice):
    return calculate_total_with_tax(invoice.lines)
```

## Boy Scout Rule

When you see duplicate code, apply [[boy-scout-rule]]:
Extract and deduplicate immediately.

---

**Last Updated:** 2025-11-10
