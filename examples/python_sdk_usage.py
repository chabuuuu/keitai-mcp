"""Example: Automating Fujitsu F-03L using the Keitai MCP Python API."""

import asyncio
from keitai_mcp.device.adb import ADBClient
from keitai_mcp.device.inspector import UIInspector
from keitai_mcp.tools import keypad, screen, system, ui


async def main():
    # 1. Initialize ADB Client
    adb = ADBClient()

    # 2. Query hardware details
    info = await system.get_device_info(adb)
    print(f"Connected to: {info['hardware']['manufacturer']} {info['hardware']['model']}")
    print(f"Battery: {info['power_battery']['level_percent']}% | Flip Lid: {info['clamshell']['lid_state']}")

    # 3. Ensure device is awake
    await keypad.wake(adb)

    # 4. Dump UI hierarchy and check focused element
    focused = await ui.get_focused_element(adb)
    print(f"Currently focused element: {focused.get('class')} - '{focused.get('text')}'")

    # 5. Capture screenshot
    print("Capturing screen...")
    await screen.take_screenshot(adb, save_path="f03l_example_capture.png")
    print("Saved screenshot to 'f03l_example_capture.png'")

    # 6. Navigate using physical D-Pad
    print("Navigating D-Pad: DOWN -> DOWN -> CENTER")
    await keypad.press_sequence(adb, keys=["DOWN", "DOWN", "CENTER"], interval_ms=300)

    # 7. Query updated focus
    focused_after = await ui.get_focused_element(adb)
    print(f"New focus after navigation: {focused_after.get('class')} - '{focused_after.get('text')}'")


if __name__ == "__main__":
    asyncio.run(main())
