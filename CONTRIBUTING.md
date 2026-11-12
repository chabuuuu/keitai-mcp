# Contributing to Keitai MCP

Thank you for your interest in contributing to **Keitai MCP**! We welcome bug reports, documentation enhancements, additional key layout mappings, and feature improvements.

---

## 🛠️ Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/haphuthinh/keitai_mcp.git
   cd keitai_mcp
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies in editable mode**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify installation**:
   ```bash
   keitai-mcp --help
   pytest -v
   ```

---

## 🧪 Testing Guidelines

- **Unit Tests**: All unit tests in `tests/test_f03l_constants.py`, `tests/test_ui_inspector.py`, `tests/test_adb_unit.py`, and `tests/test_server_registration.py` must pass without requiring a physical device.
- **Integration Tests**: Tests in `tests/test_live_device.py` run against real connected Keitai hardware. If no device is connected, pytest skips them automatically.
- Always run `pytest` before submitting a PR:
  ```bash
  pytest
  ```

---

## 📝 Coding Standards

- **Python Version**: Python 3.10+ compatibility.
- **Type Hints**: All functions, methods, and classes must include clear type annotations (`typing`, `__future__.annotations`).
- **Asynchronous Execution**: ADB communications and tool handlers should remain non-blocking using `asyncio`.
- **Formatting**: We follow PEP 8 standards with descriptive docstrings.

---

## 📱 Hardware Support Expansion

While Keitai MCP was forged with first-class support for the **Fujitsu arrows ケータイ F-03L**, contributions adding device profiles for other Japanese feature phones (e.g., Sharp Aquos Keitai SH-01J/SH-02L, Kyocera Digno Keitai KYF31/KYF37/KYF39) are warmly welcomed!

---

## 📬 Submitting Changes

1. Fork the repository and create a descriptive branch:
   ```bash
   git checkout -b feature/sharp-aquos-keymap
   ```
2. Commit your changes with clear messages.
3. Push to your branch and open a Pull Request explaining the problem, solution, and test results.

