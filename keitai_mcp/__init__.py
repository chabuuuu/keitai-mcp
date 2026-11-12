"""Keitai MCP - Model Context Protocol Server for Fujitsu F-03L & Android Keitai Flip Phones."""

__version__ = "0.1.0"
__author__ = "Ha Phu Thinh"
__license__ = "MIT"

from keitai_mcp.device.adb import ADBClient
from keitai_mcp.server import create_server

__all__ = ["ADBClient", "create_server", "__version__"]

