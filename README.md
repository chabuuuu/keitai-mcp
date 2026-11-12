# Keitai MCP 📱

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![MCP: Supported](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)
[![Hardware: Fujitsu F-03L](https://img.shields.io/badge/Hardware-Fujitsu%20F--03L%20Verified-brightgreen.svg)](#hardware-profile)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Keitai MCP** is an open-source [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server and developer toolset designed specifically for AI agents (such as Antigravity, Claude, Cursor, Windsurf) and developers to interact with, automate, and develop software for Japanese Android feature phones ("ガラケー" / Garakei / Keitai), with first-class support for the **Fujitsu arrows ケータイ F-03L** (NTT DOCOMO).

---

## 🌟 Why Keitai MCP?

Japanese Android flip phones like the Fujitsu F-03L are unique beasts:
- **No standard touchscreen**: Navigation is driven primarily by a **5-way physical D-Pad**, numeric keypad (0–9, *, #), and dedicated softkeys (`F1`, `F2`, `CLR`, `CALL`, `ENDCALL`).
- **Compact resolution**: 480 × 854 FWVGA display at 240 dpi.
- **Clamshell form factor**: Physical lid open/close sensor (`gpio_lid`).
- **Architecture**: 32-bit ARM (`armeabi-v7a`) on Qualcomm Snapdragon 210 running Android 8.1 Oreo (API 27) with 1 GB RAM.

Most general-purpose Android automation tools assume high-resolution touchscreens and modern touch gestures. When AI agents attempt to operate a Keitai, they often fail because they don't know:
1. Which UI element currently has **D-Pad focus**.
2. How to map physical keys (`UP`, `DOWN`, `CENTER`, `CLR`, `F1`, `FAV1`).
3. That screenshots must be scaled and captured efficiently without crashing low-memory buffers.
4. How to detect clamshell open/close states.

**Keitai MCP bridges this gap completely.** It equips LLM agents with native Keitai awareness, real-time vision, focus tracking, and hardware key controls.

---

## ✨ Features

- 🎮 **Physical Keypad Control**: Send individual key events, long-presses, and complex multi-key sequences (`UP`, `DOWN`, `CENTER`/`OK`, `BACK`/`CLR`, `F1`, `F2`, `0`–`9`, `STAR`, `POUND`, `FAV1`–`FAV3`).
- 👁️ **Live Screen Vision**: Capture 480×854 screenshots returned directly as MCP `ImageContent` for multimodal vision models, with automatic metadata (current package/activity).
- 🔍 **Token-Efficient UI Hierarchy**: Automatically parses `uiautomator dump` XML into a clean, readable text tree, clearly marking `[★FOCUSED]` elements, `[CLICKABLE]` items, and exact bounding box coordinates.
- 📦 **App Management**: Install APKs (with automated `armeabi-v7a` compatibility checks and runtime permissions), launch activities, force-stop, and clear app data.
- 🩺 **Hardware & Battery Diagnostics**: Real-time status of battery percentage, temperature (°C), voltage, clamshell lid state (`OPEN` / `CLOSED`), RAM availability, and Wi-Fi IP address.
- 📜 **Logcat & Crash Diagnostics**: Query logcat filtered by package PID, inspect the Android crash ring buffer (`logcat -b crash`), and capture fatal exception stack traces.
- 📁 **Device File Transfer**: Seamless `push`, `pull`, and `ls` on internal storage and microSD card.
- 📚 **Embedded MCP Resources & Prompts**: Built-in F-03L hardware specification sheets, Android Keitai development guidelines, and step-by-step navigation prompts.
- 💻 **Rich CLI**: Includes the `keitai-mcp` CLI for quick terminal inspection, device discovery, screenshots, and key injection.

---

## 📋 Requirements

1. **Host Machine**: Linux, macOS, or Windows.
2. **Python**: Python 3.10 or newer.
3. **Android Platform Tools**: `adb` command installed and available on your system `PATH`.
4. **Device**: Fujitsu arrows ケータイ F-03L (or compatible Android Keitai) connected via USB with **USB Debugging** enabled.

---

## 🚀 Quick Start

### 1. Installation

Clone and install using `pip` or `pipx`:

```bash
git clone https://github.com/haphuthinh/keitai_mcp.git
cd keitai_mcp
pip install -e .
```

Verify your connected Keitai:
```bash
keitai-mcp devices
```

Output:
```
                   Connected Android Devices                   
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Serial   ┃ State  ┃ Model ┃ Product ┃ F-03L Detected?       ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ 96344868 │ device │ F_03L │ F03L    │ ✔ YES (Fujitsu F-03L) │
└──────────┴────────┴───────┴─────────┴───────────────────────┘
```

Inspect live device status:
```bash
keitai-mcp info
```

---

## ⚙️ MCP Client Configuration

### Claude Desktop

Add `keitai` to your `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "keitai": {
      "command": "keitai-mcp",
      "args": ["run"]
    }
  }
}
```

Or using direct virtualenv Python:

```json
{
  "mcpServers": {
    "keitai": {
      "command": "/path/to/keitai_mcp/.venv/bin/python",
      "args": ["-m", "keitai_mcp", "run"]
    }
  }
}
```

### Antigravity

In Antigravity, MCP servers are configured globally in `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "keitai": {
      "command": "/path/to/keitai_mcp/.venv/bin/python",
      "args": ["-m", "keitai_mcp", "run"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Cursor / Windsurf / Zed

Add to your workspace or user MCP settings (`mcpServers` object):

```json
{
  "mcpServers": {
    "keitai": {
      "command": "keitai-mcp",
      "args": ["run"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## 🛠️ Complete MCP Tool Reference

Keitai MCP exposes 28 purpose-built tools:

| Tool Name | Parameters | Description |
|---|---|---|
| `keitai_press_key` | `key`, `long_press`, `count`, `delay_ms` | Press a hardware key (`UP`, `DOWN`, `CENTER`, `BACK`, `F1`, `F2`, `0-9`, `STAR`, `POUND`, `FAV1-3`). |
| `keitai_press_sequence` | `keys`, `interval_ms` | Execute a sequence of keypresses (e.g. `["DOWN", "DOWN", "CENTER"]`). |
| `keitai_input_text` | `text` | Types alphanumeric text into the currently active text field. |
| `keitai_tap` | `x`, `y` | Tap coordinates (0–480, 0–854). |
| `keitai_swipe` | `x1`, `y1`, `x2`, `y2`, `duration_ms` | Perform swipe gesture. |
| `keitai_wake` | *none* | Wake the Keitai screen if it is asleep. |
| `keitai_sleep` | *none* | Put the Keitai screen to sleep. |
| `keitai_take_screenshot` | `save_path`, `return_image`, `max_width` | Capture live screen as MCP `ImageContent` and optional PNG file. |
| `keitai_inspect_ui` | `focused_only`, `clickable_only`, `max_depth`, `output_format` | Dump UI hierarchy tree with clear `[★FOCUSED]` markers. |
| `keitai_get_focused_element` | *none* | Returns the currently focused element's bounds, text, ID, and class. |
| `keitai_find_element` | `query`, `search_by` | Locate UI elements matching text, resource-id, or class. |
| `keitai_install_apk` | `apk_path`, `grant_permissions`, `reinstall` | Install APK with automated permissions and 32-bit validation. |
| `keitai_uninstall_app` | `package_name`, `keep_data` | Uninstall an application package. |
| `keitai_launch_app` | `package_name`, `activity` | Launch an application by package or specific activity name. |
| `keitai_stop_app` | `package_name` | Force-stop an application (`am force-stop`). |
| `keitai_clear_app` | `package_name` | Reset app data and cache (`pm clear`). |
| `keitai_list_installed_apps` | `third_party_only`, `filter_query` | List installed applications on the device. |
| `keitai_get_device_info` | *none* | Hardware specs, clamshell state, battery, RAM, storage, focused app. |
| `keitai_get_battery` | *none* | Battery percentage, temperature in °C, voltage, and health. |
| `keitai_get_clamshell_state` | *none* | Physical clamshell lid state (`OPEN` or `CLOSED`). |
| `keitai_get_network_info` | *none* | Wi-Fi connection IP address, MAC address, and status. |
| `keitai_exec_shell` | `command`, `timeout_seconds` | Safely execute arbitrary ADB shell command with structured output. |
| `keitai_read_logcat` | `package_name`, `tag`, `priority`, `lines` | Read filtered Android logcat entries. |
| `keitai_clear_logcat` | *none* | Clear the logcat buffer. |
| `keitai_get_recent_crashes` | `package_name` | Retrieve fatal exceptions, ANRs, and crash ring buffer logs. |
| `keitai_push_file` | `local_path`, `remote_path` | Transfer file from host to phone. |
| `keitai_pull_file` | `remote_path`, `local_path` | Transfer file from phone to host. |
| `keitai_list_files` | `remote_path` | List files and folders in a device directory. |

---

## 📖 MCP Resources & Prompts

### Resources
- `keitai://f03l/specs`: Complete technical hardware and software specifications of Fujitsu arrows Keitai F-03L.
- `keitai://dev/guidelines`: Comprehensive guide on developing Android applications for Japanese flip phones.
- `keitai://dev/keycodes`: Complete keycode catalog and mapping reference table.

### Prompts
- `plan_keitai_navigation(target_action)`: Guides an agent through inspecting the screen and executing D-Pad steps to reach an element.
- `diagnose_keitai_crash(package_name)`: Diagnoses application crashes on Android 8.1 / armeabi-v7a.

---

## 🎛️ CLI Reference

Keitai MCP also includes a command-line interface:

```bash
# View help
keitai-mcp --help

# Show device status panel
keitai-mcp info

# Capture a screenshot
keitai-mcp screenshot -o screen.png

# Send a key event
keitai-mcp key UP
keitai-mcp key CENTER
keitai-mcp key BACK --count 2

# Inspect current UI tree
keitai-mcp ui
keitai-mcp ui --clickable-only

# List installed 3rd party apps
keitai-mcp apps
keitai-mcp apps --all --query docomo
```

---

## 📱 Hardware Profile: Fujitsu F-03L

| Specification | Details |
|---|---|
| **Model** | Fujitsu arrows ケータイ F-03L (Docomo) |
| **OS** | Android 8.1.0 Oreo (API Level 27) |
| **SoC** | Qualcomm Snapdragon 210 (MSM8909) Quad-core ARM Cortex-A7 @ 1.1 GHz |
| **Architecture** | 32-bit ARM (`armeabi-v7a`) |
| **RAM** | 1 GB LPDDR3 (~913 MB visible to OS) |
| **Storage** | 8 GB ROM (~1.6 GB available user space) + microSDXC slot |
| **Main Display** | 3.4-inch TFT LCD, 480 × 854 pixels, 240 dpi, Non-touch |
| **Sub-Display** | 0.8-inch OLED (96 × 32 pixels) on outer lid |
| **Keypad** | 5-way D-Pad, Numeric 0–9, *, #, F1, F2, CLR, CALL, ENDCALL, Quick 1/2/3 |
| **Lid Switch** | `gpio_lid` sensor (`mLidState=1` for Open, `0` for Closed) |

For in-depth developer instructions, see [KEITAI_DEVELOPMENT_GUIDE.md](KEITAI_DEVELOPMENT_GUIDE.md).

---

## 🧪 Testing

Keitai MCP has full unit and integration test coverage:

```bash
# Run test suite
pytest -v
```

If your Fujitsu F-03L is plugged in, pytest automatically runs the live integration tests (`tests/test_live_device.py`). If no device is connected, live tests are cleanly skipped.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and guidelines.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
# keitai-mcp
