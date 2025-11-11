# Agency Toolkit Refactoring - Execution Order

## 🎯 The Right Order (Based on Real Analysis)

### Phase 1: Foundation (BLOCKING everything)
**Status:** CRITICAL - Must do first

#### Epic 1: Fix load_config (CC: 20 → <10)
- **Time:** 3 hours
- **Risk:** LOW (pure refactoring)
- **Impact:** HIGH (every command uses this)
- **AI-Safe:** ✅ YES (atomic tasks)

**Why First?**
- Worst complexity hotspot in entire codebase
- Called by every command on startup
- Blocks nothing (can be done immediately)

---

### Phase 2: Core Architecture (ENABLES future features)
**Status:** HIGH PRIORITY - Do second

#### Epic 2: Task Handler Plugin System
- **Time:** 7.5 hours
- **Risk:** MEDIUM (changes orchestrator)
- **Impact:** CRITICAL (enables extensibility)
- **AI-Safe:** ⚠️ MOSTLY (needs validation at Task 2.6)

**Why Second?**
- Current TASK_REGISTRY is anti-pattern
- 4 handlers is manageable (not 8+)
- Epic 1 proves tests are robust enough
- Sets up architecture for future growth

**Dependencies:**
- None! Can start after Epic 1 merges

---

### Phase 3: Command Complexity (POLISH)
**Status:** MEDIUM PRIORITY - Do third

#### Epic 3.1: Refactor commands/os.py::_execute_batch (CC: 17 → <10)
- **Time:** 2 hours
- **Risk:** LOW (well-tested)
- **Impact:** MEDIUM (makes batch execution clearer)
- **AI-Safe:** ✅ YES

**Why Third?**
- Benefits from TaskContext type safety (from Epic 2)
- Not blocking other work
- Clear refactor target

---

#### Epic 3.2: Refactor commands/validate.py::_compare_snapshots (CC: 17 → <8)
- **Time:** 2 hours
- **Risk:** LOW
- **Impact:** MEDIUM
- **AI-Safe:** ✅ YES

**Strategy:**
```python
# Split into 3 functions:
1. _load_snapshot(path) -> dict
2. _compute_diff(snap1, snap2) -> dict
3. _format_diff_output(diff, format) -> str
```

---

#### Epic 3.3: Refactor commands/info.py::providers_status (CC: 15 → <8)
- **Time:** 1.5 hours
- **Risk:** LOW
- **Impact:** LOW (informational command)
- **AI-Safe:** ✅ YES

**Strategy:**
```python
class ProviderStatusChecker:
    def check_mistral(self) -> ProviderStatus: ...
    def check_replicate(self) -> ProviderStatus: ...
    def check_all(self) -> list[ProviderStatus]: ...
```

---

#### Epic 3.4: Refactor commands/social.py::social (CC: 13 → <8)
- **Time:** 1.5 hours
- **Risk:** MEDIUM (frequently used command)
- **Impact:** MEDIUM
- **AI-Safe:** ✅ YES

**Strategy:**
- Extract CSV batch logic to separate function
- Extract single post creation
- Main function becomes orchestrator

---

### Phase 4: Polish (NICE TO HAVE)
**Status:** LOW PRIORITY - Do if time permits

#### Epic 4.1: Type Hints on Public APIs
- **Time:** 2 hours
- **AI-Safe:** ✅ YES

#### Epic 4.2: Improve Error Messages
- **Time:** 1 hour
- **AI-Safe:** ✅ YES

#### Epic 4.3: Add Architecture Diagrams
- **Time:** 1 hour
- **AI-Safe:** ✅ YES

---

## 📊 Summary Timeline

| Phase | Epic | Time | Cumulative | Status |
|-------|------|------|------------|--------|
| 1 | Epic 1: load_config | 3h | 3h | 🔴 MUST DO |
| 2 | Epic 2: Task Handlers | 7.5h | 10.5h | 🔴 MUST DO |
| 3 | Epic 3.1: _execute_batch | 2h | 12.5h | 🟡 SHOULD DO |
| 3 | Epic 3.2: _compare_snapshots | 2h | 14.5h | 🟡 SHOULD DO |
| 3 | Epic 3.3: providers_status | 1.5h | 16h | 🟡 SHOULD DO |
| 3 | Epic 3.4: social command | 1.5h | 17.5h | 🟡 SHOULD DO |
| 4 | Epic 4.x: Polish | 4h | 21.5h | 🟢 NICE TO HAVE |

---

## 🎯 Minimum Viable Refactor (MVP)

**For a showcase-ready project:**

✅ **MUST HAVE:**
- Epic 1: load_config (3h)
- Epic 2: Task Handlers (7.5h)
- **Total: 10.5 hours**

⚠️ **SHOULD HAVE (for demo):**
- Epic 3.1: _execute_batch (2h)
- Epic 3.2: _compare_snapshots (2h)
- **Total: 14.5 hours**

🟢 **NICE TO HAVE:**
- Remaining complexity fixes + polish
- **Total: 21.5 hours**

---

## 🚀 Execution Strategy for AI Agents

### Week 1: Foundation
**Monday:** Epic 1 Tasks 1.1-1.3 (2h)
**Tuesday:** Epic 1 Tasks 1.4-1.6 (1h) + PR review
**Wednesday:** Merge Epic 1

### Week 2: Core Architecture
**Monday:** Epic 2 Tasks 2.1-2.3 (1.5h)
**Tuesday:** Epic 2 Task 2.4 (1h)
**Wednesday:** Epic 2 Task 2.5 (3h)
**Thursday:** Epic 2 Tasks 2.6-2.8 (1.5h) + PR review
**Friday:** Merge Epic 2

### Week 3: Polish (Optional)
**Monday-Tuesday:** Epic 3.1-3.2 (4h)
**Wednesday:** Epic 3.3-3.4 (3h)
**Thursday:** Epic 4.x (if time)
**Friday:** Final showcase prep

---

## 🎪 What Changes After This?

### Before Refactor:
```python
# utils.py
def load_config():  # CC: 20, god function
    # 100+ lines of if/elif/try/except
    pass

# core/task_handlers.py
TASK_REGISTRY = {
    "ai": lambda task, ctx: ...,  # fragile
    "social": lambda task, ctx: ...,
}

# orchestrator.py
handler = TASK_REGISTRY.get(tool)
if not handler:
    raise ValueError("Unknown")
output = handler(task, context)  # untyped
```

### After Refactor:
```python
# utils.py
def load_config() -> Config:  # CC: 5, orchestrator
    file_config = _load_config_file() or {}
    merged = _merge_env_vars(file_config)
    complete = _apply_defaults(merged)
    return Config(**complete)

# tasks/ai_handler.py
class AITaskHandler(TaskHandler):  # extensible
    def validate_params(self, params): ...
    def execute(self, params, context: TaskContext): ...

# orchestrator.py
handler = get_task_handler(tool)  # typed
handler.validate_params(params)   # fail-fast
output = handler.execute(params, TaskContext(...))
```

---

## 🎯 Success Metrics

### Technical Metrics
- [ ] No function with CC > 10
- [ ] All tests pass (100% pass rate)
- [ ] Type hints on all public APIs
- [ ] CI/CD pipeline green

### Showcase Metrics
- [ ] "GRAND AGENCY OS" demo works flawlessly
- [ ] Code is readable by other developers
- [ ] Architecture is extensible
- [ ] Error messages are helpful

---

## 🤝 For Your AI Agent

**Start with Epic 1, Task 1.1:**
```bash
Read and analyze agency_toolkit/utils.py::load_config
Show me the current code structure and all branches
```

**Don't jump ahead!** Each task depends on the previous one.
