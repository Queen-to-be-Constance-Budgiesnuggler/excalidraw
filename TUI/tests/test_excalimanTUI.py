import asyncio
import pytest

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
import TUI.excalimanTUI as etm

etm.SERVER_CMD = ["python", "-c", "print('server')"]
etm.ROOM_CMD = ["python", "-c", "print('room')"]
etm.SERVER_PATH = "."
etm.ROOM_PATH = "."

class TestManager(etm.ExcalimanTUI):
    async def start_tunnel(self, local_port: int, remote_port: int):
        proc = await asyncio.create_subprocess_exec("true")
        self.tunnel_proc.append(proc)
        return proc

@pytest.mark.asyncio
async def test_start_server():
    app = TestManager()
    async with app.run_test() as pilot:
        await pilot.click("#start_server")
        assert app.server_proc is not None
        await app.exit_all()
