#!/usr/bin/env python3
# excalidraw_tunnel_manager.py
# A TUI application using Textual to manage Excalidraw and Excalidraw Room tunnels and servers.

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Switch, TextLog
from textual.containers import Container
from textual.reactive import reactive
import os

# Adjust these paths and commands to match your setup
SERVER_PATH = os.path.expanduser("~/path/to/excalidraw")
ROOM_PATH = os.path.expanduser("~/path/to/excalidraw-room")
SERVER_CMD = ["npm", "start"]      # Command to launch Excalidraw server
ROOM_CMD   = ["npm", "start"]      # Command to launch Excalidraw Room server
SSH_HOST   = "your-host"            # SSH host for tunneling
DEV_PORT_SERVER = 8000
PROD_PORT_SERVER = 80
DEV_PORT_ROOM   = 3000
PROD_PORT_ROOM  = 443

class TunnelManager(App):
    """
    A Textual-based TUI for: 
      - Starting, rebooting, and exiting Excalidraw and Room servers
      - Establishing and tearing down SSH tunnels
      - Switching between dev and prod environments
      - Displaying status and tunnel URL
    """
    CSS = """
    Screen { align: center middle; }
    #controls { layout: vertical; width: 30%; min-width: 40; padding: 1; }
    #log { layout: vertical; width: 70%; padding: 1; border: heavy; }
    """

    env = reactive("dev")
    server_proc = reactive(None)
    room_proc   = reactive(None)
    tunnel_proc = reactive([])

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with Container(id="controls"):
                yield Static("Environment:")
                yield Switch(label="Prod", value=False, name="env_switch")
                yield Button("Start Server", id="start_server")
                yield Button("Start Room", id="start_room")
                yield Button("Reboot All", id="reboot_all")
                yield Button("Exit All", id="exit_all")
                yield Static("Tunnel URL:", id="link_label")
                yield Static("", id="link_url")
            yield TextLog(highlight=True, id="log")
        yield Footer()

    async def on_mount(self):
        self.log = self.query_one(TextLog)
        self.link_widget = self.query_one("#link_url", Static)
        self.update_link()

    def update_link(self):
        # Update displayed URL based on current environment
        port = DEV_PORT_SERVER if self.env == "dev" else PROD_PORT_SERVER
        url = f"http://localhost:{port}"
        self.link_widget.update(url)

    async def on_switch_changed(self, event):
        # Toggle environment
        self.env = "prod" if event.value else "dev"
        self.log.write(f"Switched environment to [bold]{self.env}[/bold]")
        self.update_link()

    async def on_button_pressed(self, event):
        match event.button.id:
            case "start_server":
                await self.start_server()
            case "start_room":
                await self.start_room()
            case "reboot_all":
                await self.reboot_all()
            case "exit_all":
                await self.exit_all()

    async def start_server(self):
        # If already running, skip
        if self.server_proc and self.server_proc.returncode is None:
            self.log.write("[yellow]Server already running[/yellow]")
            return
        self.log.write("Starting Excalidraw server...")
        self.server_proc = await asyncio.create_subprocess_exec(*SERVER_CMD, cwd=SERVER_PATH)
        await asyncio.sleep(1)  # brief wait for server to initialize
        port = DEV_PORT_SERVER if self.env == "dev" else PROD_PORT_SERVER
        # Establish SSH tunnel
        self.log.write(f"Tunneling port {port} -> localhost:{port} via {SSH_HOST}...")
        tunnel = await asyncio.create_subprocess_exec(
            "ssh", "-N", "-L", f"{port}:localhost:{port}", SSH_HOST
        )
        self.tunnel_proc.append(tunnel)
        self.log.write(f"[green]Server tunnel active at http://localhost:{port}[/green]")

    async def start_room(self):
        if self.room_proc and self.room_proc.returncode is None:
            self.log.write("[yellow]Room already running[/yellow]")
            return
        self.log.write("Starting Excalidraw Room server...")
        self.room_proc = await asyncio.create_subprocess_exec(*ROOM_CMD, cwd=ROOM_PATH)
        await asyncio.sleep(1)
        port = DEV_PORT_ROOM if self.env == "dev" else PROD_PORT_ROOM
        self.log.write(f"Tunneling port {port} -> localhost:{port} via {SSH_HOST}...")
        tunnel = await asyncio.create_subprocess_exec(
            "ssh", "-N", "-L", f"{port}:localhost:{port}", SSH_HOST
        )
        self.tunnel_proc.append(tunnel)
        self.log.write(f"[green]Room tunnel active at http://localhost:{port}[/green]")

    async def reboot_all(self):
        self.log.write("Rebooting both server and room...")
        await self.exit_all()
        await self.start_server()
        await self.start_room()

    async def exit_all(self):
        self.log.write("Stopping all services and tunnels...")
        # Terminate room first, then server
        if self.room_proc:
            self.room_proc.terminate()
            await self.room_proc.wait()
            self.log.write("Room server stopped")
        if self.server_proc:
            self.server_proc.terminate()
            await self.server_proc.wait()
            self.log.write("Server stopped")
        # Close tunnels
        for tunnel in self.tunnel_proc:
            tunnel.terminate()
            await tunnel.wait()
        self.tunnel_proc.clear()
        self.log.write("All tunnels closed")

if __name__ == "__main__":
    TunnelManager.run(title="Excalidraw Tunnel Manager")
