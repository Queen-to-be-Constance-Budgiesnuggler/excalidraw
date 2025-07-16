# AGENTS.md

## Project Structure

Excalidraw is structured as a **monorepo**:

- **`packages/excalidraw/`** - Main React component library
- **`excalidraw-app/`** - Full web application
- **`packages/`** - Core packages (`@excalidraw/common`, `@excalidraw/element`, `@excalidraw/math`, `@excalidraw/utils`)
- **`examples/`** - Integration examples

## Agent Workflow

- **Editing**: Codex should focus edits primarily within `packages/*` and `excalidraw-app/`.
- **Testing**: Automatically run tests before finalizing changes (`yarn test:update` and `yarn test:typecheck`).
- **Documentation**: Clearly document changes in Pull Requests.

## Development Commands

```bash
yarn install              # Install dependencies
yarn test:typecheck       # TypeScript checks
yarn test:update          # Run tests & update snapshots
yarn fix                  # Format and lint
```

## Contribution Guidelines

- Contributions must pass type checks and automated tests.
- PR titles: `[<project_name>] <descriptive title>`
- Clearly document changes in the PR description.
