"""Asynchronous ADB Client tailored for Fujitsu F-03L and Keitai devices."""

from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass
from typing import Final

logger = logging.getLogger("keitai_mcp.adb")


class ADBError(RuntimeError):
    """Exception raised when an ADB command fails."""

    def __init__(self, message: str, returncode: int = -1, stdout: str = "", stderr: str = ""):
        super().__init__(message)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@dataclass
class DeviceInfo:
    """Summary of connected device detected via ADB."""
    serial: str
    state: str
    product: str = ""
    model: str = ""
    device: str = ""
    transport_id: str = ""

    @property
    def is_f03l(self) -> bool:
        """Check if this device is the Fujitsu F-03L."""
        values = [self.product, self.model, self.device]
        return any("F03L" in v.upper() or "F_03L" in v.upper() or "F-03L" in v.upper() for v in values)


class ADBClient:
    """High-level async client for communicating with Android Keitai via ADB."""

    DEFAULT_TIMEOUT: Final[float] = 15.0

    def __init__(self, serial: str | None = None, adb_path: str = "adb"):
        self.serial = serial
        self.adb_path = adb_path
        self._cached_serial: str | None = serial

    async def _ensure_serial(self) -> str:
        """Resolve and verify device serial."""
        if self._cached_serial:
            return self._cached_serial

        devices = await self.get_devices()
        if not devices:
            raise ADBError("No ADB devices connected. Please connect your Keitai via USB with USB Debugging enabled.")

        # Prioritize Fujitsu F-03L if connected
        f03l_device = next((d for d in devices if d.is_f03l and d.state == "device"), None)
        if f03l_device:
            self._cached_serial = f03l_device.serial
            return self._cached_serial

        # Otherwise pick the first online device
        online_devices = [d for d in devices if d.state == "device"]
        if not online_devices:
            raise ADBError(f"No online ADB devices found. Detected devices: {[d.serial + ' (' + d.state + ')' for d in devices]}")

        self._cached_serial = online_devices[0].serial
        return self._cached_serial

    def _build_cmd(self, subcmd: list[str], target_serial: str | None) -> list[str]:
        cmd = [self.adb_path]
        if target_serial:
            cmd.extend(["-s", target_serial])
        cmd.extend(subcmd)
        return cmd

    async def execute(
        self,
        subcmd: list[str],
        timeout: float = DEFAULT_TIMEOUT,
        target_serial: str | None = None,
    ) -> tuple[int, str, str]:
        """Execute a general ADB command."""
        serial = target_serial or (self._cached_serial if subcmd and subcmd[0] not in ("devices", "version", "kill-server", "start-server") else None)
        cmd = self._build_cmd(subcmd, serial)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_b, stderr_b = await asyncio.wait_for(process.communicate(), timeout=timeout)
            stdout = stdout_b.decode("utf-8", errors="replace")
            stderr = stderr_b.decode("utf-8", errors="replace")
            return process.returncode or 0, stdout, stderr
        except asyncio.TimeoutError:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            raise ADBError(f"ADB command timed out after {timeout}s: {' '.join(cmd)}")
        except FileNotFoundError:
            raise ADBError(f"ADB executable not found at '{self.adb_path}'. Please ensure Android SDK Platform-Tools are installed and on PATH.")

    async def shell(self, command: str, timeout: float = DEFAULT_TIMEOUT) -> str:
        """Run an ADB shell command and return stdout string."""
        serial = await self._ensure_serial()
        code, stdout, stderr = await self.execute(["shell", command], timeout=timeout, target_serial=serial)
        if code != 0:
            raise ADBError(
                f"ADB shell command failed with exit code {code}: {command}\n{stderr.strip() or stdout.strip()}",
                returncode=code,
                stdout=stdout,
                stderr=stderr,
            )
        return stdout

    async def shell_raw(self, command: str, timeout: float = DEFAULT_TIMEOUT) -> bytes:
        """Run an ADB shell command and return raw stdout bytes."""
        serial = await self._ensure_serial()
        cmd = self._build_cmd(["shell", command], serial)
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_b, stderr_b = await asyncio.wait_for(process.communicate(), timeout=timeout)
            return stdout_b
        except asyncio.TimeoutError:
            process.kill()
            raise ADBError(f"ADB shell timed out after {timeout}s: {command}")

    async def exec_out(self, args: list[str], timeout: float = DEFAULT_TIMEOUT) -> bytes:
        """Execute `adb exec-out` directly without PTY transformation (vital for binary screenshots)."""
        serial = await self._ensure_serial()
        cmd = self._build_cmd(["exec-out", *args], serial)
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_b, stderr_b = await asyncio.wait_for(process.communicate(), timeout=timeout)
            if process.returncode != 0:
                raise ADBError(
                    f"ADB exec-out failed (code {process.returncode}): {stderr_b.decode('utf-8', errors='replace')}",
                    returncode=process.returncode or -1,
                )
            return stdout_b
        except asyncio.TimeoutError:
            process.kill()
            raise ADBError(f"ADB exec-out timed out after {timeout}s: {' '.join(args)}")

    async def get_devices(self) -> list[DeviceInfo]:
        """List all connected ADB devices with model and product info."""
        code, stdout, _ = await self.execute(["devices", "-l"], timeout=5.0)
        devices: list[DeviceInfo] = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("List of devices") or line.startswith("*"):
                continue

            parts = line.split()
            if len(parts) >= 2:
                serial = parts[0]
                state = parts[1]
                extra: dict[str, str] = {}
                for item in parts[2:]:
                    if ":" in item:
                        k, v = item.split(":", 1)
                        extra[k] = v
                devices.append(
                    DeviceInfo(
                        serial=serial,
                        state=state,
                        product=extra.get("product", ""),
                        model=extra.get("model", ""),
                        device=extra.get("device", ""),
                        transport_id=extra.get("transport_id", ""),
                    )
                )
        return devices

    async def screencap(self) -> bytes:
        """Capture screenshot as raw PNG bytes."""
        return await self.exec_out(["screencap", "-p"], timeout=10.0)

    async def get_prop(self, prop_name: str) -> str:
        """Get a single Android system property."""
        res = await self.shell(f"getprop {prop_name}")
        return res.strip()

    async def get_all_props(self) -> dict[str, str]:
        """Get all Android system properties as a dictionary."""
        output = await self.shell("getprop")
        props: dict[str, str] = {}
        pattern = re.compile(r"^\[(.*?)\]: \[(.*?)\]$")
        for line in output.splitlines():
            m = pattern.match(line.strip())
            if m:
                props[m.group(1)] = m.group(2)
        return props

    async def get_current_focus(self) -> tuple[str | None, str | None]:
        """Get the package and activity of the currently focused window.

        Returns:
            (package_name, activity_name) or (None, None)
        """
        output = await self.shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
        # Example 1: mCurrentFocus=Window{4588358 u0 com.nttdocomo.android.afphome/com.nttdocomo.android.afphome.homemain.HomeMainActivity}
        m = re.search(r"mCurrentFocus=Window\{[0-9a-fA-F]+\s+u\d+\s+([^\s/]+)/([^\s\}]+)\}", output)
        if m:
            return m.group(1), m.group(2)

        # Example 2: mFocusedApp=AppWindowToken{5b9c1fc token=Token{940b0c9 ActivityRecord{bb87093 u0 com.pkg/.Activity t2}}}
        m = re.search(r"ActivityRecord\{[0-9a-fA-F]+\s+u\d+\s+([^\s/]+)/([^\s\}]+)", output)
        if m:
            return m.group(1), m.group(2)

        return None, None

    async def is_screen_on(self) -> bool:
        """Check if display power is ON."""
        output = await self.shell("dumpsys power | grep -iE 'mWakefulness=|Display Power:'")
        if "mWakefulness=Awake" in output or "Display Power: state=ON" in output:
            return True
        return False

    async def get_lid_state(self) -> int:
        """Check the clamshell lid state (0=closed, 1=open, -1=unknown)."""
        output = await self.shell("dumpsys window policy | grep -i 'mLidState'")
        m = re.search(r"mLidState=(-?\d+)", output)
        if m:
            return int(m.group(1))
        return -1

    async def get_battery_info(self) -> dict[str, str | int | bool]:
        """Get parsed battery status information."""
        output = await self.shell("dumpsys battery")
        info: dict[str, str | int | bool] = {}
        for line in output.splitlines():
            line = line.strip()
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v.lower() == "true":
                    info[k] = True
                elif v.lower() == "false":
                    info[k] = False
                elif v.lstrip("-").isdigit():
                    info[k] = int(v)
                else:
                    info[k] = v
        return info

    async def get_wifi_info(self) -> dict[str, str]:
        """Get IP address and WiFi interface status."""
        info: dict[str, str] = {"status": "disconnected", "ip": "", "mac": ""}
        try:
            output = await self.shell("ip addr show wlan0")
            if "state UP" in output:
                info["status"] = "connected"
            m_ip = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", output)
            if m_ip:
                info["ip"] = m_ip.group(1)
            m_mac = re.search(r"link/ether ([0-9a-fA-F:]{17})", output)
            if m_mac:
                info["mac"] = m_mac.group(1)
        except Exception:
            pass
        return info

    async def push(self, local_path: str, remote_path: str, timeout: float = 60.0) -> str:
        """Push a local file or directory to the device."""
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file does not exist: {local_path}")
        serial = await self._ensure_serial()
        code, stdout, stderr = await self.execute(["push", local_path, remote_path], timeout=timeout, target_serial=serial)
        if code != 0:
            raise ADBError(f"Push failed: {stderr or stdout}", returncode=code)
        return stdout.strip()

    async def pull(self, remote_path: str, local_path: str, timeout: float = 60.0) -> str:
        """Pull a file from the device to local filesystem."""
        serial = await self._ensure_serial()
        code, stdout, stderr = await self.execute(["pull", remote_path, local_path], timeout=timeout, target_serial=serial)
        if code != 0:
            raise ADBError(f"Pull failed: {stderr or stdout}", returncode=code)
        return stdout.strip()

