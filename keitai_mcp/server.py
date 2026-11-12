"""Model Context Protocol (MCP) Server for Keitai (Fujitsu F-03L)."""

from __future__ import annotations

import logging
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
import mcp.types as types

from keitai_mcp.device.adb import ADBClient
from keitai_mcp.resources.guidelines import KEITAI_GUIDELINES_TEXT
from keitai_mcp.resources.keymap import KEYMAP_MD_TEXT
from keitai_mcp.resources.specs import F03L_SPECS_TEXT
from keitai_mcp.tools import apps, files, keypad, logs, screen, system, ui

logger = logging.getLogger("keitai_mcp.server")


def create_server(serial: str | None = None, adb_path: str = "adb") -> MCPServer:
    """Create and configure the Keitai MCP server."""
    adb = ADBClient(serial=serial, adb_path=adb_path)

    instructions = (
        "You are connected to a Japanese Keitai (feature flip phone), specifically the Fujitsu arrows Keitai F-03L, "
        "running Android 8.1.0 (API 27) with a 480x854 non-touch display, 5-way D-Pad, numeric keypad, and physical softkeys. "
        "Users navigate using the D-Pad (UP, DOWN, LEFT, RIGHT, CENTER/OK) and physical buttons (F1, F2, BACK/CLR, 0-9). "
        "Use the provided tools to inspect UI focus, capture screenshots, press physical keys, install APKs, "
        "diagnose crashes, and develop software tailored for this unique feature phone form factor."
    )

    server = MCPServer(
        name="keitai-mcp",
        version="0.1.0",
        instructions=instructions,
    )

    # ---------------------------------------------------------
    # 1. Keypad & Input Tools
    # ---------------------------------------------------------
    @server.tool()
    async def keitai_press_key(
        key: str,
        long_press: bool = False,
        count: int = 1,
        delay_ms: int = 150,
    ) -> dict[str, Any]:
        """Press a physical key on the Keitai keypad.

        Supported keys include:
        - D-Pad: 'UP', 'DOWN', 'LEFT', 'RIGHT', 'CENTER' (or 'OK', 'SELECT')
        - Navigation: 'BACK' (or 'CLR', 'CLEAR'), 'CALL', 'ENDCALL', 'HOME', 'MENU'
        - Softkeys: 'F1' (Left softkey / Submenu), 'F2' (Right softkey / Browser), 'F3', 'F4'
        - Numbers & Symbols: '0'..'9', 'STAR' ('*'), 'POUND' ('#')
        - Quick Launch: 'FAV1', 'FAV2', 'FAV3'
        - Side: 'VOL_UP', 'VOL_DOWN', 'CAMERA'
        """
        return await keypad.press_key(adb, key, long_press=long_press, count=count, delay_ms=delay_ms)

    @server.tool()
    async def keitai_press_sequence(
        keys: list[str],
        interval_ms: int = 250,
    ) -> dict[str, Any]:
        """Execute a sequence of physical key presses on the Keitai with specified intervals (e.g. ['DOWN', 'DOWN', 'CENTER'])."""
        return await keypad.press_sequence(adb, keys=keys, interval_ms=interval_ms)

    @server.tool()
    async def keitai_input_text(text: str) -> dict[str, Any]:
        """Input alphanumeric text into the currently focused text field."""
        return await keypad.input_text(adb, text=text)

    @server.tool()
    async def keitai_tap(x: int, y: int) -> dict[str, Any]:
        """Tap at specific screen coordinates (x, y) on the 480x854 canvas."""
        return await keypad.tap(adb, x=x, y=y)

    @server.tool()
    async def keitai_swipe(
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration_ms: int = 300,
    ) -> dict[str, Any]:
        """Swipe across the screen from (x1, y1) to (x2, y2)."""
        return await keypad.swipe(adb, x1=x1, y1=y1, x2=x2, y2=y2, duration_ms=duration_ms)

    @server.tool()
    async def keitai_wake() -> dict[str, Any]:
        """Wake up the Keitai screen if it is asleep."""
        return await keypad.wake(adb)

    @server.tool()
    async def keitai_sleep() -> dict[str, Any]:
        """Put the Keitai screen to sleep."""
        return await keypad.sleep(adb)

    # ---------------------------------------------------------
    # 2. Screen & Vision Tools
    # ---------------------------------------------------------
    @server.tool()
    async def keitai_take_screenshot(
        save_path: str | None = None,
        return_image: bool = True,
        max_width: int | None = None,
    ) -> list[types.ImageContent | types.TextContent]:
        """Capture a live screenshot of the Keitai screen for vision analysis and optional file saving."""
        return await screen.take_screenshot(
            adb,
            save_path=save_path,
            return_image=return_image,
            max_width=max_width,
        )

    # ---------------------------------------------------------
    # 3. UI Hierarchy & Focus Inspector
    # ---------------------------------------------------------
    @server.tool()
    async def keitai_inspect_ui(
        focused_only: bool = False,
        clickable_only: bool = False,
        max_depth: int = 8,
        output_format: Literal["tree", "json"] = "tree",
    ) -> str:
        """Dump the UI hierarchy on the Keitai screen, clearly tagging focused elements (★FOCUSED), clickable items, and coordinates."""
        return await ui.inspect_ui(
            adb,
            focused_only=focused_only,
            clickable_only=clickable_only,
            max_depth=max_depth,
            output_format=output_format,
        )

    @server.tool()
    async def keitai_get_focused_element() -> dict[str, Any]:
        """Retrieve details of the element currently focused by the D-pad cursor."""
        return await ui.get_focused_element(adb)

    @server.tool()
    async def keitai_find_element(
        query: str,
        search_by: Literal["text", "id", "class", "any"] = "any",
    ) -> list[dict[str, Any]]:
        """Search UI elements by text, resource ID, or class name to locate their screen coordinates and focusability."""
        return await ui.find_element(adb, query=query, search_by=search_by)

    # ---------------------------------------------------------
    # 4. Application Management
    # ---------------------------------------------------------
    @server.tool()
    async def keitai_install_apk(
        apk_path: str,
        grant_permissions: bool = True,
        reinstall: bool = True,
    ) -> dict[str, Any]:
        """Install an APK onto the Keitai (targets 32-bit armeabi-v7a / Android 8.1)."""
        return await apps.install_apk(
            adb,
            apk_path=apk_path,
            grant_permissions=grant_permissions,
            reinstall=reinstall,
        )

    @server.tool()
    async def keitai_uninstall_app(
        package_name: str,
        keep_data: bool = False,
    ) -> dict[str, Any]:
        """Uninstall an application package from the Keitai."""
        return await apps.uninstall_app(adb, package_name=package_name, keep_data=keep_data)

    @server.tool()
    async def keitai_launch_app(
        package_name: str,
        activity: str | None = None,
    ) -> dict[str, Any]:
        """Launch an application on the Keitai by package name."""
        return await apps.launch_app(adb, package_name=package_name, activity=activity)

    @server.tool()
    async def keitai_stop_app(package_name: str) -> dict[str, Any]:
        """Force stop a running application on the Keitai."""
        return await apps.stop_app(adb, package_name=package_name)

    @server.tool()
    async def keitai_clear_app(package_name: str) -> dict[str, Any]:
        """Clear user data and cache for an application on the Keitai."""
        return await apps.clear_app(adb, package_name=package_name)

    @server.tool()
    async def keitai_list_installed_apps(
        third_party_only: bool = True,
        filter_query: str | None = None,
    ) -> list[str]:
        """List installed packages on the Keitai (defaults to 3rd party apps)."""
        return await apps.list_installed_apps(adb, third_party_only=third_party_only, filter_query=filter_query)

    # ---------------------------------------------------------
    # 5. System Diagnostics & State
    # ---------------------------------------------------------
    @server.tool()
    async def keitai_get_device_info() -> dict[str, Any]:
        """Get comprehensive hardware specs, clamshell open/close status, battery, memory, storage, and focused app."""
        return await system.get_device_info(adb)

    @server.tool()
    async def keitai_get_battery() -> dict[str, Any]:
        """Get battery level percentage, temperature in Celsius, voltage, and charging state."""
        return await system.get_battery(adb)

    @server.tool()
    async def keitai_get_clamshell_state() -> dict[str, Any]:
        """Get the physical clamshell lid status (open vs closed) of the Keitai."""
        return await system.get_clamshell_state(adb)

    @server.tool()
    async def keitai_get_network_info() -> dict[str, Any]:
        """Get WiFi connection IP address, MAC address, and status."""
        return await system.get_network_info(adb)

    @server.tool()
    async def keitai_exec_shell(
        command: str,
        timeout_seconds: int = 15,
    ) -> dict[str, Any]:
        """Execute an arbitrary ADB shell command on the Keitai safely."""
        return await system.exec_shell(adb, command=command, timeout_seconds=timeout_seconds)

    # ---------------------------------------------------------
    # 6. Logs & Crash Traces
    # ---------------------------------------------------------
    @server.tool()
    async def keitai_read_logcat(
        package_name: str | None = None,
        tag: str | None = None,
        priority: Literal["V", "D", "I", "W", "E", "F"] = "V",
        lines: int = 100,
    ) -> str:
        """Read recent Android logcat entries with filtering by package, tag, and priority."""
        return await logs.read_logcat(
            adb,
            package_name=package_name,
            tag=tag,
            priority=priority,
            lines=lines,
        )

    @server.tool()
    async def keitai_clear_logcat() -> dict[str, Any]:
        """Clear the device logcat buffer."""
        return await logs.clear_logcat(adb)

    @server.tool()
    async def keitai_get_recent_crashes(package_name: str | None = None) -> str:
        """Retrieve recent crash logs, stack traces, and fatal exceptions from logcat crash buffer."""
        return await logs.get_recent_crashes(adb, package_name=package_name)

    # ---------------------------------------------------------
    # 7. File Operations
    # ---------------------------------------------------------
    @server.tool()
    async def keitai_push_file(local_path: str, remote_path: str) -> dict[str, Any]:
        """Push a file or directory from host to the Keitai."""
        return await files.push_file(adb, local_path=local_path, remote_path=remote_path)

    @server.tool()
    async def keitai_pull_file(remote_path: str, local_path: str) -> dict[str, Any]:
        """Pull a file or directory from the Keitai to host machine."""
        return await files.pull_file(adb, remote_path=remote_path, local_path=local_path)

    @server.tool()
    async def keitai_list_files(remote_path: str = "/sdcard") -> list[dict[str, Any]]:
        """List files and folders at a specified directory on the Keitai."""
        return await files.list_files(adb, remote_path=remote_path)

    # ---------------------------------------------------------
    # 8. Resources
    # ---------------------------------------------------------
    @server.resource("keitai://f03l/specs")
    def get_f03l_specs() -> str:
        """Fujitsu arrows Keitai F-03L complete technical specifications."""
        return F03L_SPECS_TEXT

    @server.resource("keitai://dev/guidelines")
    def get_dev_guidelines() -> str:
        """Comprehensive guide on building Android applications for Japanese Keitai flip phones."""
        return KEITAI_GUIDELINES_TEXT

    @server.resource("keitai://dev/keycodes")
    def get_keymap_reference() -> str:
        """Complete keycode catalog and physical mapping table for Fujitsu F-03L."""
        return KEYMAP_MD_TEXT

    # ---------------------------------------------------------
    # 9. Prompts
    # ---------------------------------------------------------
    @server.prompt()
    def plan_keitai_navigation(target_action: str) -> str:
        """Prompt to help an agent inspect the screen and plan D-pad steps to reach a UI target."""
        return (
            f"Objective: Reach and activate '{target_action}' on the Fujitsu F-03L Keitai.\n\n"
            "Steps for the Agent:\n"
            "1. Call `keitai_get_focused_element` or `keitai_inspect_ui` to identify the current focus position.\n"
            "2. Locate target element's relative direction (above, below, left, right).\n"
            "3. Use `keitai_press_key` with D-Pad ('UP', 'DOWN', 'LEFT', 'RIGHT') to navigate towards it.\n"
            "4. Verify focus is on the target element.\n"
            "5. Press 'CENTER' (OK) to activate."
        )

    @server.prompt()
    def diagnose_keitai_crash(package_name: str) -> str:
        """Prompt to retrieve and diagnose application crashes on Fujitsu F-03L."""
        return (
            f"Analyze recent crash traces for package '{package_name}' on Fujitsu F-03L.\n\n"
            "Instructions:\n"
            "1. Call `keitai_get_recent_crashes(package_name='{package_name}')` to retrieve stack traces.\n"
            "2. Check if the crash is caused by:\n"
            "   - Missing ABI support (ensure armeabi-v7a native libs are present).\n"
            "   - Touchscreen assumption (e.g. attempting to listen to touch events on non-focusable views).\n"
            "   - OutOfMemoryError (device has 1 GB RAM total).\n"
            "   - Unsupported newer Android API (device runs Android 8.1 / API 27).\n"
            "3. Provide recommended code fixes."
        )

    return server
