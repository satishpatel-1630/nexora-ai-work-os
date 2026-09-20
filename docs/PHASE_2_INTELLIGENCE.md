# NEXORA Phase 2 — Intelligence Engine

Phase 2 turns the Phase 1 foundation into an executable intelligence pipeline.

## Pipeline

Request → Intent → Research → Task Intelligence → Planning → Specialist Selection → Specialist Research → Briefs → Prompting → Routing → Model Execution → Usage → Result.

## Providers

The default provider is "mock", allowing credential-free local development and CI. Gemini is isolated behind GeminiProvider and GeminiResearchProvider and uses the official Google GenAI SDK when AI_DEFAULT_PROVIDER=gemini.

## Persistence

Phase 2 adds intelligence_runs, research_findings, task_plans, specialist_briefs, prompt_artifacts, and model_invocations.

## API

- POST /api/v1/intelligence/runs
- GET /api/v1/intelligence/runs
- GET /api/v1/intelligence/runs/{id}
- POST /api/v1/intelligence/runs/{id}/execute
- GET /api/v1/intelligence/runs/{id}/research
- GET /api/v1/intelligence/runs/{id}/plan
- GET /api/v1/intelligence/runs/{id}/briefs
- GET /api/v1/intelligence/runs/{id}/prompts
- GET /api/v1/intelligence/runs/{id}/usage

The execute endpoint enqueues INTELLIGENCE_RUN onto the existing Redis queue. The worker executes the pipeline and persists the result.

## Security

Model output and research are untrusted data. They cannot directly execute tools or bypass approvals. Secrets are never returned by the API.

## Deferred

Phase 3 will implement executable agents, capabilities, MCP and tool execution. Media, social publishing, semantic memory and production secrets remain later phases.
