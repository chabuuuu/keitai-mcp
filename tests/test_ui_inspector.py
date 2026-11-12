"""Unit tests for UI hierarchy parsing and element extraction."""

import pytest
from keitai_mcp.device.inspector import UIInspector, UINode

SAMPLE_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.fujitsu.test" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[0,0][480,854]">
    <node index="0" text="Keitai Settings" resource-id="com.fujitsu.test:id/title" class="android.widget.TextView" package="com.fujitsu.test" content-desc="Header Title" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[10,20][470,80]" />
    <node index="1" text="Wi-Fi" resource-id="com.fujitsu.test:id/wifi_item" class="android.widget.Button" package="com.fujitsu.test" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="true" scrollable="false" long-clickable="false" password="false" selected="true" bounds="[10,90][470,160]" />
    <node index="2" text="Bluetooth" resource-id="com.fujitsu.test:id/bt_item" class="android.widget.Button" package="com.fujitsu.test" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[10,170][470,240]" />
  </node>
</hierarchy>
"""


def test_parse_bounds():
    bounds, center = UIInspector.parse_bounds("[10,20][470,80]")
    assert bounds == (10, 20, 470, 80)
    assert center == (240, 50)


def test_parse_xml_tree():
    root = UIInspector.parse_xml(SAMPLE_XML)
    assert root is not None
    assert root.class_name == "android.widget.FrameLayout"
    assert root.short_class == "FrameLayout"
    assert len(root.children) == 3


def test_find_focused_node():
    root = UIInspector.parse_xml(SAMPLE_XML)
    assert root is not None
    focused = UIInspector.find_focused(root)
    assert focused is not None
    assert focused.text == "Wi-Fi"
    assert focused.resource_id == "com.fujitsu.test:id/wifi_item"
    assert focused.focused is True
    assert focused.short_class == "Button"


def test_find_interactive_nodes():
    root = UIInspector.parse_xml(SAMPLE_XML)
    assert root is not None
    interactive = UIInspector.find_interactive(root)
    assert len(interactive) == 2
    names = [n.text for n in interactive]
    assert "Wi-Fi" in names
    assert "Bluetooth" in names


def test_search_nodes():
    root = UIInspector.parse_xml(SAMPLE_XML)
    assert root is not None

    by_text = UIInspector.search_nodes(root, query="Bluetooth", search_by="text")
    assert len(by_text) == 1
    assert by_text[0].resource_id == "com.fujitsu.test:id/bt_item"

    by_id = UIInspector.search_nodes(root, query="title", search_by="id")
    assert len(by_id) == 1
    assert by_id[0].text == "Keitai Settings"


def test_format_tree_text():
    root = UIInspector.parse_xml(SAMPLE_XML)
    assert root is not None
    formatted = UIInspector.format_tree_text(root, max_depth=3)
    assert "Button [★FOCUSED, SELECTED, CLICKABLE, FOCUSABLE] text=\"Wi-Fi\"" in formatted
    assert "TextView text=\"Keitai Settings\"" in formatted
