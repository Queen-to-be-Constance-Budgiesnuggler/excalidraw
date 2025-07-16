# Excaliman Session Manager TUI

This directory contains a GPU-accelerated Textual UI designed for the Kitty terminal. It manages both Excalidraw and Excalidraw-Room servers, creates SSH tunnels and monitors their status. Multiple environments are supported along with automatic restarts and log viewing.

The tool relies on the same commands you would normally use when developing Excalidraw locally. Common commands found across this repository include:

- `yarn start` – start the main Excalidraw app.
- `yarn start:dev` and `pm2 start pm2.production.json` – start the collaboration server from **excalidraw-room**.
- `yarn fix`, `yarn test`, `yarn test:update`, `yarn test:code` – formatting and testing helpers.
- `docker-compose up --build -d` – run the Docker setup.

The default ports used during development are 3000 for the main app, 3002 for the collaboration server and 3015 for the AI backend. These values along with host URLs come from `.env.development` and include variables like `VITE_APP_WS_SERVER_URL`, `VITE_APP_PLUS_APP`, `VITE_APP_AI_BACKEND`, `VITE_APP_LIBRARY_URL`, `VITE_APP_LIBRARY_BACKEND`, `VITE_APP_BACKEND_V2_GET_URL` and `VITE_APP_BACKEND_V2_POST_URL`.

## Setup

1. **Install dependencies**

   ```bash
   pip install textual
   ```

2. **Adjust configuration** Edit `excalimanTUI.py` and update the following constants at the top of the file:
   - `SERVER_PATH` / `ROOM_PATH` – paths to your local clones of `excalidraw` and `excalidraw-room` (e.g. `~/path/to/excalidraw`).
   - `SERVER_CMD` / `ROOM_CMD` – commands used to start the servers. Example values are `["yarn", "start"]` for the main app and `["yarn", "start:dev"]` for the Room server. Ensure these commands work locally before using the tunnel manager.
   - `SSH_HOST` – the host that will be used for SSH tunneling.
   - port numbers if needed.

## Running

From any terminal run:

```bash
python excalimanTUI.py
```

The UI lets you launch and stop the Excalidraw and Room servers, view their output in real time and automatically restart them if they crash. It can create and tear down tunnels and reboot everything with a single command. The manager supports multiple environments which define port mappings.
