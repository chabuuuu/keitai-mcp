"""UI Hierarchy Inspector and Focus Parser for Keitai screens."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Literal

from keitai_mcp.device.adb import ADBClient


@dataclass
class UINode:
    """Parsed UI Element from uiautomator dump."""
    index: int
    text: str
    resource_id: str
    class_name: str
    package: str
    content_desc: str
    checkable: bool
    checked: bool
    clickable: bool
    enabled: bool
    focusable: bool
    focused: bool
    scrollable: bool
    long_clickable: bool
    password: bool
    selected: bool
    bounds: tuple[int, int, int, int]  # (left, top, right, bottom)
    center: tuple[int, int]            # (center_x, center_y)
    children: list[UINode] = field(default_factory=list)

    @property
    def short_class(self) -> str:
        """Class name without package (e.g. TextView instead of android.widget.TextView)."""
        return self.class_name.split(".")[-1] if self.class_name else "Node"

    @property
    def display_label(self) -> str:
        """User-visible text or content description."""
        return self.text.strip() or self.content_desc.strip() or ""

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data: dict = {
            "class": self.short_class,
            "full_class": self.class_name,
            "resource_id": self.resource_id,
            "text": self.text,
            "content_desc": self.content_desc,
            "bounds": list(self.bounds),
            "center": list(self.center),
            "focused": self.focused,
            "focusable": self.focusable,
            "clickable": self.clickable,
            "selected": self.selected,
            "enabled": self.enabled,
        }
        if self.children:
            data["children"] = [c.to_dict() for c in self.children]
        return data


class UIInspector:
    """Inspector for capturing and parsing the Android Keitai UI hierarchy."""

    BOUNDS_PATTERN = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")

    def __init__(self, adb: ADBClient):
        self.adb = adb

    @classmethod
    def parse_bounds(cls, bounds_str: str) -> tuple[tuple[int, int, int, int], tuple[int, int]]:
        """Parse bounds string '[x1,y1][x2,y2]' into ((x1,y1,x2,y2), (cx,cy))."""
        m = cls.BOUNDS_PATTERN.match(bounds_str)
        if m:
            x1, y1, x2, y2 = map(int, m.groups())
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            return (x1, y1, x2, y2), (cx, cy)
        return (0, 0, 0, 0), (0, 0)

    @classmethod
    def _parse_element(cls, elem: ET.Element) -> UINode:
        attrib = elem.attrib
        bounds, center = cls.parse_bounds(attrib.get("bounds", ""))
        node = UINode(
            index=int(attrib.get("index", "0")),
            text=attrib.get("text", ""),
            resource_id=attrib.get("resource-id", ""),
            class_name=attrib.get("class", ""),
            package=attrib.get("package", ""),
            content_desc=attrib.get("content-desc", ""),
            checkable=attrib.get("checkable") == "true",
            checked=attrib.get("checked") == "true",
            clickable=attrib.get("clickable") == "true",
            enabled=attrib.get("enabled", "true") == "true",
            focusable=attrib.get("focusable") == "true",
            focused=attrib.get("focused") == "true",
            scrollable=attrib.get("scrollable") == "true",
            long_clickable=attrib.get("long-clickable") == "true",
            password=attrib.get("password") == "true",
            selected=attrib.get("selected") == "true",
            bounds=bounds,
            center=center,
        )
        for child in elem:
            if child.tag == "node":
                node.children.append(cls._parse_element(child))
        return node

    @classmethod
    def parse_xml(cls, xml_content: str) -> UINode | None:
        """Parse raw UIAutomator XML string into UINode tree."""
        if not xml_content or "<hierarchy" not in xml_content:
            return None
        try:
            root = ET.fromstring(xml_content.strip())
            for child in root:
                if child.tag == "node":
                    return cls._parse_element(child)
            return None
        except ET.ParseError:
            return None

    async def dump_xml(self) -> str:
        """Dump UIAutomator XML from connected Keitai."""
        tmp_path = "/data/local/tmp/keitai_uidump.xml"
        cmd = f"uiautomator dump {tmp_path} >/dev/null 2>&1 && cat {tmp_path}"
        try:
            xml_text = await self.adb.shell(cmd, timeout=8.0)
            return xml_text.strip()
        except Exception:
            # Fallback if dump failed directly
            await self.adb.shell(f"uiautomator dump {tmp_path}", timeout=8.0)
            xml_text = await self.adb.shell(f"cat {tmp_path}", timeout=5.0)
            return xml_text.strip()

    async def get_tree(self) -> UINode | None:
        """Fetch and parse current UI tree."""
        xml_content = await self.dump_xml()
        return self.parse_xml(xml_content)

    @classmethod
    def flatten_nodes(cls, root: UINode) -> list[UINode]:
        """Flatten tree into a list of all nodes."""
        result = [root]
        for child in root.children:
            result.extend(cls.flatten_nodes(child))
        return result

    @classmethod
    def find_focused(cls, root: UINode) -> UINode | None:
        """Find the element with focused=True."""
        for node in cls.flatten_nodes(root):
            if node.focused:
                return node
        return None

    @classmethod
    def find_interactive(cls, root: UINode) -> list[UINode]:
        """Find all focusable or clickable elements."""
        return [
            node for node in cls.flatten_nodes(root)
            if (node.focusable or node.clickable) and (node.bounds[2] > node.bounds[0] and node.bounds[3] > node.bounds[1])
        ]

    @classmethod
    def search_nodes(
        cls,
        root: UINode,
        query: str,
        search_by: Literal["text", "id", "class", "any"] = "any"
    ) -> list[UINode]:
        """Search nodes matching query."""
        q = query.lower()
        results: list[UINode] = []
        for node in cls.flatten_nodes(root):
            matched = False
            if search_by in ("text", "any") and (q in node.text.lower() or q in node.content_desc.lower()):
                matched = True
            elif search_by in ("id", "any") and q in node.resource_id.lower():
                matched = True
            elif search_by in ("class", "any") and q in node.class_name.lower():
                matched = True

            if matched:
                results.append(node)
        return results

    @classmethod
    def format_tree_text(
        cls,
        node: UINode,
        depth: int = 0,
        max_depth: int = 8,
        focused_only: bool = False,
        interactive_only: bool = False,
    ) -> str:
        """Format node hierarchy as a readable text summary for LLM agents."""
        lines: list[str] = []

        def _traverse(n: UINode, d: int):
            if d > max_depth:
                return

            is_focused = n.focused
            is_interactive = n.focusable or n.clickable
            has_label = bool(n.text or n.content_desc)

            include = True
            if focused_only and not is_focused:
                include = False
            elif interactive_only and not is_interactive and not has_label:
                include = False

            if include:
                indent = "  " * d
                flags = []
                if n.focused:
                    flags.append("★FOCUSED")
                if n.selected:
                    flags.append("SELECTED")
                if n.clickable:
                    flags.append("CLICKABLE")
                if n.focusable:
                    flags.append("FOCUSABLE")

                flag_str = f" [{', '.join(flags)}]" if flags else ""
                label_parts = []
                if n.text:
                    label_parts.append(f'text="{n.text}"')
                if n.content_desc:
                    label_parts.append(f'desc="{n.content_desc}"')
                if n.resource_id:
                    res_short = n.resource_id.split("/")[-1]
                    label_parts.append(f'id="{res_short}"')

                details = " " + " ".join(label_parts) if label_parts else ""
                lines.append(f"{indent}- {n.short_class}{flag_str}{details} bounds={list(n.bounds)} center={list(n.center)}")

            for child in n.children:
                _traverse(child, d + 1)

        _traverse(node, depth)
        return "\n".join(lines)

