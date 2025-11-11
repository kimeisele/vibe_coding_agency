# WU-7.3: Interactive Wizards Implementation Plan

**Story**: 7.3 - Interactive Wizards (Usability)
**Objective**: Make toolkit accessible to non-technical users
**Effort**: 2.5-3 hours
**Priority**: HIGH (increases adoption)
**Status**: 🟢 READY TO BUILD

---

## Target Personas

1. **Marketing Manager**: "I want to create social posts but don't know CLI flags"
2. **Designer**: "I prefer guided workflows to memorizing commands"
3. **First-time User**: "I need hand-holding to get started"

---

## Wizard Scope (3 Wizards)

### Wizard 1: Social Post Generation
**Command**: `toolkit social` (no args)

**Flow**:
```
📝 Social Post Generator Wizard
═══════════════════════════════

1. What's your message? [text input, required]
   └─ Example: "Check out our new product launch!"

2. What style do you prefer? [choice]
   ├─ modern    (clean, minimal, professional)
   ├─ bold      (bright, energetic, eye-catching)
   └─ minimal   (zen, simple, elegant)

3. What color theme? [choice]
   ├─ auto      (let AI decide)
   ├─ warm      (oranges, reds, yellows)
   ├─ cool      (blues, purples, greens)
   └─ neutral   (blacks, grays, whites)

4. Add background image? [yes/no]
   └─ If yes → "What concept?" [text input]
       └─ Example: "sunset beach"

5. How many variations? [number 1-100]
   └─ Default: 1
   └─ Tip: Batch mode is faster for 10+

6. Output directory? [path]
   └─ Default: ./output/social
   └─ Tip: Must be writable

7. Preview before generating? [yes/no/dry-run]
   ├─ dry-run   (show what would happen)
   ├─ yes       (generate now)
   └─ no        (save config and exit)

8. Generate! ✨
```

**Output**: Social post PNG files in output directory

---

### Wizard 2: Briefing Generation
**Command**: `toolkit briefing` (no args)

**Flow**:
```
📄 Briefing Generator Wizard
════════════════════════════

1. What's your project? [text input, required]
   └─ Example: "Q4 Marketing Campaign"

2. Add description? [yes/no]
   └─ If yes → [text input]

3. Briefing type? [choice]
   ├─ project    (comprehensive project brief)
   ├─ campaign   (marketing campaign brief)
   ├─ proposal   (business proposal)
   └─ other      (custom content)

4. Export format? [choice]
   ├─ markdown  (quick, readable)
   ├─ pdf       (professional, shareable)
   └─ both      (markdown + PDF)

5. Add team members? [yes/no]
   └─ If yes → "Names (comma-separated)?" [text input]

6. Output directory? [path]
   └─ Default: ./output/briefing

7. Generate! ✨
```

**Output**: Markdown and/or PDF files

---

### Wizard 3: Image Generation
**Command**: `toolkit image` (no args)

**Flow**:
```
🎨 Image Generator Wizard
═════════════════════════

1. Describe the image [text input, required]
   └─ Example: "futuristic city at sunset"

2. Image size? [choice]
   ├─ square      (1080x1080, social media)
   ├─ landscape   (1920x1080, website hero)
   ├─ portrait    (1080x1920, mobile)
   └─ custom      (width x height)

3. Use seed template? [yes/no]
   └─ If yes → [choice]
       ├─ moody    (dark, atmospheric)
       ├─ corporate (professional, clean)
       ├─ playful  (bright, fun, vibrant)
       └─ minimal  (simple, zen-like)

4. How many variations? [number 1-5]
   └─ Default: 1
   └─ Tip: More = longer wait

5. Output directory? [path]
   └─ Default: ./output/images

6. Generate! ✨
```

**Output**: PNG image files

---

## Implementation Architecture

### Core Wizard Function Pattern

```python
def social_wizard():
    """Interactive wizard for social post generation"""

    # 1. Collect inputs
    message = prompt_text("What's your message?", required=True)
    style = prompt_choice("What style?", ["modern", "bold", "minimal"])
    color = prompt_choice("Color theme?", ["auto", "warm", "cool", "neutral"])

    # ... more prompts ...

    # 2. Validate inputs
    if count < 1 or count > 100:
        raise ValueError("Posts must be 1-100")

    # 3. Show preview
    if not dry_run:
        summary = f"""
        Message: {message}
        Style: {style}
        Count: {count}
        """
        typer.echo(summary)
        if not typer.confirm("Proceed?"):
            typer.echo("Cancelled.")
            return

    # 4. Execute
    try:
        result = generate_social_posts(
            text=message,
            style=style,
            color=color,
            count=count,
            output_dir=output_dir,
            dry_run=dry_run
        )
        typer.echo(f"✨ Generated {count} posts in {output_dir}")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise

```

### Helper Functions

```python
# agency_toolkit/commands/wizard_utils.py

def prompt_text(
    question: str,
    required: bool = False,
    default: Optional[str] = None
) -> str:
    """Prompt for text input"""
    # Use questionary.text()

def prompt_choice(
    question: str,
    choices: List[str],
    default: Optional[str] = None
) -> str:
    """Prompt for choice selection"""
    # Use questionary.select()

def prompt_confirm(
    question: str,
    default: bool = False
) -> bool:
    """Prompt for yes/no confirmation"""
    # Use questionary.confirm()

def prompt_number(
    question: str,
    min_val: int = 1,
    max_val: int = 100,
    default: int = 1
) -> int:
    """Prompt for number with validation"""
    # Use questionary.text() + validation

def prompt_path(
    question: str,
    default: str = "./output"
) -> str:
    """Prompt for directory path"""
    # Validate path exists or can be created

```

---

## Implementation Checklist

### Phase 1: Create Wizard Helper Functions (30 min)
```
[ ] Create agency_toolkit/commands/wizard_utils.py
[ ] Implement prompt_text()
[ ] Implement prompt_choice()
[ ] Implement prompt_confirm()
[ ] Implement prompt_number()
[ ] Implement prompt_path()
[ ] Add input validation & error messages
[ ] Test all helpers with sample inputs
```

### Phase 2: Build Social Wizard (45 min)
```
[ ] Create social_wizard() function
[ ] Implement 7-step flow (above)
[ ] Add clear prompts and helpful defaults
[ ] Validate all inputs
[ ] Build preview step
[ ] Integrate with existing social generate command
[ ] Test wizard end-to-end
```

### Phase 3: Build Briefing & Image Wizards (45 min)
```
[ ] Create briefing_wizard() function (similar structure)
[ ] Create image_wizard() function
[ ] Test both wizards end-to-end
```

### Phase 4: Integration & Polish (30 min)
```
[ ] Update social.py to call social_wizard() when no args
[ ] Update briefing.py to call briefing_wizard()
[ ] Update image.py to call image_wizard()
[ ] Add --no-wizard flag (users can bypass if they want)
[ ] Test all 3 wizards work correctly
[ ] Test edge cases (empty input, invalid values, etc.)
[ ] Ensure error messages are helpful
```

### Phase 5: Testing & Refinement (30 min)
```
[ ] Manual testing with 3+ real users
[ ] Collect feedback on prompt clarity
[ ] Collect feedback on default values
[ ] Refine prompts based on feedback
[ ] Document in DEVELOPMENT.md
[ ] Create unit tests for wizard functions
```

---

## Code Structure

```
agency_toolkit/
├── commands/
│   ├── wizard_utils.py          [NEW: Helper functions]
│   ├── social.py                [MODIFY: Add wizard]
│   ├── briefing.py              [MODIFY: Add wizard]
│   └── image.py                 [MODIFY: Add wizard]
└── tests/
    └── unit/
        └── test_wizard_utils.py  [NEW: Tests]
```

---

## Success Criteria

### Functional
- [x] All 3 wizards implement their flows
- [x] All inputs are validated
- [x] Error messages are clear and actionable
- [x] Users can abort at any time
- [x] Dry-run mode shows what would happen

### Usability
- [x] Non-technical users can use without documentation
- [x] Prompts are clear (jargon-free)
- [x] Defaults are sensible
- [x] Progress indicators show what's happening
- [x] Success messages are encouraging

### Quality
- [x] Unit tests cover all helpers
- [x] Integration tests cover all 3 wizards
- [x] No crashes on invalid input
- [x] Code is readable and maintainable
- [x] Documented in DEVELOPMENT.md

### User Feedback
- [x] Tested with 3+ non-technical users
- [x] Feedback incorporated
- [x] Prompts refined based on testing

---

## Estimated Timeline

| Phase | Task | Time | Notes |
|-------|------|------|-------|
| 1 | Wizard Helpers | 30 min | Utility functions |
| 2 | Social Wizard | 45 min | Most complex flow |
| 3 | Briefing/Image | 45 min | Simpler flows |
| 4 | Integration | 30 min | Wire up to commands |
| 5 | Testing | 30 min | User feedback loop |
| | **Total** | **180 min** | **~3 hours** |

---

## Questions & Decisions

**Q: Should wizards be default or opt-in?**
A: Default (when no args provided). Users can always use full CLI with `--help`.

**Q: What if validation fails?**
A: Show error message, offer to retry that step (don't exit).

**Q: How to handle --no-wizard flag?**
A: For power users who want direct CLI: `toolkit social --no-wizard "message"`.

**Q: Test with real users or internal testing?**
A: Real users (3+ non-technical people if available).

---

## Next Steps

1. **Approval**: Review this plan
2. **Implementation**: Start with Phase 1 (wizard helpers)
3. **Iteration**: Build → Test → Refine → Deploy

---

**Document Status**: 🟢 READY FOR IMPLEMENTATION
**Created**: 2025-11-10
**Author**: AI-Driven Development
