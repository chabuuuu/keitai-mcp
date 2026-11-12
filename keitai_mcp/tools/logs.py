"""Logcat inspection and crash diagnostics for Keitai."""

from __future__ import annotations

import logging
from typing import Any, Literal

from keitai_mcp.device.adb import ADBClient

logger = logging.getLogger("keitai_mcp.tools.logs")


async def read_logcat(
    adb: ADBClient,
    package_name: str | None = None,
    tag: str | None = None,
    priority: Literal["V", "D", "I", "W", "E", "F"] = "V",
    lines: int = 100,
) -> str:
    """Read recent Android logcat entries with filtering.

    Args:
        adb: ADB client instance.
        package_name: Optional package name to filter logs to that app's process ID.
        tag: Optional log tag to filter (e.g. 'ActivityManager', 'MyKeitaiApp').
        priority: Minimum log priority ('V'=Verbose, 'D'=Debug, 'I'=Info, 'W'=Warn, 'E'=Error, 'F'=Fatal).
        lines: Number of recent log lines to retrieve (default 100).

    Returns:
        Filtered logcat text output.
    """
    lines = max(10, min(lines, 1000))
    filter_expr = f"{tag}:{priority} *:S" if tag else f"*:{priority}"

    pid = None
    if package_name:
        try:
            pid_out = await adb.shell(f"pidof -s {package_name}")
            if pid_out.strip().isdigit():
                pid = pid_out.strip()
        except Exception:
            pass

    cmd = f"logcat -d -t {lines}"
    if pid:
        cmd += f" --pid={pid}"
    cmd += f" {filter_expr}"

    try:
        output = await adb.shell(cmd, timeout=10.0)
        return output.strip() if output.strip() else f"No logs matching filter ({filter_expr})."
    except Exception as e:
        return f"Error reading logcat: {e}"


async def clear_logcat(adb: ADBClient) -> dict[str, Any]:
    """Clear the logcat buffer on the Keitai."""
    await adb.shell("logcat -c")
    return {"success": True, "message": "Logcat buffer cleared"}


async def get_recent_crashes(
    adb: ADBClient,
    package_name: str | None = None,
) -> str:
    """Retrieve crash traces from logcat crash buffer and fatal exception traces.

    Args:
        adb: ADB client instance.
        package_name: Optional package name to filter crashes for.

    Returns:
        Recent crash reports and stack traces.
    """
    crashes: list[str] = []

    # 1. Check crash ring buffer
    try:
        crash_buf = await adb.shell("logcat -d -b crash -t 150")
        if crash_buf.strip():
            crashes.append(f"--- Crash Ring Buffer ---\n{crash_buf.strip()}")
    except Exception:
        pass

    # 2. Check FATAL EXCEPTION in main logcat
    try:
        fatal_logs = await adb.shell("logcat -d -t 200 | grep -A 25 -B 2 'FATAL EXCEPTION'")
        if fatal_logs.strip():
            crashes.append(f"--- Fatal Exceptions ---\n{fatal_logs.strip()}")
    except Exception:
        pass

    # 3. Check ANR traces if available
    try:
        anr_traces = await adb.shell("tail -n 60 /data/anr/traces.txt 2>/dev/null")
        if anr_traces.strip():
            crashes.append(f"--- Recent ANR Trace ---\n{anr_traces.strip()}")
    except Exception:
        pass

    if not crashes:
        return "No recent crashes or fatal exceptions found on the device."

    full_report = "\n\n".join(crashes)
    if package_name:
        lines = [line for line in full_report.splitlines() if package_name in line or "---" in line or "Exception" in line or "at " in line]
        return "\n".join(lines) if lines else f"No crashes mentioning package '{package_name}' found."

    return full_report

