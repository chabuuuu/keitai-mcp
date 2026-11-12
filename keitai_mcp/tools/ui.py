"""UI hierarchy and focus inspection tools for Keitai."""

from __future__ import annotations

import json
import logging
from typing import Any, Literal

from keitai_mcp.device.adb import ADBClient
from keitai_mcp.device.inspector import UIInspector

logger = logging.getLogger("keitai_mcp.tools.ui")


async def inspect_ui(
    adb: ADBClient,
    focused_only: bool = False,
    clickable_only: bool = False,
    max_depth: int = 8,
    output_format: Literal["tree", "json"] = "tree",
) -> str:
    """Dump and parse the current UI hierarchy on the Keitai screen.

    Provides a clean, compact view of UI elements, clearly highlighting which element
    currently holds D-pad focus (★FOCUSED), clickable items, and coordinates.

    Args:
        adb: ADB client instance.
        focused_only: Only show elements that are currently focused.
        clickable_only: Filter to interactive (clickable/focusable) elements only.
        max_depth: Maximum tree depth to display (default 8).
        output_format: 'tree' for indented human/agent text, or 'json' for raw structured dictionary.

    Returns:
        Formatted UI hierarchy representation.
    """
    inspector = UIInspector(adb)
    root = await inspector.get_tree()

    if not root:
        return "No UI hierarchy could be retrieved. Is the Keitai screen on and unlocked?"

    if output_format == "json":
        return json.dumps(root.to_dict(), indent=2, ensure_ascii=False)

    return inspector.format_tree_text(
        root,
        max_depth=max_depth,
        focused_only=focused_only,
        interactive_only=clickable_only,
    )


async def get_focused_element(adb: ADBClient) -> dict[str, Any]:
    """Retrieve details of the element currently focused by the D-pad cursor.

    Essential for testing focus navigation in Android Keitai applications.

    Args:
        adb: ADB client instance.

    Returns:
        Dictionary with focused element details, or status indicating nothing is focused.
    """
    inspector = UIInspector(adb)
    root = await inspector.get_tree()

    if not root:
        return {"focused": False, "error": "Unable to dump UI hierarchy"}

    node = inspector.find_focused(root)
    if not node:
        return {
            "focused": False,
            "message": "No UI element currently has focus. You may need to press D-pad UP/DOWN/LEFT/RIGHT to move focus into the view."
        }

    return {
        "focused": True,
        "class": node.short_class,
        "full_class": node.class_name,
        "resource_id": node.resource_id,
        "text": node.text,
        "content_desc": node.content_desc,
        "bounds": list(node.bounds),
        "center": list(node.center),
        "clickable": node.clickable,
        "focusable": node.focusable,
        "package": node.package,
    }


async def find_element(
    adb: ADBClient,
    query: str,
    search_by: Literal["text", "id", "class", "any"] = "any",
) -> list[dict[str, Any]]:
    """Search for UI elements matching text, resource ID, or class name.

    Args:
        adb: ADB client instance.
        query: Search string (e.g. 'Settings', 'btn_login', 'TextView').
        search_by: Attribute to match ('text', 'id', 'class', or 'any').

    Returns:
        List of matching elements with their coordinates and status.
    """
    inspector = UIInspector(adb)
    root = await inspector.get_tree()

    if not root:
        return []

    matches = inspector.search_nodes(root, query=query, search_by=search_by)
    return [
        {
            "class": m.short_class,
            "resource_id": m.resource_id,
            "text": m.text,
            "content_desc": m.content_desc,
            "bounds": list(m.bounds),
            "center": list(m.center),
            "focused": m.focused,
            "focusable": m.focusable,
            "clickable": m.clickable,
        }
        for m in matches
    ]

