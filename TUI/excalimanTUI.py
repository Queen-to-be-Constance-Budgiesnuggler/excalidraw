#!/usr/bin/env python3
# excalimanTUI.py
# A GPU‑accelerated Textual TUI for managing Excalidraw and Excalidraw Room servers via Kitty.

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Button,
    Static,
    Log,
    Select,
)
from textual.containers import Container
from textual.reactive import reactive
import os
import signal
import webbrowser

# Adjust these paths and commands to match your setup
SERVER_PATH = os.path.expanduser("~/path/to/excalidraw")
ROOM_PATH = os.path.expanduser("~/path/to/excalidraw-room")
SERVER_CMD = ["npm", "start"]      # Command to launch Excalidraw server
ROOM_CMD = ["npm", "start"]        # Command to launch Excalidraw Room server
SSH_HOST = "your-host"            # SSH host for tunneling

# Environment presets
ENVIRONMENTS = {
    "dev": {
        "server_port": 3000,
        "room_port": 3002,
        "remote_server_port": 3000,
        "remote_room_port": 3002,
    },
    "prod": {
        "server_port": 80,
        "room_port": 443,
        "remote_server_port": 80,
        "remote_room_port": 443,
    },
}

class ExcalimanTUI(App):
    """
    A Textual-based GPU TUI for Kitty that allows you to:
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
    room_proc = reactive(None)
    tunnel_proc = reactive([])
    monitor_tasks = reactive([])
    shutting_down = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with Container(id="controls"):
                yield Static("Environment:")
                yield Select(
                    [(name, name) for name in ENVIRONMENTS.keys()],
                    prompt="Select",
                    value=self.env,
                    id="env_select",
                )
                yield Button("Start Server", id="start_server")
                yield Button("Start Room", id="start_room")
                yield Button("Reset Room", id="reset_room")
                yield Button("Reboot All", id="reboot_all")
                yield Button("Exit All", id="exit_all")
                yield Static("Tunnel URL:", id="link_label")
                yield Static("", id="link_url")
            yield Log(highlight=True, id="log")
        yield Footer()

    async def on_mount(self):
        self.log_widget = self.query_one(Log)
        self.link_widget = self.query_one("#link_url", Static)
        self.update_link()

    def update_link(self):
        # Update displayed URL based on current environment
        port = ENVIRONMENTS[self.env]["server_port"]
        url = f"http://localhost:{port}"
        self.link_widget.update(url)

    async def on_select_changed(self, event: Select.Changed) -> None:
        self.env = event.value
        self.log_widget.write(f"Switched environment to [bold]{self.env}[/bold]")
        self.update_link()

    async def on_button_pressed(self, event):
        match event.button.id:
            case "start_server":
                await self.start_server()
            case "start_room":
                await self.start_room()
            case "reset_room":
                await self.reset_room()
            case "reboot_all":
                await self.reboot_all()
            case "exit_all":
                await self.exit_all()

    async def launch_process(self, cmd, cwd, name):
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self.monitor_tasks.append(asyncio.create_task(self.monitor_process(proc, name, cmd, cwd)))
        return proc

    async def monitor_process(self, proc, name, cmd, cwd):
        assert proc.stdout
        async for line in proc.stdout:
            self.log_widget.write(f"[{name}] {line.decode().rstrip()}")
        await proc.wait()
        self.log_widget.write(f"[red]{name} exited ({proc.returncode})[/red]")
        if not self.shutting_down:
            self.log_widget.write(f"Restarting {name}...")
            if name == "server":
                await self.start_server()
            elif name == "room":
                await self.start_room()

    async def start_tunnel(self, local_port: int, remote_port: int):
        self.log_widget.write(
            f"Tunneling port {local_port} -> localhost:{remote_port} via {SSH_HOST}..."
        )
        tunnel = await asyncio.create_subprocess_exec(
            "ssh",
            "-N",
            "-L",
            f"{local_port}:localhost:{remote_port}",
            SSH_HOST,
        )
        self.tunnel_proc.append(tunnel)
        return tunnel

    async def start_server(self):
        if self.server_proc and self.server_proc.returncode is None:
            self.log_widget.write("[yellow]Server already running[/yellow]")
            return
        self.log_widget.write("Starting Excalidraw server...")
        self.server_proc = await self.launch_process(SERVER_CMD, SERVER_PATH, "server")
        await asyncio.sleep(1)
        cfg = ENVIRONMENTS[self.env]
        await self.start_tunnel(cfg["server_port"], cfg["remote_server_port"])
        url = f"http://localhost:{cfg['server_port']}"
        self.log_widget.write(f"[green]Server tunnel active at {url}[/green]")
        webbrowser.open(url)

    async def start_room(self):
        if self.room_proc and self.room_proc.returncode is None:
            self.log_widget.write("[yellow]Room already running[/yellow]")
            return
        self.log_widget.write("Starting Excalidraw Room server...")
        self.room_proc = await self.launch_process(ROOM_CMD, ROOM_PATH, "room")
        await asyncio.sleep(1)
        cfg = ENVIRONMENTS[self.env]
        await self.start_tunnel(cfg["room_port"], cfg["remote_room_port"])
        self.log_widget.write(
            f"[green]Room tunnel active at http://localhost:{cfg['room_port']}[/green]"
        )

    async def reset_room(self):
        if not self.room_proc:
            return
        self.log_widget.write("Resetting room server...")
        self.room_proc.send_signal(signal.SIGINT)
        await self.room_proc.wait()
        self.room_proc = None
        await self.start_room()

    async def reboot_all(self):
        self.log_widget.write("Rebooting both server and room...")
        await self.exit_all()
        await self.start_server()
        await self.start_room()

    async def exit_all(self):
        self.log_widget.write("Stopping all services and tunnels...")
        self.shutting_down = True
        # Terminate room first, then server
        if self.room_proc:
            self.room_proc.send_signal(signal.SIGINT)
            await self.room_proc.wait()
            self.log_widget.write("Room server stopped")
        if self.server_proc:
            self.server_proc.send_signal(signal.SIGINT)
            await self.server_proc.wait()
            self.log_widget.write("Server stopped")
        # Close tunnels
        for tunnel in self.tunnel_proc:
            tunnel.terminate()
            await tunnel.wait()
        self.tunnel_proc.clear()
        self.log_widget.write("All tunnels closed")
        for task in self.monitor_tasks:
            task.cancel()
        self.monitor_tasks.clear()
        self.shutting_down = False

if __name__ == "__main__":
    ExcalimanTUI.run(title="Excaliman TUI")
