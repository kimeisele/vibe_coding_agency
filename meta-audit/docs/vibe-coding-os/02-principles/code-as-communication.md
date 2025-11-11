---
id: code-as-communication
type: principle
category: principles
tags: [clean-code, readability, maintainability]
related:
  - clean-code
  - the-antidote
version: 1.0.0
---

# Code as Communication

## Principle

> **Code is read far more often than it is written. Optimize for the reader.**

## The Audience

Who reads your code?
- Future you (6 months later)
- Your teammates
- The next maintainer
- Your code reviewer

## Goals

### 1. Maintainability
Can someone fix a bug without understanding the entire system?

### 2. Scalability
Can someone add features without rewriting everything?

### 3. Readability
Can someone understand what this does in <5 minutes?

## Practices

- Use domain language
- Meaningful names
- Clear structure
- Comments explain WHY, code explains WHAT

## Example

### ❌ Poor Communication

```python
def p(d):
    r = []
    for i in d:
        if i[0] == 'A' and i[1] > 100:
            r.append(i)
    return r
```

### ✅ Clear Communication

```python
def get_active_high_value_users(users):
    """Filter users who are active (status='A') and have orders >$100."""
    return [
        user for user in users
        if user.status == 'ACTIVE' and user.total_orders > 100
    ]
```

**Difference:** 2nd version communicates intent.

---

**Last Updated:** 2025-11-10
