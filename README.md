# bot

## Deploy to Cloud 66

If you saw "We couldn’t detect a framework in your source code. To deploy, please add a Dockerfile" — this repository now includes a root-level `Dockerfile` that builds the application located in the `bot/` subfolder. Cloud 66 (and other platform scanners) require a `Dockerfile` at the repository root unless you configure a subdirectory build path in the platform UI.

Quick steps:
1. Use the existing Stack → select "Containers / Dockerfile".
2. Set required environment variables: `API_ID`, `API_HASH`, `BOT_TOKEN` (optional), `OWNER_ID`.
3. Map persistent volumes `/app/sessions` and `/app/downloads`.

