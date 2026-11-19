---
name: graphify
description: Build, update, or query the repository knowledge graph to trace dependencies and navigate code architecture without reading raw files. Use when exploring unfamiliar architecture, tracing call paths, or analyzing refactoring impact.
---

# Graphify Workflow

Graphify builds and queries a deterministic AST-based code graph of the repository using Tree-sitter.

## 1. Generate or Update Graph

Run in repository root:

```bash
graphify update
```

This parses source code locally and outputs artifacts in `graphify-out/`:
- `graphify-out/GRAPH_REPORT.md`: Architecture overview, community clusters, and core hub nodes ("god nodes").
- `graphify-out/graph.json`: Machine-readable dependency graph.
- `graphify-out/graph.html`: Visual interactive dependency graph.

## 2. Inspecting Architecture & Dependencies

Always enclose symbols in quotes `"..."`. Do not use literal angle brackets `<...>` in the shell.

### A. Tracing Paths Between Components
Find how two parts of the system connect across function calls, models, or imports:

```bash
# General search (directed)
graphify path "SymbolA" "SymbolB"

# If no directed path exists or searching upstream & downstream (recommended):
graphify path "SymbolA" "SymbolB" --undirected

# If a symbol is ambiguous across multiple files, qualify with file::Symbol:
graphify path "backend/app/models/batch.py::Batch" "backend/app/models/reading.py::Reading" --undirected
```

### B. Explaining a Component's Neighborhood
Inspect a node's dependencies and direct connections:

```bash
graphify explain "backend/app/models/batch.py::Batch"
```

### C. Viewing Architectural Communities
Open `graphify-out/GRAPH_REPORT.md` to see the top connected hub nodes ("god nodes") and modular clusters.

## 3. Maintenance

The generated `graphify-out/` and `.graphify/` caches are ignored in `.gitignore`.
