import React, { useState } from 'react';
import { Folder, File, ChevronRight, ChevronDown, Sparkles, Code, CheckCircle, AlertCircle } from 'lucide-react';

const AIAgencyWorkspace = () => {
  const [expandedFolders, setExpandedFolders] = useState(['root', 'agents', 'prompts']);
  const [selectedItem, setSelectedItem] = useState(null);

  const workspaceStructure = {
    name: 'ai-agent-agency/',
    type: 'folder',
    children: [
      {
        name: '00-SYSTEM-CORE/',
        type: 'folder',
        description: 'Grundlegende Agent-Konfigurationen',
        children: [
          { 
            name: 'agent-roles.yaml', 
            type: 'file',
            content: `# AI Agent Rollen Definition
# Jeder Agent = spezialisierte Rolle mit klarem Scope

architect_agent:
  role: "System Architect"
  expertise: ["system design", "tech stack", "scalability"]
  output_format: "structured markdown with diagrams"
  constraints:
    - "no implementation details"
    - "focus on high-level design"
    - "always provide alternatives"
  
code_generator_agent:
  role: "Code Generator"
  expertise: ["implementation", "best practices", "clean code"]
  output_format: "production-ready code with tests"
  constraints:
    - "follow project style guide"
    - "include error handling"
    - "atomic commits only"

reviewer_agent:
  role: "Code Reviewer"
  expertise: ["security", "performance", "maintainability"]
  output_format: "actionable feedback list"
  constraints:
    - "constructive feedback only"
    - "prioritize critical issues"
    - "suggest specific improvements"`
          },
          { 
            name: 'context-templates.md', 
            type: 'file',
            content: `# Context Engineering Templates

## Minimum Viable Context (MVC)
Jeder Prompt braucht:
- WHO: Welcher Agent?
- WHAT: Welche Aufgabe?
- WHY: Welches Ziel?
- CONSTRAINTS: Was NICHT tun?

## Template Struktur
\`\`\`
AGENT: [role]
TASK: [specific task]
CONTEXT: [relevant info only]
OUTPUT: [exact format]
CONSTRAINTS: [dos and don'ts]
\`\`\`

## Anti-Slop Regeln
❌ "Make it better"
✅ "Refactor function X to reduce cyclomatic complexity below 10"

❌ "Add features"  
✅ "Implement user authentication with JWT, max 3 endpoints"`
          },
          { 
            name: 'anti-slop-rules.md', 
            type: 'file',
            content: `# Anti-AI-Slop Best Practices

## Code Quality Guards

### 1. Atomic Outputs
- One agent = One responsibility
- One prompt = One deliverable
- One file = One purpose

### 2. Verification Chain
Agent Output → Validator Agent → Human Gate → Integration

### 3. No Generic Fluff
❌ "This is a robust solution..."
❌ "Here's a comprehensive approach..."
❌ "Let me help you with that..."

✅ Direct technical content only
✅ Code + minimal explanation
✅ Actionable next steps

### 4. Context Pollution Prevention
- Clear previous context before new task
- Use structured handoffs between agents
- Version control for prompt templates

### 5. Deterministic Outputs
- Specify exact format (JSON schema, TypeScript interfaces)
- Use temperature=0 for code generation
- Request diffs, not full rewrites`
          }
        ]
      },
      {
        name: '01-AGENTS/',
        type: 'folder',
        description: 'Spezialisierte Agent-Definitionen',
        children: [
          {
            name: 'intake-agents/',
            type: 'folder',
            children: [
              { 
                name: 'scope-analyzer.md', 
                type: 'file',
                content: `# Scope Analyzer Agent

## Role
Extracts clear project scope from vague client descriptions

## Input Format
Raw client request (any format)

## Processing
1. Extract core requirements
2. Identify ambiguities
3. Flag scope creep risks
4. Generate clarifying questions

## Output Format
\`\`\`yaml
core_requirements:
  - [requirement 1]
  - [requirement 2]
  
ambiguities:
  - question: "..."
    impact: "high/medium/low"
    
red_flags:
  - [potential scope creep area]
  
clarifying_questions:
  - [question 1]
  - [question 2]
\`\`\`

## Prompt Template
\`\`\`
You are a technical scope analyst. 
Client request: {CLIENT_INPUT}

Extract:
1. MUST-HAVE features (critical for V1)
2. UNCLEAR aspects (need clarification)
3. SCOPE RISKS (likely to expand)

Output ONLY valid YAML. No preamble.
\`\`\``
              }
            ]
          },
          {
            name: 'architecture-agents/',
            type: 'folder',
            children: [
              { 
                name: 'system-designer.md', 
                type: 'file',
                content: `# System Designer Agent

## Prompt Chain Structure

### Step 1: Component Identification
\`\`\`
INPUT: validated project scope
TASK: Identify 5-7 main system components
OUTPUT: component list with responsibilities
NEXT: data-flow-mapper
\`\`\`

### Step 2: Data Flow Mapping
\`\`\`
INPUT: component list
TASK: Map data flow between components
OUTPUT: mermaid diagram + description
NEXT: tech-stack-recommender
\`\`\`

### Step 3: Tech Stack Recommendation
\`\`\`
INPUT: components + data flow
TASK: Recommend minimal viable tech stack
OUTPUT: stack with justifications
NEXT: architecture-reviewer
\`\`\`

## Anti-Pattern Detection
- Flags: microservices for simple CRUD
- Flags: over-engineering (Kubernetes for 100 users)
- Flags: missing error handling strategy`
              }
            ]
          },
          {
            name: 'implementation-agents/',
            type: 'folder',
            children: [
              { 
                name: 'code-generator.md', 
                type: 'file',
                content: `# Code Generator Agent

## Context Requirements (Strict)
\`\`\`yaml
required_context:
  - file_path: "exact/path/in/repo"
  - function_signature: "def function_name(params)"
  - dependencies: ["list", "of", "imports"]
  - style_guide: "link to rules"
  
optional_context:
  - existing_code: "related functions"
  - test_examples: "similar tests"
\`\`\`

## Output Format (Enforced)
\`\`\`python
# File: {exact_path}
# Purpose: {one_line}
# Dependencies: {explicit_list}

{code_block}

# Tests: test_{filename}
{test_block}

# Integration:
# 1. Add to {file}
# 2. Import as {name}
# 3. Run: pytest {test_file}
\`\`\`

## Quality Gates
Before output, verify:
- [ ] No placeholder comments
- [ ] Error handling present
- [ ] Type hints included (Python)
- [ ] Max function length: 50 lines
- [ ] No hardcoded values`
              }
            ]
          }
        ]
      },
      {
        name: '02-PROMPTS/',
        type: 'folder',
        description: 'Atomic, wiederverwendbare Prompt-Bausteine',
        children: [
          {
            name: 'atomic-prompts/',
            type: 'folder',
            children: [
              { 
                name: 'code-review.md', 
                type: 'file',
                content: `# Atomic Prompt: Code Review

## Context Block
\`\`\`
<context>
  <role>Senior Code Reviewer</role>
  <focus>Security, Performance, Maintainability</focus>
  <language>{LANGUAGE}</language>
  <style_guide>{STYLE_GUIDE_URL}</style_guide>
</context>
\`\`\`

## Task Block
\`\`\`
<task>
Review this code for:
1. Security vulnerabilities (OWASP Top 10)
2. Performance bottlenecks
3. Code smell (>15 cyclomatic complexity)
4. Missing error handling

<code>
{CODE_BLOCK}
</code>
</task>
\`\`\`

## Output Format
\`\`\`
<output_format>
Return JSON only:
{
  "critical": [{"line": N, "issue": "", "fix": ""}],
  "warnings": [{"line": N, "issue": "", "suggestion": ""}],
  "score": N/10,
  "approved": boolean
}
</output_format>
\`\`\`

## Usage in Chain
scope-analyzer → system-designer → code-generator → **THIS** → human-review`
              }
            ]
          },
          {
            name: 'prompt-chains/',
            type: 'folder',
            children: [
              { 
                name: 'new-project-chain.yaml', 
                type: 'file',
                content: `# Prompt Chain: New Project (End-to-End)

chain_name: "new_project_full_cycle"
trigger: "client submits new project request"

steps:
  - id: "intake"
    agent: "scope-analyzer"
    input: "client_brief"
    output: "validated_scope.yaml"
    human_gate: true  # Client confirms scope
    
  - id: "architecture"
    agent: "system-designer"
    input: "validated_scope.yaml"
    output: "architecture.md"
    human_gate: true  # Architect approves
    
  - id: "planning"
    agent: "task-breakdown"
    input: "architecture.md"
    output: "feature_list.yaml"
    human_gate: false
    
  - id: "implementation"
    agent: "code-generator"
    input: "feature_list.yaml[0]"  # First feature only
    output: "code + tests"
    loop: true  # Iterate through features
    human_gate: true  # Per feature review
    
  - id: "review"
    agent: "code-reviewer"
    input: "generated_code"
    output: "review_report.json"
    human_gate: true
    
  - id: "deployment"
    agent: "deployment-validator"
    input: "approved_code"
    output: "deployment_checklist.md"
    human_gate: true

error_handling:
  - if: "human_gate == rejected"
    action: "return to previous step with feedback"
  - if: "agent_output == invalid"
    action: "retry with clarified prompt"`
              }
            ]
          }
        ]
      },
      {
        name: '03-WORKFLOWS/',
        type: 'folder',
        description: 'Multi-Agent Orchestrierung',
        children: [
          { 
            name: 'legacy-takeover.yaml', 
            type: 'file',
            content: `# Workflow: Legacy Code Takeover

trigger: "client provides existing codebase"

phases:
  assess:
    - agent: "codebase-scanner"
      output: "inventory.json"
    - agent: "dependency-analyzer"
      output: "dep_tree.yaml"
    - agent: "security-auditor"
      output: "vulnerabilities.json"
      
  understand:
    - agent: "architecture-reverse-engineer"
      input: "all previous outputs"
      output: "inferred_architecture.md"
    - agent: "documentation-generator"
      output: "technical_docs.md"
      
  plan:
    - agent: "refactor-prioritizer"
      output: "refactor_roadmap.yaml"
    - human: "client approves roadmap"
    
  execute:
    - agent: "refactor-executor"
      loop: "each refactor task"
      output: "PR + tests"
    - agent: "integration-tester"
      output: "test_report.json"`
          }
        ]
      },
      {
        name: '04-CONTEXT-MANAGEMENT/',
        type: 'folder',
        description: 'Stateful Context für Agenten',
        children: [
          { 
            name: 'context-assembly.md', 
            type: 'file',
            content: `# Context Assembly Rules

## Principle: Minimum Viable Context (MVC)
Include only what's necessary for THIS task.

## Context Layers

### Layer 1: Agent Role (Always)
\`\`\`
You are a {ROLE}.
Your expertise: {EXPERTISE_LIST}.
Your constraints: {CONSTRAINT_LIST}.
\`\`\`

### Layer 2: Task Specification (Always)
\`\`\`
Task: {ATOMIC_TASK}
Expected output: {FORMAT}
Success criteria: {CRITERIA}
\`\`\`

### Layer 3: Project Context (Conditional)
Include ONLY if relevant:
- Tech stack (if code generation)
- Style guide (if formatting matters)
- Previous decisions (if building on past work)

### Layer 4: Domain Context (Rare)
Only for domain-specific tasks:
- Business rules
- Compliance requirements
- User personas

## Context Size Budget
- Code generation: <4000 tokens
- Architecture: <2000 tokens
- Review: <3000 tokens

## Context Pollution Check
Before sending prompt, remove:
- ❌ Duplicate information
- ❌ Irrelevant history
- ❌ Vague instructions
- ❌ Example code (unless template)`
          },
          { 
            name: 'state-handoff.md', 
            type: 'file',
            content: `# State Handoff Between Agents

## Problem
Agent A produces output → Agent B needs context from A

## Anti-Pattern
❌ Pass entire conversation history to Agent B

## Solution: Structured Handoff

### Handoff Document Format
\`\`\`yaml
handoff:
  from_agent: "scope-analyzer"
  to_agent: "system-designer"
  timestamp: "2025-11-10T10:30:00Z"
  
  task_completed:
    output_file: "validated_scope.yaml"
    key_decisions:
      - "Using REST API (not GraphQL)"
      - "SQLite for MVP (not PostgreSQL)"
    
  next_task:
    description: "Design system architecture"
    inputs_needed:
      - validated_scope.yaml
      - tech_stack_constraints.md
    expected_output: "architecture.md"
    
  context_notes:
    - "Client prefers Python backend"
    - "Must deploy on Vercel (serverless)"
\`\`\`

## Implementation
1. Agent A completes task
2. System generates handoff doc
3. Agent B receives only handoff + referenced files
4. No raw conversation history passed`
          }
        ]
      },
      {
        name: '05-QUALITY-GATES/',
        type: 'folder',
        description: 'Validatoren für Agent-Outputs',
        children: [
          { 
            name: 'output-validators.md', 
            type: 'file',
            content: `# Output Validation System

## Validation Chain
Agent Output → Format Validator → Quality Validator → Human Gate

## Format Validators (Automated)

### Code Output
\`\`\`python
def validate_code_output(output):
    checks = {
        'has_tests': 'test_' in output,
        'has_docstrings': '"""' in output,
        'no_todos': 'TODO' not in output,
        'no_placeholders': 'placeholder' not in output.lower(),
        'proper_imports': output.startswith('import') or 'from' in output[:100]
    }
    return all(checks.values()), checks
\`\`\`

### Markdown Documentation
\`\`\`python
def validate_docs_output(output):
    checks = {
        'has_title': output.startswith('#'),
        'has_sections': output.count('##') >= 3,
        'has_examples': '```' in output,
        'no_fluff': not any(word in output for word in ['robust', 'comprehensive', 'leverage'])
    }
    return all(checks.values()), checks
\`\`\`

## Quality Validators (Agent-based)

### Reviewer Agent Prompt
\`\`\`
Review this {ARTIFACT_TYPE} against:
1. Completeness (all requirements met?)
2. Clarity (understandable by junior dev?)
3. Maintainability (follows best practices?)

Return:
{
  "approved": bool,
  "issues": [{severity, description, line}],
  "score": 0-10
}

Approval threshold: 8/10
\`\`\``
          }
        ]
      }
    ]
  };

  const toggleFolder = (path) => {
    setExpandedFolders(prev => 
      prev.includes(path) 
        ? prev.filter(p => p !== path)
        : [...prev, path]
    );
  };

  const renderTree = (node, path = '') => {
    const currentPath = path ? `${path}/${node.name}` : node.name;
    const isExpanded = expandedFolders.includes(currentPath);
    const isSelected = selectedItem === currentPath;

    if (node.type === 'folder') {
      return (
        <div key={currentPath} className="ml-0">
          <div 
            className={`flex items-center gap-2 py-2 px-3 cursor-pointer hover:bg-blue-50 rounded transition-colors ${isSelected ? 'bg-blue-100' : ''}`}
            onClick={() => {
              toggleFolder(currentPath);
              setSelectedItem(currentPath);
            }}
          >
            {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <Folder size={16} className="text-blue-600" />
            <span className="font-medium text-sm">{node.name}</span>
          </div>
          {isExpanded && node.children && (
            <div className="ml-4 border-l-2 border-gray-200 pl-2">
              {node.children.map(child => renderTree(child, currentPath))}
            </div>
          )}
          {isExpanded && node.description && (
            <div className="ml-10 text-xs text-gray-500 italic mb-2">
              {node.description}
            </div>
          )}
        </div>
      );
    } else {
      return (
        <div 
          key={currentPath}
          className={`flex items-center gap-2 py-2 px-3 cursor-pointer hover:bg-green-50 rounded transition-colors ${isSelected ? 'bg-green-100' : ''}`}
          onClick={() => setSelectedItem(currentPath)}
        >
          <File size={16} className="text-green-600" />
          <span className="text-sm">{node.name}</span>
        </div>
      );
    }
  };

  const getSelectedContent = () => {
    const findNode = (node, path, currentPath = '') => {
      const nodePath = currentPath ? `${currentPath}/${node.name}` : node.name;
      if (nodePath === path) return node;
      if (node.children) {
        for (const child of node.children) {
          const found = findNode(child, path, nodePath);
          if (found) return found;
        }
      }
      return null;
    };

    const node = findNode(workspaceStructure, selectedItem);
    return node?.content || node?.description;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="text-yellow-400" size={32} />
            <h1 className="text-4xl font-bold">AI-Agent-Agentur Workspace</h1>
          </div>
          <p className="text-blue-200 text-lg">
            Modulares System für AI-gestützte Softwareentwicklung
          </p>
          <div className="mt-4 flex gap-4 justify-center text-sm">
            <div className="flex items-center gap-2 bg-blue-800/50 px-4 py-2 rounded-lg">
              <Code size={16} />
              <span>Atomic Prompts</span>
            </div>
            <div className="flex items-center gap-2 bg-green-800/50 px-4 py-2 rounded-lg">
              <CheckCircle size={16} />
              <span>Anti-Slop Guards</span>
            </div>
            <div className="flex items-center gap-2 bg-purple-800/50 px-4 py-2 rounded-lg">
              <AlertCircle size={16} />
              <span>Context Engineering</span>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* File Tree */}
          <div className="lg:col-span-1 bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Folder size={20} />
              Workspace Structure
            </h2>
            <div className="overflow-y-auto max-h-[600px] text-white">
              {renderTree(workspaceStructure)}
            </div>
          </div>

          {/* Content Viewer */}
          <div className="lg:col-span-2 bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <File size={20} />
              Content Preview
            </h2>
            {selectedItem ? (
              <div className="bg-slate-900/50 rounded-lg p-4 overflow-x-auto">
                <pre className="text-sm text-green-300 whitespace-pre-wrap font-mono">
                  {getSelectedContent() || 'Wähle eine Datei aus der Struktur'}
                </pre>
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">
                <File size={48} className="mx-auto mb-4 opacity-50" />
                <p>Klicke auf eine Datei in der Struktur links, um den Inhalt zu sehen</p>
              </div>
            )}
          </div>
        </div>

        {/* Key Principles */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-900/30 border border-blue-500/30 rounded-lg p-4">
            <h3 className="font-bold mb-2 text-blue-300">🎯 Atomic Prompts</h3>
            <p className="text-sm text-gray-300">Ein Prompt = Eine Aufgabe. Keine Vermischung von Concerns.</p>
          </div>
          <div className="bg-green-900/30 border border-green-500/30 rounded-lg p-4">
            <h3 className="font-bold mb-2 text-green-300">🧹 Anti-Slop</h3>
            <p className="text-sm text-gray-300">Kein generisches Gerede. Nur präzise, technische Outputs.</p>
          </div>
          <div className="bg-purple-900/30 border border-purple-500/30 rounded-lg p-4">
            <h3 className="font-bold mb-2 text-purple-300">🔗 Context Chains</h3>
            <p className="text-sm text-gray-300">Strukturierter State-Transfer zwischen Agenten.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAgencyWorkspace;