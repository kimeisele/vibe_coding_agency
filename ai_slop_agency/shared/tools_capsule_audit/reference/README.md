# Capsule Audit - Reusable Component Analysis (V2)

This document summarizes the findings from analyzing `phoenix_2`, `agency_toolkit`, and other related projects to identify reusable components for the `capsule_audit` tool. This version includes a deeper analysis of the `steward context` command.

## Executive Summary

The analysis revealed a powerful combination of components from `phoenix_2` that can serve as the foundation for `capsule_audit`.

1.  **`steward context` for Data Collection**: This command is a sophisticated data aggregation engine, perfect for gathering the raw data needed for an audit. It's the "goldmine" of context.
2.  **`ExploreAgent` for Orchestration & Analysis**: This autonomous agent is the ideal engine for taking the aggregated data and performing a deep, LLM-driven analysis to generate insights and recommendations.

The recommended approach is a hybrid one: use the data collector pattern from `steward context` to gather facts, and feed those facts into an adapted `ExploreAgent` for intelligent analysis.

## Key Findings & Reusable Components

### 1. `phoenix_2` - The Core Engine

- **`steward context` Subcommand (`phoenix_steward_context_subcommand/`)**: This is the "Single Point Of Truth" (SPOT) in `phoenix_2`.
    - **Data Aggregation**: It uses a powerful and extensible collector pattern to gather data from numerous sources (Git, system health, work units, sessions, etc.) via its various `_collectors.py` files. This is a perfect, ready-made architecture for the data gathering phase of `capsule_audit`.
    - **Persistence & State**: It is deeply integrated with session management and a database, providing a robust mechanism for handling persistent state.
    - **RAG Integration**: It has built-in capabilities to integrate with a Retrieval-Augmented Generation (RAG) system (`rag_integration.py`), which is an advanced feature that could be leveraged in the future.

- **`ExploreAgent` (`phoenix_explore_agent/`)**: This is the intelligent analysis engine.
    - **Orchestration**: The agent's core logic (`agent.py`, `planning.py`, `context.py`) provides the plan-execute-reflect loop needed for the "LLM Orchestrator" concept.
    - **Extensible Tools**: The `handlers/` directory provides a system for adding new analysis capabilities, which can be used to act on the data collected by the `steward context`-like collectors.

- **`Explore CLI` (`phoenix_explore_cli/`)**: A well-structured CLI that can be adapted for `capsule_audit`.

### 2. Standalone Packages - Essential Services

- **`prompt_registry_package/`**: A sophisticated package for managing prompts, including validation and context injection. Essential for the `ExploreAgent`.

- **`phoenix_config_package/`**: A robust package for handling hierarchical configuration.

### 3. `agency_toolkit` - Modern & Simple References

- **`agency_toolkit_providers/`**: A clean and simple implementation of the LLM provider pattern.
- **`agency_toolkit_cli_app.py`**: A good reference for a modern CLI structure.

## Proposed Implementation Plan for `capsule_audit` (Hybrid Approach)

1.  **Data Collection Layer (from `steward context`)**:
    -   Create a `collectors/` directory in `capsule_audit`.
    -   Adapt the collector pattern from `phoenix_steward_context_subcommand/collectors.py` and its related files.
    -   Implement collectors for the specific data points needed for a capsule audit (e.g., file structure, dependencies, complexity metrics, etc.).

2.  **Analysis & Orchestration Layer (from `ExploreAgent`)**:
    -   Adapt the `ExploreAgent` into a generic `AuditAgent`.
    -   The `AuditAgent` will not discover context on its own, but will be *given* the context aggregated by the collectors.
    -   The agent's `run` method will take the collected data as input, and its planning prompts will be designed to analyze this pre-existing data to find issues and suggest improvements.

3.  **Core Workflow**:
    -   The main `capsule-audit analyze` command will first invoke the **Data Collection Layer** to gather all relevant facts about the project capsule.
    -   It will then pass the aggregated JSON/dictionary of facts to the **Analysis & Orchestration Layer** (`AuditAgent`).
    -   The `AuditAgent` will then execute its plan-execute-reflect loop to analyze the data and produce the final audit report.

4.  **Supporting Components**:
    -   Use `phoenix_config_package` for configuration.
    -   Use `prompt_registry_package` for managing the `AuditAgent`'s prompts.
    -   Use the `agency_toolkit_providers` as a reference for the LLM provider.
    -   Adapt the `phoenix_explore_cli` for the main CLI, using `agency_toolkit_cli_app.py` as a structural reference.

This hybrid approach leverages the best of both worlds: the powerful, systematic data aggregation of `steward context` and the intelligent, autonomous analysis of the `ExploreAgent`. This will create a highly effective and comprehensive audit tool.