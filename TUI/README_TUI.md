# Excalidraw Tunnel Manager TUI

This directory contains a Textual-based terminal UI for starting the Excalidraw servers
and creating SSH tunnels to them.

## Setup

1. **Install dependencies**
   ```bash
   pip install textual
   ```

2. **Adjust configuration**
   Edit `excalidraw_tunnel_manager.py` and update the following constants at the
   top of the file:
   - `SERVER_PATH` / `ROOM_PATH` – paths to your local clones of
     `excalidraw` and `excalidraw-room` (e.g. `~/path/to/excalidraw`).
   - `SERVER_CMD` / `ROOM_CMD` – commands used to start the servers.
   - `SSH_HOST` – the host that will be used for SSH tunneling.
   - port numbers if needed.

## Running

From any terminal run:

```bash
python excalidraw_tunnel_manager.py
```

The UI lets you start and stop the Excalidraw and Room servers, create
and tear down tunnels and reboot everything with a single command.
