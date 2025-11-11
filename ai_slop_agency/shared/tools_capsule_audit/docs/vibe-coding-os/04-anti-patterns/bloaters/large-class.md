---
id: large-class
type: anti-pattern
category: anti-patterns
severity: high
tags: [bloater, god-object, srp-violation]
related:
  - god-object-pattern
  - srp-single-responsibility
version: 1.0.0
---

# Large Class

## Definition

A class with too many methods, fields, or lines of code.

## Heuristics

- Class >500 lines
- Class >20 methods
- Class >10 instance variables
- Class name is vague ("Manager", "Handler")

## Problems

- Violates SRP
- High cognitive load
- Difficult to test
- Tight coupling
- Merge conflicts

## Detection

Use [[audit-grid-template]]:
- God Object Indicator: HIGH
- SRP Violation: YES
- Cognitive Load: 6-7/7

## Refactoring

1. **Extract Class** - Move related methods to new class
2. **Extract Subclass** - Create specialized versions
3. **Extract Interface** - Define protocol

See: [[god-object-pattern]] for detailed refactoring strategy

---

**Last Updated:** 2025-11-10
