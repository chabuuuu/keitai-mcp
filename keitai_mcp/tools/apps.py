"""Application management tools for Keitai."""

from __future__ import annotations

import logging
import os
import re
from typing import Any

from keitai_mcp.device.adb import ADBClient, ADBError

logger = logging.getLogger("keitai_mcp.tools.apps")


async def install_apk(
    adb: ADBClient,
    apk_path: str,
    grant_permissions: bool = True,
    reinstall: bool = True,
) -> dict[str, Any]:
    """Install an APK onto the Keitai device.

    Note: Fujitsu F-03L runs 32-bit ARM (armeabi-v7a) on Android 8.1.
    Ensure APKs target 32-bit ARM or contain universal/armeabi-v7a native libraries.

    Args:
        adb: ADB client instance.
        apk_path: Absolute or relative local path to the APK file.
        grant_permissions: Automatically grant all runtime permissions (-g).
        reinstall: Allow reinstalling an existing app while keeping data (-r).

    Returns:
        Result summary dict.
    """
    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"APK file not found at: {apk_path}")

    args = ["install"]
    if reinstall:
        args.append("-r")
    if grant_permissions:
        args.append("-g")
    args.append(apk_path)

    serial = await adb._ensure_serial()
    code, stdout, stderr = await adb.execute(args, timeout=120.0, target_serial=serial)

    combined = f"{stdout}\n{stderr}".strip()
    if code != 0 or "Failure" in combined:
        raise ADBError(f"APK installation failed: {combined}", returncode=code, stdout=stdout, stderr=stderr)

    return {
        "success": True,
        "apk_path": os.path.abspath(apk_path),
        "output": combined,
    }


async def uninstall_app(
    adb: ADBClient,
    package_name: str,
    keep_data: bool = False,
) -> dict[str, Any]:
    """Uninstall an application package from the Keitai.

    Args:
        adb: ADB client instance.
        package_name: Package name (e.g. 'com.example.keitai_app').
        keep_data: Keep the app data and cache directories (-k).

    Returns:
        Result summary dict.
    """
    args = ["uninstall"]
    if keep_data:
        args.append("-k")
    args.append(package_name)

    serial = await adb._ensure_serial()
    code, stdout, stderr = await adb.execute(args, timeout=30.0, target_serial=serial)
    combined = f"{stdout}\n{stderr}".strip()

    if code != 0 or "Failure" in combined:
        raise ADBError(f"App uninstall failed: {combined}", returncode=code, stdout=stdout, stderr=stderr)

    return {"success": True, "package": package_name, "output": combined}


async def launch_app(
    adb: ADBClient,
    package_name: str,
    activity: str | None = None,
) -> dict[str, Any]:
    """Launch an application on the Keitai.

    Args:
        adb: ADB client instance.
        package_name: Application package name.
        activity: Optional specific activity name. If omitted, uses Monkey to launch main activity.

    Returns:
        Launch status dict.
    """
    if activity:
        act = activity if activity.startswith(".") or "/" in activity else f".{activity}"
        target = f"{package_name}/{act}" if "/" not in act else act
        output = await adb.shell(f"am start -n {target}")
    else:
        # Use monkey launcher
        output = await adb.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")

    return {
        "success": True,
        "package": package_name,
        "activity": activity,
        "output": output.strip(),
    }


async def stop_app(
    adb: ADBClient,
    package_name: str,
) -> dict[str, Any]:
    """Force stop a running application on the Keitai.

    Args:
        adb: ADB client instance.
        package_name: Package name to kill.

    Returns:
        Result summary dict.
    """
    await adb.shell(f"am force-stop {package_name}")
    return {"success": True, "package": package_name, "action": "force-stop"}


async def clear_app(
    adb: ADBClient,
    package_name: str,
) -> dict[str, Any]:
    """Clear data and cache for an application.

    Args:
        adb: ADB client instance.
        package_name: Application package name.

    Returns:
        Result summary dict.
    """
    output = await adb.shell(f"pm clear {package_name}")
    return {"success": "Success" in output, "package": package_name, "output": output.strip()}


async def list_installed_apps(
    adb: ADBClient,
    third_party_only: bool = True,
    filter_query: str | None = None,
) -> list[str]:
    """List installed application packages on the Keitai.

    Args:
        adb: ADB client instance.
        third_party_only: If True, only lists user-installed 3rd party apps (-3).
                          If False, lists all packages including system packages.
        filter_query: Optional substring to filter package names.

    Returns:
        List of package names.
    """
    flag = "-3" if third_party_only else ""
    output = await adb.shell(f"pm list packages {flag}")
    packages: list[str] = []

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            pkg = line.replace("package:", "").strip()
            if not filter_query or filter_query.lower() in pkg.lower():
                packages.append(pkg)

    return sorted(packages)

