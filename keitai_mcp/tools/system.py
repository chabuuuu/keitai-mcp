"""Device diagnostics, battery, clamshell, and system tools for Keitai."""

from __future__ import annotations

import logging
import re
from typing import Any

from keitai_mcp.device.adb import ADBClient
from keitai_mcp.device.f03l import (
    DEVICE_BRAND,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    SCREEN_DENSITY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SUB_DISPLAY_HEIGHT,
    SUB_DISPLAY_TYPE,
    SUB_DISPLAY_WIDTH,
    TARGET_ABI,
    TARGET_ANDROID_VERSION,
    TARGET_SDK_INT,
)

logger = logging.getLogger("keitai_mcp.tools.system")


async def get_device_info(adb: ADBClient) -> dict[str, Any]:
    """Retrieve comprehensive device status, specifications, and hardware profile.

    Returns detailed info on Fujitsu F-03L including CPU ABI, screen resolution,
    clamshell lid open/close status, battery health, RAM, storage, and focused app.

    Args:
        adb: ADB client instance.

    Returns:
        Structured dictionary of device specifications and live state.
    """
    props = await adb.get_all_props()
    pkg, activity = await adb.get_current_focus()
    lid_state = await adb.get_lid_state()
    screen_on = await adb.is_screen_on()
    battery = await adb.get_battery_info()
    wifi = await adb.get_wifi_info()

    # Parse memory from /proc/meminfo
    mem_info: dict[str, str] = {}
    try:
        mem_raw = await adb.shell("cat /proc/meminfo")
        for line in mem_raw.splitlines()[:5]:
            if ":" in line:
                k, v = line.split(":", 1)
                mem_info[k.strip()] = v.strip()
    except Exception:
        pass

    # Storage info
    storage_info: dict[str, str] = {}
    try:
        df_raw = await adb.shell("df -h /data")
        lines = df_raw.strip().splitlines()
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 6:
                storage_info = {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "use_percent": parts[4],
                    "mount": parts[5],
                }
    except Exception:
        pass

    lid_str = "open" if lid_state == 1 else "closed" if lid_state == 0 else "unknown"

    return {
        "hardware": {
            "model": props.get("ro.product.model", DEVICE_MODEL),
            "manufacturer": props.get("ro.product.manufacturer", DEVICE_MANUFACTURER),
            "brand": props.get("ro.product.brand", DEVICE_BRAND),
            "device": props.get("ro.product.device", DEVICE_MODEL),
            "board": props.get("ro.product.board", "F03L"),
            "cpu_abi": props.get("ro.product.cpu.abi", TARGET_ABI),
            "cpu_abilist": props.get("ro.product.cpu.abilist", TARGET_ABI),
        },
        "software": {
            "android_version": props.get("ro.build.version.release", TARGET_ANDROID_VERSION),
            "sdk_int": int(props.get("ro.build.version.sdk", TARGET_SDK_INT)),
            "security_patch": props.get("ro.build.version.security_patch", "2019-06-01"),
            "build_id": props.get("ro.build.display.id", ""),
        },
        "displays": {
            "main_display": {
                "width": SCREEN_WIDTH,
                "height": SCREEN_HEIGHT,
                "density_dpi": SCREEN_DENSITY,
                "resolution": f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}",
                "screen_power": "ON" if screen_on else "OFF",
            },
            "sub_display": {
                "width": SUB_DISPLAY_WIDTH,
                "height": SUB_DISPLAY_HEIGHT,
                "type": SUB_DISPLAY_TYPE,
            },
        },
        "clamshell": {
            "lid_state": lid_str,
            "lid_code": lid_state,
        },
        "power_battery": {
            "level_percent": battery.get("level", 0),
            "temperature_c": round(battery.get("temperature", 0) / 10.0, 1) if "temperature" in battery else None,
            "voltage_mv": battery.get("voltage", 0),
            "charging_ac": battery.get("AC powered", False),
            "charging_usb": battery.get("USB powered", False),
            "health": battery.get("health", 2),
        },
        "memory_ram": {
            "total": mem_info.get("MemTotal", "Unknown"),
            "available": mem_info.get("MemAvailable", "Unknown"),
            "free": mem_info.get("MemFree", "Unknown"),
        },
        "internal_storage": storage_info,
        "network": wifi,
        "current_focus": {
            "package": pkg,
            "activity": activity,
        },
    }


async def get_battery(adb: ADBClient) -> dict[str, Any]:
    """Get battery level, charging status, and temperature."""
    raw = await adb.get_battery_info()
    temp_c = round(raw.get("temperature", 0) / 10.0, 1) if "temperature" in raw else None
    return {
        "level_percent": raw.get("level", 0),
        "temperature_c": temp_c,
        "voltage_mv": raw.get("voltage", 0),
        "status": raw.get("status", 0),
        "health": raw.get("health", 2),
        "ac_powered": raw.get("AC powered", False),
        "usb_powered": raw.get("USB powered", False),
    }


async def get_clamshell_state(adb: ADBClient) -> dict[str, Any]:
    """Get the physical clamshell (flip lid) status of the Keitai."""
    code = await adb.get_lid_state()
    desc = "OPEN (flip is opened)" if code == 1 else "CLOSED (flip is closed)" if code == 0 else "UNKNOWN"
    return {
        "lid_state": "open" if code == 1 else "closed" if code == 0 else "unknown",
        "code": code,
        "description": desc,
    }


async def get_network_info(adb: ADBClient) -> dict[str, Any]:
    """Get WiFi network IP, MAC address, and status."""
    return await adb.get_wifi_info()


async def exec_shell(
    adb: ADBClient,
    command: str,
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    """Execute an arbitrary ADB shell command on the Keitai.

    Args:
        adb: ADB client instance.
        command: Shell command string to execute.
        timeout_seconds: Command timeout in seconds.

    Returns:
        Dictionary containing exit_code, stdout, and stderr.
    """
    serial = await adb._ensure_serial()
    code, stdout, stderr = await adb.execute(["shell", command], timeout=float(timeout_seconds), target_serial=serial)
    return {
        "exit_code": code,
        "stdout": stdout,
        "stderr": stderr,
        "command": command,
    }
