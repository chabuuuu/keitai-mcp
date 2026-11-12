"""Unit tests for Keitai MCP Server tool, resource, and prompt registrations."""

import pytest
from keitai_mcp.server import create_server


def test_server_instance_and_metadata():
    server = create_server()
    assert server.name == "keitai-mcp"
    assert server.version == "0.1.0"


def test_tools_registered():
    server = create_server()
    tools = list(server._tool_manager._tools.keys())

    expected_tools = [
        "keitai_press_key",
        "keitai_press_sequence",
        "keitai_input_text",
        "keitai_tap",
        "keitai_swipe",
        "keitai_wake",
        "keitai_sleep",
        "keitai_take_screenshot",
        "keitai_inspect_ui",
        "keitai_get_focused_element",
        "keitai_find_element",
        "keitai_install_apk",
        "keitai_uninstall_app",
        "keitai_launch_app",
        "keitai_stop_app",
        "keitai_clear_app",
        "keitai_list_installed_apps",
        "keitai_get_device_info",
        "keitai_get_battery",
        "keitai_get_clamshell_state",
        "keitai_get_network_info",
        "keitai_exec_shell",
        "keitai_read_logcat",
        "keitai_clear_logcat",
        "keitai_get_recent_crashes",
        "keitai_push_file",
        "keitai_pull_file",
        "keitai_list_files",
    ]

    for tool_name in expected_tools:
        assert tool_name in tools, f"Tool '{tool_name}' missing from registered tools"


def test_resources_registered():
    server = create_server()
    resource_uris = list(server._resource_manager._resources.keys())

    expected_resources = [
        "keitai://f03l/specs",
        "keitai://dev/guidelines",
        "keitai://dev/keycodes",
    ]

    for uri in expected_resources:
        assert uri in resource_uris, f"Resource '{uri}' missing from registered resources"


def test_prompts_registered():
    server = create_server()
    prompts = list(server._prompt_manager._prompts.keys())

    assert "plan_keitai_navigation" in prompts
    assert "diagnose_keitai_crash" in prompts
