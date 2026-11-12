"""Keymap and Keycode Reference Resource for Fujitsu F-03L."""

from keitai_mcp.device.f03l import KEY_CATALOG, KEY_MAP

def generate_keymap_markdown() -> str:
    """Generate Markdown reference table for all Fujitsu F-03L keys."""
    lines = [
        "# Fujitsu arrows Keitai F-03L - Hardware Keycode Reference",
        "",
        "This reference documents physical buttons, keycodes, and aliases accepted by Keitai MCP.",
        "",
        "| Category | Key Name | Keycode | Label / Japanese | Description |",
        "|---|---|---|---|---|",
    ]

    for item in KEY_CATALOG:
        lines.append(
            f"| `{item.category}` | `{item.canonical_name}` | `{item.keycode}` | {item.physical_label} | {item.description} |"
        )

    lines.extend([
        "",
        "## Additional Supported Aliases",
        "",
        "- `OK`, `SELECT` -> Maps to `CENTER` (`23` - `KEYCODE_DPAD_CENTER`)",
        "- `CLR`, `CLEAR` -> Maps to `BACK` (`4` - `KEYCODE_BACK`)",
        "- `SUBMENU`, `MAIL`, `SOFTKEY_LEFT` -> Maps to `F1` (`131` - `KEYCODE_F1`)",
        "- `BROWSER`, `SOFTKEY_RIGHT` -> Maps to `F2` (`132` - `KEYCODE_F2`)",
        "- `TALK`, `DIAL` -> Maps to `CALL` (`5` - `KEYCODE_CALL`)",
        "- `END`, `POWER` -> Maps to `ENDCALL` (`6` - `KEYCODE_ENDCALL`)",
        "- `QUICK_1`, `BUTTON_1`, `FAVORITE_1` -> Maps to `FAV1` (`188` - `KEYCODE_BUTTON_1`)",
        "- `QUICK_2`, `BUTTON_2`, `FAVORITE_2` -> Maps to `FAV2` (`189` - `KEYCODE_BUTTON_2`)",
        "- `QUICK_3`, `BUTTON_3`, `FAVORITE_3` -> Maps to `FAV3` (`190` - `KEYCODE_BUTTON_3`)",
        "",
        "## ADB Shell Equivalent",
        "```bash",
        "# Example: Press D-Pad Center",
        "adb shell input keyevent 23",
        "",
        "# Example: Long-press Manner mode (# key)",
        "adb shell input keyevent --longpress 18",
        "```",
    ])

    return "\n".join(lines)


KEYMAP_MD_TEXT = generate_keymap_markdown()
