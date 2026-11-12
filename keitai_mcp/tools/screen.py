"""Screen capture and vision tools for Keitai devices."""

from __future__ import annotations

import base64
import io
import json
import logging
import os
from typing import Any

from PIL import Image
import mcp.types as types

from keitai_mcp.device.adb import ADBClient

logger = logging.getLogger("keitai_mcp.tools.screen")


async def take_screenshot(
    adb: ADBClient,
    save_path: str | None = None,
    return_image: bool = True,
    max_width: int | None = None,
) -> list[types.ImageContent | types.TextContent]:
    """Capture a screenshot of the Keitai screen.

    Returns the image for AI vision models and saves it locally if requested.

    Args:
        adb: ADB client instance.
        save_path: Optional path to save the PNG file locally (e.g. 'f03l_screen.png').
        return_image: Whether to include the base64 ImageContent in the MCP response.
        max_width: Optional maximum width to downscale image for bandwidth/token efficiency.

    Returns:
        List containing ImageContent and TextContent with metadata.
    """
    raw_bytes = await adb.screencap()
    img = Image.open(io.BytesIO(raw_bytes))

    orig_width, orig_height = img.size

    # Optional resize
    if max_width and orig_width > max_width:
        ratio = max_width / float(orig_width)
        new_height = int(float(orig_height) * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    out_buffer = io.BytesIO()
    # Save as PNG
    img.save(out_buffer, format="PNG", optimize=True)
    png_bytes = out_buffer.getvalue()
    b64_str = base64.b64encode(png_bytes).decode("ascii")

    saved_to = None
    if save_path:
        abs_path = os.path.abspath(save_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True) if os.path.dirname(abs_path) else None
        with open(abs_path, "wb") as f:
            f.write(png_bytes)
        saved_to = abs_path

    # Get current focused app metadata
    pkg, activity = await adb.get_current_focus()

    metadata: dict[str, Any] = {
        "success": True,
        "width": img.width,
        "height": img.height,
        "original_width": orig_width,
        "original_height": orig_height,
        "focused_package": pkg,
        "focused_activity": activity,
        "saved_path": saved_to,
        "bytes_size": len(png_bytes),
    }

    contents: list[types.ImageContent | types.TextContent] = [
        types.TextContent(
            type="text",
            text=f"Keitai Screenshot captured: {img.width}x{img.height} (Package: {pkg or 'Unknown'})\n"
                 f"Details: {json.dumps(metadata, indent=2, ensure_ascii=False)}"
        )
    ]

    if return_image:
        contents.append(
            types.ImageContent(
                type="image",
                data=b64_str,
                mimeType="image/png",
            )
        )

    return contents

