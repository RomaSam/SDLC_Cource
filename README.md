# Cinema

Simple Cinema web app — Python + SQLite + FastAPI, with an MCP server for AI tool integration.

## Running locally

### 1. Start the Cinema API

```bash
cd Cinema
uvicorn api.main:app --reload
```

API will be available at `http://127.0.0.1:8000`.

### 2. Start the MCP server with Inspector

Use the pinned Inspector version to avoid known bugs in other releases:

```bash
cd Cinema/mcp
npx @modelcontextprotocol/inspector@0.19.0 py server.py
```

Opens the Inspector UI in the browser at `http://localhost:5173`.

> **Note:** Use `py` on Windows. Use `python3` on macOS/Linux.

### Refreshing resources in the Inspector

The Inspector does **not** auto-refresh when you switch between resources.
To see current data for any resource:

1. Click the resource name in the left sidebar.
2. Click the **"Read Resource"** button in the detail pane.

Each click of "Read Resource" sends a fresh request to the MCP server.
