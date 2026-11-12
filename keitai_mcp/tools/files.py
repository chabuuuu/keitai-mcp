"""File transfer and filesystem inspection tools for Keitai."""

from __future__ import annotations

import logging
import os
import re
from typing import Any

from keitai_mcp.device.adb import ADBClient

logger = logging.getLogger("keitai_mcp.tools.files")


async def push_file(
    adb: ADBClient,
    local_path: str,
    remote_path: str,
) -> dict[str, Any]:
    """Push a local file or directory to the Keitai device.

    Args:
        adb: ADB client instance.
        local_path: Path on host machine.
        remote_path: Destination path on device (e.g. '/sdcard/Download/test.json').

    Returns:
        Transfer result summary.
    """
    output = await adb.push(local_path, remote_path)
    return {
        "success": True,
        "local_path": os.path.abspath(local_path),
        "remote_path": remote_path,
        "output": output,
    }


async def pull_file(
    adb: ADBClient,
    remote_path: str,
    local_path: str,
) -> dict[str, Any]:
    """Pull a file or directory from the Keitai to the host machine.

    Args:
        adb: ADB client instance.
        remote_path: Path on device.
        local_path: Destination path on host.

    Returns:
        Transfer result summary.
    """
    output = await adb.pull(remote_path, local_path)
    return {
        "success": True,
        "remote_path": remote_path,
        "local_path": os.path.abspath(local_path),
        "output": output,
    }


async def list_files(
    adb: ADBClient,
    remote_path: str = "/sdcard",
) -> list[dict[str, Any]]:
    """List files and directories at a given path on the Keitai.

    Args:
        adb: ADB client instance.
        remote_path: Directory path on device.

    Returns:
        List of entries with name, size, is_dir, permissions.
    """
    output = await adb.shell(f"ls -la '{remote_path}'")
    entries: list[dict[str, Any]] = []

    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("total"):
            continue

        parts = line.split()
        if len(parts) >= 8:
            perms = parts[0]
            is_dir = perms.startswith("d")
            name = " ".join(parts[7:]) if len(parts) >= 8 else parts[-1]
            if name in (".", ".."):
                continue

            size = parts[4] if not is_dir else "0"
            entries.append({
                "name": name,
                "is_dir": is_dir,
                "permissions": perms,
                "size_bytes": int(size) if size.isdigit() else size,
                "date": f"{parts[5]} {parts[6]}",
                "path": f"{remote_path.rstrip('/')}/{name}",
            })

    return entries
