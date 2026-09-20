# NEXORA Architecture

## Control flow

Request → Research → Task Intelligence → Decompose → Specialist Selection → Specialist Brief → Prompt Engineering → Model Routing → Agent Execution → Evaluation → Repair/Retry → Approval → External Execution → Analytics → Memory.

Phase 1 establishes contracts for these stages; only the application foundation is executable.

## Layers

HTTP/API → Application Services → Domain → Repositories → Infrastructure.

The domain is provider-neutral. External actions are policy-controlled and consequential actions require approval.

## Runtime

Web is the user experience. FastAPI owns application APIs. PostgreSQL is the system of record. Redis provides Phase 1 worker/readiness infrastructure.

## Future boundaries

ModelRouter and CostRouter remain provider-neutral. Capabilities describe what can be done; tools describe concrete operations; policy determines whether a tool may execute. MCP, memory/RAG, media, social, integrations, evaluation and durable workflows are later phases.
