# CLIENT_TEMPLATE

**Template for KDAF-compliant client projects**

## Directory Structure

```
CLIENT_TEMPLATE/
├── 00_INTAKE/          Initial requirements and scope
├── 01_AUDIT_DATA/      Raw analysis outputs
├── 02_REFACTORING/     Curated fixes after triage
└── 03_DELIVERABLES/    Final deliverables
```

## Workflow

### Phase 1: INTAKE (00_INTAKE/)
1. Gather client requirements
2. Define scope and objectives
3. Document technical context

### Phase 2: AUDIT (01_AUDIT_DATA/)
1. Run analysis: `kdaf_orchestrator.py run_audit --target "<client-name>"`
2. Outputs:
   - security.json
   - complexity.json
   - ai_slop.json
   - god_object.json

### Phase 3: REFACTORING (02_REFACTORING/)
1. Triage findings: `kdaf_orchestrator.py triage --input "01_AUDIT_DATA/security.json"`
2. Outputs:
   - security_critical.json
   - security_manual_review.json
   - security_auto_safe.json

### Phase 4: DELIVERABLES (03_DELIVERABLES/)
1. Apply fixes: `kdaf_orchestrator.py fix --input "02_REFACTORING/security_critical.json"`
2. Generate reports
3. Package artifacts

## Notes

- Each phase builds on the previous
- All outputs are preserved for audit trail
- Timestamps ensure chronological tracking
