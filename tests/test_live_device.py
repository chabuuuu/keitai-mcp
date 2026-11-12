"""Integration tests with live connected Fujitsu F-03L device."""

import pytest
from keitai_mcp.device.adb import ADBClient
from keitai_mcp.tools import keypad, screen, system, ui


@pytest.fixture
async def live_client():
    client = ADBClient()
    try:
        devices = await client.get_devices()
        f03l = [d for d in devices if d.state == "device"]
        if not f03l:
            pytest.skip("No online ADB device connected for live integration tests.")
        return client
    except Exception:
        pytest.skip("ADB daemon not accessible.")


@pytest.mark.asyncio
async def test_live_device_info(live_client):
    info = await system.get_device_info(live_client)
    assert "hardware" in info
    assert info["hardware"]["model"] in ("F-03L", "F_03L")
    assert info["software"]["android_version"] == "8.1.0"
    assert info["displays"]["main_display"]["resolution"] == "480x854"


@pytest.mark.asyncio
async def test_live_battery(live_client):
    battery = await system.get_battery(live_client)
    assert 0 <= battery["level_percent"] <= 100
    assert battery["voltage_mv"] > 3000


@pytest.mark.asyncio
async def test_live_clamshell_state(live_client):
    lid = await system.get_clamshell_state(live_client)
    assert lid["lid_state"] in ("open", "closed", "unknown")


@pytest.mark.asyncio
async def test_live_ui_dump(live_client):
    tree_text = await ui.inspect_ui(live_client, max_depth=3)
    assert len(tree_text) > 0


@pytest.mark.asyncio
async def test_live_screenshot_capture(live_client, tmp_path):
    target_png = str(tmp_path / "live_test.png")
    contents = await screen.take_screenshot(live_client, save_path=target_png, return_image=True)
    assert len(contents) == 2
    assert contents[0].type == "text"
    assert contents[1].type == "image"

