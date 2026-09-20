# Security

Phase 1 principles:

- Never commit secrets; use .env locally and .env.example as the template.
- External content is untrusted and cannot override system instructions or permissions.
- Tools do not execute merely because they are registered.
- Consequential external actions pass through policy and approval.
- Agents receive no unrestricted shell, filesystem, browser, database or account access.
- API errors do not expose internal tracebacks.
- Request IDs are returned for supportability but contain no sensitive information.
