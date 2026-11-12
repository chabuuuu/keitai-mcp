"""Unit tests for ADB parser logic and device detection."""

import pytest
from keitai_mcp.device.adb import ADBClient, DeviceInfo


def test_device_info_f03l_detection():
    dev_f03l = DeviceInfo(
        serial="96344868",
        state="device",
        product="F03L",
        model="F_03L",
        device="F03L",
    )
    assert dev_f03l.is_f03l is True

    dev_pixel = DeviceInfo(
        serial="123456",
        state="device",
        product="oriole",
        model="Pixel 6",
        device="oriole",
    )
    assert dev_pixel.is_f03l is False


@pytest.mark.asyncio
async def test_get_devices_parsing(monkeypatch):
    sample_output = (
        "List of devices attached\n"
        "96344868               device usb:1-2.2 product:F03L model:F_03L device:F03L transport_id:1\n"
        "emulator-5554          offline transport_id:2\n"
    )

    async def mock_execute(self, cmd, timeout=5.0, target_serial=None):
        return 0, sample_output, ""

    monkeypatch.setattr(ADBClient, "execute", mock_execute)

    client = ADBClient()
    devices = await client.get_devices()

    assert len(devices) == 2
    assert devices[0].serial == "96344868"
    assert devices[0].state == "device"
    assert devices[0].is_f03l is True
    assert devices[1].serial == "emulator-5554"
    assert devices[1].state == "offline"


@pytest.mark.asyncio
async def test_focus_parsing(monkeypatch):
    dumpsys_output = (
        "  mCurrentFocus=Window{4588358 u0 com.nttdocomo.android.afphome/com.nttdocomo.android.afphome.homemain.HomeMainActivity}\n"
    )

    async def mock_shell(self, cmd, timeout=15.0):
        return dumpsys_output

    monkeypatch.setattr(ADBClient, "shell", mock_shell)

    client = ADBClient(serial="96344868")
    pkg, act = await client.get_current_focus()
    assert pkg == "com.nttdocomo.android.afphome"
    assert act == "com.nttdocomo.android.afphome.homemain.HomeMainActivity"


@pytest.mark.asyncio
async def test_battery_parsing(monkeypatch):
    battery_output = (
        "Current Battery Service state:\n"
        "  AC powered: true\n"
        "  USB powered: false\n"
        "  level: 85\n"
        "  scale: 100\n"
        "  voltage: 4100\n"
        "  temperature: 310\n"
    )

    async def mock_shell(self, cmd, timeout=15.0):
        return battery_output

    monkeypatch.setattr(ADBClient, "shell", mock_shell)

    client = ADBClient(serial="96344868")
    bat = await client.get_battery_info()
    assert bat["AC powered"] is True
    assert bat["level"] == 85
    assert bat["temperature"] == 310

