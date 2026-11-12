"""Keypad and input interaction tools for Keitai devices."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from keitai_mcp.device.adb import ADBClient
from keitai_mcp.device.f03l import resolve_keycode

logger = logging.getLogger("keitai_mcp.tools.keypad")


async def press_key(
    adb: ADBClient,
    key: str,
    long_press: bool = False,
    count: int = 1,
    delay_ms: int = 150,
) -> dict[str, Any]:
    """Press a physical key on the Keitai keypad.

    Args:
        adb: ADB client instance.
        key: Key name (e.g. 'UP', 'DOWN', 'LEFT', 'RIGHT', 'CENTER', 'OK', 'BACK', 'CLR',
             'CALL', 'ENDCALL', 'F1', 'F2', '0'..'9', 'STAR', 'POUND', 'FAV1'..'FAV3').
        long_press: Whether to perform a long-press (useful for manner mode or quick menus).
        count: Number of times to press the key sequentially.
        delay_ms: Milliseconds between consecutive presses when count > 1.

    Returns:
        Summary dict of the action with keycode and status.
    """
    keycode = resolve_keycode(key)
    count = max(1, min(count, 50))  # limit count to reasonable bounds

    for i in range(count):
        cmd = f"input keyevent {'--longpress ' if long_press else ''}{keycode}"
        await adb.shell(cmd)
        if count > 1 and i < count - 1:
            await asyncio.sleep(delay_ms / 1000.0)

    return {
        "success": True,
        "key": key.upper(),
        "keycode": keycode,
        "count": count,
        "long_press": long_press,
    }


async def press_sequence(
    adb: ADBClient,
    keys: list[str],
    interval_ms: int = 250,
) -> dict[str, Any]:
    """Execute a sequence of physical key presses on the Keitai with specified intervals.

    Args:
        adb: ADB client instance.
        keys: List of key names to press in order (e.g. ['DOWN', 'DOWN', 'CENTER']).
        interval_ms: Milliseconds to wait between consecutive key presses.

    Returns:
        Summary dict of executed keys.
    """
    executed: list[dict[str, Any]] = []
    interval_sec = max(0.05, interval_ms / 1000.0)

    for idx, k in enumerate(keys):
        keycode = resolve_keycode(k)
        await adb.shell(f"input keyevent {keycode}")
        executed.append({"key": k.upper(), "keycode": keycode})
        if idx < len(keys) - 1:
            await asyncio.sleep(interval_sec)

    return {
        "success": True,
        "total_keys": len(executed),
        "sequence": executed,
    }


async def input_text(
    adb: ADBClient,
    text: str,
) -> dict[str, Any]:
    """Input alphanumeric text into the currently focused text field.

    Note: Android input text accepts ASCII characters. For spaces, %s is used.
    For non-ASCII / Japanese kanji, consider setting clipboard or using IME.

    Args:
        adb: ADB client instance.
        text: Text string to input.

    Returns:
        Result summary dict.
    """
    if not text:
        return {"success": True, "text": "", "length": 0}

    # Escape characters for shell input text
    # Spaces are encoded as %s in Android input tool
    escaped = text.replace(" ", "%s").replace("&", "\\&").replace("'", "\\'").replace('"', '\\"')
    cmd = f"input text {escaped}"
    await adb.shell(cmd)

    return {
        "success": True,
        "text": text,
        "length": len(text),
    }


async def tap(
    adb: ADBClient,
    x: int,
    y: int,
) -> dict[str, Any]:
    """Tap at specific screen coordinates (x, y).

    Even though the Fujitsu F-03L is a flip phone without standard touchscreen use,
    the Android subsystem accepts touchscreen coordinates, which is invaluable for testing
    or interacting with non-D-pad-optimized applications.

    Args:
        adb: ADB client instance.
        x: X coordinate (0-480).
        y: Y coordinate (0-854).

    Returns:
        Coordinates tapped.
    """
    x = max(0, min(x, 480))
    y = max(0, min(y, 854))
    await adb.shell(f"input tap {x} {y}")
    return {"success": True, "action": "tap", "x": x, "y": y}


async def swipe(
    adb: ADBClient,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration_ms: int = 300,
) -> dict[str, Any]:
    """Swipe across the screen between two points.

    Args:
        adb: ADB client instance.
        x1: Start X coordinate.
        y1: Start Y coordinate.
        x2: End X coordinate.
        y2: End Y coordinate.
        duration_ms: Duration of swipe in milliseconds.

    Returns:
        Swipe details.
    """
    duration_ms = max(50, duration_ms)
    await adb.shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")
    return {
        "success": True,
        "action": "swipe",
        "from": [x1, y1],
        "to": [x2, y2],
        "duration_ms": duration_ms,
    }


async def wake(adb: ADBClient) -> dict[str, Any]:
    """Wake up the Keitai screen if it is asleep."""
    is_on = await adb.is_screen_on()
    if not is_on:
        await adb.shell("input keyevent KEYCODE_WAKEUP")
        await asyncio.sleep(0.5)
    return {"success": True, "screen_on": True, "was_asleep": not is_on}


async def sleep(adb: ADBClient) -> dict[str, Any]:
    """Put the Keitai screen to sleep."""
    is_on = await adb.is_screen_on()
    if is_on:
        await adb.shell("input keyevent KEYCODE_SLEEP")
        await asyncio.sleep(0.3)
    return {"success": True, "screen_on": False, "was_on": is_on}

