# Leapfrog Docweaver Monorepo

This repository is a monorepo that contains multiple applications and services for the Leapfrog Docweaver platform.

It includes:
- Backend services (API and document processing)
- An MCP server
- Frontend applications

## Repository Layout

### `apps/backend/`
Python backend workspace with:
- Main API service
- Document processor service
- Database migrations (Alembic)
- Backend tests

### `apps/frontend/`
Primary frontend application (Vite + TypeScript).

### `apps/demo-app/`
Demo frontend application used for experiments and integration testing.

### `mcp-server/`
Model Context Protocol (MCP) server implementation and related deployment/runtime files.

## Why This Is a Monorepo

Keeping backend, MCP, and frontend apps in one repository makes it easier to:
- Share contracts and integration logic
- Coordinate changes across services and UI
- Manage development workflows in one place

## Notes

- Each app/service has its own `README.md` for setup and run instructions.
- Use the package-level docs for environment-specific commands.
