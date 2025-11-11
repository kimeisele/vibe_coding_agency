# PROJECT CONTEXT HUB

> **Purpose:** This document provides essential project context to AI assistants. Load this at the beginning of development sessions to ensure consistent, informed responses.
>
> **Last Updated:** [DATE]
> **Project Version:** [VERSION]

---

## 📑 INDEX - IMPORTANT FILES

### Core Documentation
- `[PATH/TO/ARCHITECTURE.md]` - System architecture and design decisions
- `[PATH/TO/API_DOCS.md]` - API endpoints and contracts
- `[PATH/TO/DATABASE_SCHEMA.md]` - Database structure and relationships
- `[PATH/TO/DEPLOYMENT.md]` - Deployment procedures and infrastructure

### Code References
- `[PATH/TO/MAIN_ENTRYPOINT]` - Application entry point
- `[PATH/TO/CORE_MODULE]` - Core business logic
- `[PATH/TO/CONFIG]` - Configuration files

### Development Guides
- `[PATH/TO/CONTRIBUTING.md]` - Development workflow and standards
- `[PATH/TO/TESTING.md]` - Testing strategy and test suite location
- `[PATH/TO/TROUBLESHOOTING.md]` - Common issues and solutions

---

## 🎯 PROJECT OVERVIEW

### Project Name
**[PROJECT_NAME]**

### Mission Statement
[1-2 sentences describing what this project does and why it exists]

### Current Phase
- [ ] Prototype / MVP
- [ ] Active Development
- [ ] Production / Maintenance
- [ ] Legacy / Sunset

### Key Stakeholders
- **Product Owner:** [NAME/ROLE]
- **Tech Lead:** [NAME/ROLE]
- **Primary Maintainers:** [NAMES/ROLES]

---

## 🛠️ TECHNOLOGY STACK

### Core Technologies
| Category | Technology | Version | Notes |
|----------|-----------|---------|-------|
| Language | [e.g., Python] | [e.g., 3.11+] | [Any constraints] |
| Framework | [e.g., FastAPI] | [e.g., 0.104.0] | [Why this choice] |
| Database | [e.g., PostgreSQL] | [e.g., 15.x] | [Schema approach] |
| Cache | [e.g., Redis] | [e.g., 7.x] | [Use cases] |

### Frontend (if applicable)
| Technology | Version | Notes |
|-----------|---------|-------|
| [e.g., React] | [e.g., 18.x] | [State management approach] |
| [e.g., TypeScript] | [e.g., 5.x] | [Strict mode enabled] |

### Infrastructure
| Component | Technology | Notes |
|-----------|-----------|-------|
| Cloud Provider | [e.g., AWS] | [Key services used] |
| CI/CD | [e.g., GitHub Actions] | [Pipeline stages] |
| Monitoring | [e.g., Datadog] | [Key metrics tracked] |
| Logging | [e.g., ELK Stack] | [Log levels and rotation] |

### Development Tools
- **Package Manager:** [e.g., Poetry, npm]
- **Linter:** [e.g., Ruff, ESLint]
- **Formatter:** [e.g., Black, Prettier]
- **Type Checker:** [e.g., mypy, TypeScript]
- **Test Framework:** [e.g., pytest, Jest]

### Prohibited Technologies
> **DO NOT USE** the following without explicit team approval:
- [Technology/Library - Reason why it's prohibited]
- [Technology/Library - Reason why it's prohibited]

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Architecture
```
[High-level diagram or ASCII representation]

Example:
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client    │─────▶│   API GW    │─────▶│  Services   │
└─────────────┘      └─────────────┘      └─────────────┘
                            │                     │
                            ▼                     ▼
                     ┌─────────────┐      ┌─────────────┐
                     │    Cache    │      │  Database   │
                     └─────────────┘      └─────────────┘
```

### Design Patterns
- **[Pattern Name]:** [Where it's used and why]
- **[Pattern Name]:** [Where it's used and why]

### Key Architectural Decisions
1. **[Decision Title]**
   - **Context:** [Why this was needed]
   - **Decision:** [What was chosen]
   - **Consequences:** [Trade-offs accepted]

---

## 📁 PROJECT STRUCTURE

### Directory Layout
```
[project-root]/
├── [src/core/]          # [Core business logic]
├── [src/api/]           # [API endpoints and routes]
├── [src/models/]        # [Data models and schemas]
├── [src/services/]      # [Business services]
├── [src/utils/]         # [Utility functions]
├── [tests/]             # [Test suite]
├── [docs/]              # [Documentation]
└── [scripts/]           # [Build and deployment scripts]
```

### Module Responsibilities
- **`[module_name]/`** - [Responsibility and scope]
- **`[module_name]/`** - [Responsibility and scope]
- **`[module_name]/`** - [Responsibility and scope]

### Critical Files
- **`[file_path]`** - [What it does, when to modify]
- **`[file_path]`** - [What it does, when to modify]

---

## 📋 CODE CONVENTIONS

### Naming Conventions
```python
# [Language-specific examples]

# Files
module_name.py          # Snake case for modules
ComponentName.tsx       # PascalCase for components

# Variables & Functions
user_count = 0          # Snake case for variables
def calculate_total()   # Snake case for functions

# Classes
class UserService:      # PascalCase for classes

# Constants
MAX_RETRY_COUNT = 3     # UPPER_CASE for constants
```

### Code Style Rules
- **Indentation:** [e.g., 4 spaces, no tabs]
- **Line Length:** [e.g., 88 characters max]
- **Imports:** [e.g., Grouped by stdlib/third-party/local]
- **Docstrings:** [e.g., Google style, include examples]
- **Type Hints:** [e.g., Required for all public functions]

### Error Handling
```python
# [Project-specific error handling pattern]
try:
    # Business logic
    pass
except SpecificException as e:
    logger.error(f"Context: {e}")
    raise CustomException("User-facing message") from e
```

### Logging Standards
```python
# [Logging pattern used in project]
logger.debug("Detailed diagnostic info")
logger.info("Important business events")
logger.warning("Recoverable issues")
logger.error("Errors requiring attention")
logger.critical("System-critical failures")
```

---

## 🔒 SECURITY GUIDELINES

### Authentication & Authorization
- **Auth Method:** [e.g., JWT, OAuth2]
- **Session Management:** [How sessions are handled]
- **Permission Model:** [RBAC, ABAC, etc.]

### Sensitive Data Handling
- **API Keys:** [Where stored, how accessed]
- **Secrets Management:** [e.g., AWS Secrets Manager, .env files]
- **PII Data:** [How personal data is protected]

### Security Requirements
- ✅ All external inputs must be validated
- ✅ SQL queries must use parameterized statements
- ✅ Passwords must be hashed with [e.g., bcrypt]
- ✅ HTTPS required for all external communications
- ❌ Never log sensitive data (passwords, tokens, PII)
- ❌ Never commit secrets to version control

---

## 🧪 TESTING STRATEGY

### Test Coverage Requirements
- **Unit Tests:** [Target coverage: e.g., 80%+]
- **Integration Tests:** [Key flows that must be covered]
- **E2E Tests:** [Critical user journeys]

### Test Structure
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Tests with external dependencies
└── e2e/            # Full system tests
```

### Running Tests
```bash
# [Commands to run test suite]
[e.g., pytest tests/]
[e.g., npm test]
```

### Test Data
- **Fixtures:** [Location and usage]
- **Mocking:** [What to mock, what not to mock]
- **Test Database:** [Setup and teardown approach]

---

## 🚀 DEPLOYMENT

### Environments
| Environment | Purpose | URL | Deploy Method |
|------------|---------|-----|---------------|
| Development | [Local dev] | [localhost] | [Manual] |
| Staging | [Testing] | [staging.url] | [CI/CD] |
| Production | [Live] | [prod.url] | [CI/CD + Approval] |

### Deployment Process
1. [Step 1: e.g., Create PR]
2. [Step 2: e.g., Pass CI checks]
3. [Step 3: e.g., Code review approval]
4. [Step 4: e.g., Merge to main]
5. [Step 5: e.g., Auto-deploy to staging]
6. [Step 6: e.g., Manual promotion to prod]

### Environment Variables
```bash
# Required variables
[VAR_NAME]=[description]
[VAR_NAME]=[description]

# Optional variables
[VAR_NAME]=[description] # Default: [value]
```

---

## 🗄️ DATA MODELS

### Core Entities
#### [Entity Name 1]
```python
# [Primary data structure]
{
    "field_name": "type",  # [Purpose and constraints]
    "field_name": "type",  # [Purpose and constraints]
}
```

#### [Entity Name 2]
```python
# [Primary data structure]
{
    "field_name": "type",  # [Purpose and constraints]
}
```

### Entity Relationships
```
[Entity A] ──< has many >── [Entity B]
[Entity C] ──< belongs to >── [Entity A]
```

### Database Schema
- **Migration Tool:** [e.g., Alembic, Flyway]
- **Migration Location:** [e.g., migrations/]
- **Schema Version:** [Current version]

---

## 🔗 EXTERNAL DEPENDENCIES

### Third-Party APIs
| Service | Purpose | Auth Method | Rate Limits | Docs |
|---------|---------|-------------|-------------|------|
| [API Name] | [What it's used for] | [Auth type] | [Limits] | [URL] |

### External Services
- **[Service Name]:** [Purpose, configuration, failover strategy]

### Service Dependencies
```
[Your Service]
  ├── depends on → [Service A] (critical)
  ├── depends on → [Service B] (optional)
  └── provides to → [Service C]
```

---

## 🐛 KNOWN ISSUES & TECHNICAL DEBT

### Active Issues
1. **[Issue Title]**
   - **Impact:** [How it affects the system]
   - **Workaround:** [Temporary solution if any]
   - **Planned Fix:** [When/how it will be addressed]

### Technical Debt
1. **[Debt Item]**
   - **Location:** [Where in codebase]
   - **Reason:** [Why it exists]
   - **Priority:** [High/Medium/Low]

---

## 📊 PERFORMANCE CONSIDERATIONS

### Performance Targets
- **API Response Time:** [e.g., p95 < 200ms]
- **Database Query Time:** [e.g., p99 < 100ms]
- **Throughput:** [e.g., 1000 req/s]

### Known Bottlenecks
- **[Component/Operation]:** [Description and mitigation]

### Optimization Guidelines
- [Guideline 1]
- [Guideline 2]

---

## 📞 SUPPORT & ESCALATION

### Getting Help
- **Documentation:** [URL to internal docs]
- **Team Chat:** [Slack channel, Discord, etc.]
- **Issue Tracker:** [GitHub Issues, Jira, etc.]

### On-Call & Incidents
- **On-Call Schedule:** [Where to find it]
- **Incident Response:** [Process and tools]
- **Runbooks:** [Location of operational guides]

---

## 📝 ADDITIONAL CONTEXT

### Business Context
[Any business rules, domain knowledge, or context that affects technical decisions]

### Glossary
- **[Term]:** [Definition specific to this project]
- **[Term]:** [Definition specific to this project]

### Historical Context
[Important context about how the project evolved, major pivots, legacy decisions]

---

## 🔄 REPO MAP

> **Note:** This section should contain the output of a code indexing tool like tree-sitter or ctags.
> It provides the AI with a high-level view of the entire codebase structure.

### Generation Command
```bash
# [Command to regenerate this map]
# e.g., tree-sitter parse src/ > repo_map.txt
```

### Map Content
```
[Paste tree-sitter or similar tool output here]
[This should include function signatures, class definitions, imports, etc.]

Example format:
src/
├── core/
│   ├── user_service.py
│   │   ├── class UserService
│   │   │   ├── def create_user(email: str, password: str) -> User
│   │   │   ├── def authenticate(email: str, password: str) -> Token
│   │   │   └── def get_user_by_id(user_id: int) -> Optional[User]
```

---

## ✅ CONTEXT HUB CHECKLIST

Before loading this Context Hub, ensure:
- [ ] All placeholder values `[LIKE_THIS]` are replaced with actual values
- [ ] Index section points to existing, current files
- [ ] Technology stack versions are up to date
- [ ] Repo Map is freshly generated
- [ ] Known issues section reflects current state
- [ ] Contact information is accurate

---

*This Context Hub should be reviewed and updated quarterly or after major architectural changes.*
