---
id: long-method
type: anti-pattern
category: anti-patterns
severity: medium
tags: [bloater, code-smell, complexity]
related:
  - god-object-pattern
  - cognitive-load
  - srp-single-responsibility
version: 1.0.0
---

# Long Method

## Definition

A method that has grown too long, making it hard to understand and maintain.

## Heuristics

- Method >50 lines
- Method >100 lines (critical)
- Requires scrolling to see entire method
- Multiple levels of nesting (>3)

## Problems

- High cognitive load
- Difficult to test
- Likely violates SRP
- Encourages copy-paste

## Example

```python
# ❌ Long Method
def process_order(order_id):
    # Fetch order (5 lines)
    # Validate customer (10 lines)
    # Check inventory (15 lines)
    # Process payment (20 lines)
    # Update database (10 lines)
    # Send notifications (15 lines)
    # Generate invoice (10 lines)
    # ... 85+ lines total
```

## Refactoring

Apply **Extract Method** pattern:

```python
# ✅ Refactored
def process_order(order_id):
    order = fetch_order(order_id)
    validate_customer(order.customer)
    check_inventory(order.items)
    process_payment(order)
    update_database(order)
    send_notifications(order)
    generate_invoice(order)
```

Each extracted method is <15 lines and focused.

---

**Last Updated:** 2025-11-10
