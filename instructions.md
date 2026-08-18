# Project Directives & Development Guidelines

> [!IMPORTANT]
> **MANDATORY DIRECTIVE FOR THE AI ASSISTANT:**
> Read this file before proposing, designing, or implementing any code changes across this repository.

---

## 🚫 1. Strict Business Rule & Domain Modification Policy

1. **NO Autonomous Rule Creation**:
   - The assistant must **NEVER** add, invent, infer, or alter business rules, domain specifications, data constraints, calculations, or classification logic on its own.
2. **Mandatory Discussion & Approval**:
   - Any change, addition, or refactor to business rules across **ANY layer** (`domain`, `services`, `schemas`, `models`, `database`, `api`) must first be explicitly presented, discussed, and approved by the user.
3. **Pure Execution on Approvals**:
   - Data alterations, schema definitions, and model structures must strictly follow the user's direct instructions without unsolicited extra domain rules or unprompted auto-conversions.

---

## 🏗️ 2. Architectural Layers & Boundaries

* **`app/domain/`**:
  - Contains strictly **constants**, **templates**, and **documentation** (`documentation.md`).
  - No active business logic scripts or autonomous mutating functions live in `domain/`.
* **`app/schemas/`**:
  - Stateless Pydantic contracts for API input/output validation.
* **`app/services/`**:
  - Application services and calculation engines (e.g., `Polars` engine, DB queries).
* **`app/models/`**:
  - SQLAlchemy PostgreSQL table definitions.
* **`app/api/`**:
  - Thin FastAPI HTTP route handlers.

---

## 📋 3. Protocol for Feature & Rule Requests

1. **Discuss**: Present options, trade-offs, and design clearly to the user.
2. **Wait for Approval**: Do not write code or modify database schemas until the user explicitly confirms the approach.
3. **Implement Strictly as Agreed**: Implement only what was agreed upon—no unsolicited scope creep.
