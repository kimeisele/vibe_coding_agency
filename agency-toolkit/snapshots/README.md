# Snapshot Testing

This directory contains approved baseline snapshots for regression testing.

## Structure

```
snapshots/
├── approved/          # Golden master snapshots (committed to git)
└── current/           # Current test run outputs (gitignored)
```

## Usage

### 1. Generate Current Snapshots

First, generate artifacts to test:

```bash
# Generate test artifacts manually
toolkit social "Test Message" --style modern --output snapshots/current/social_modern.png
toolkit briefing generate web --output snapshots/current/briefing_web.pdf
toolkit structure create web test-project --output snapshots/current/
```

### 2. Validate Against Approved

Compare current outputs against approved baselines:

```bash
toolkit validate snapshot
```

### 3. Approve New Baselines

If changes are intentional, promote current to approved:

```bash
toolkit validate snapshot --approve
```

## What Gets Validated

- **PDFs**: Text content extraction (layout-agnostic)
- **Images**: SHA-256 hash comparison (pixel-perfect)
- **JSON**: Content comparison (structure and values)

## Best Practices

1. **Commit approved/** to version control
2. **Add current/** to `.gitignore`
3. **Run validation** before merging PRs
4. **Only approve** when changes are intentional
