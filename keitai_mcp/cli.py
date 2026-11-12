"""Command-line interface for Keitai MCP."""

from __future__ import annotations

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from keitai_mcp import __version__
from keitai_mcp.device.adb import ADBClient
from keitai_mcp.server import create_server

app = typer.Typer(
    name="keitai-mcp",
    help="Model Context Protocol (MCP) server & developer CLI for Fujitsu F-03L and Android Keitai.",
    add_completion=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit."),
):
    if version:
        console.print(f"[bold cyan]keitai-mcp[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@app.command()
def run(
    transport: str = typer.Option("stdio", "--transport", "-t", help="Transport mode: 'stdio' or 'sse'."),
    port: int = typer.Option(8000, "--port", "-p", help="Port for SSE transport."),
    serial: Optional[str] = typer.Option(None, "--serial", "-s", help="Specific ADB device serial."),
    adb_path: str = typer.Option("adb", "--adb-path", help="Path to adb executable."),
):
    """Start the Keitai MCP server for AI agents (Claude Desktop, Cursor, Antigravity, etc.)."""
    server = create_server(serial=serial, adb_path=adb_path)
    if transport == "sse":
        console.print(f"[bold green]Starting Keitai MCP Server (SSE) on port {port}...[/bold green]")
        server.run(transport="sse", port=port)
    else:
        # stdio mode (default for MCP clients)
        server.run(transport="stdio")


@app.command()
def devices(
    adb_path: str = typer.Option("adb", "--adb-path", help="Path to adb executable."),
):
    """List connected ADB devices and detect Fujitsu F-03L."""
    async def _run():
        client = ADBClient(adb_path=adb_path)
        devs = await client.get_devices()
        if not devs:
            console.print("[bold red]No ADB devices detected.[/bold red] Ensure phone is plugged in with USB debugging enabled.")
            return

        table = Table(title="Connected Android Devices", border_style="cyan")
        table.add_column("Serial", style="bold yellow")
        table.add_column("State", style="green")
        table.add_column("Model")
        table.add_column("Product")
        table.add_column("F-03L Detected?", style="bold magenta")

        for d in devs:
            is_f03l = "✔ YES (Fujitsu F-03L)" if d.is_f03l else "No"
            table.add_row(d.serial, d.state, d.model or "Unknown", d.product or "Unknown", is_f03l)

        console.print(table)

    asyncio.run(_run())


@app.command()
def info(
    serial: Optional[str] = typer.Option(None, "--serial", "-s", help="Specific device serial."),
    adb_path: str = typer.Option("adb", "--adb-path", help="Path to adb executable."),
):
    """Display comprehensive hardware, battery, screen, and lid status of the Keitai."""
    async def _run():
        from keitai_mcp.tools import system
        client = ADBClient(serial=serial, adb_path=adb_path)
        with console.status("[cyan]Querying Keitai hardware profile..."):
            data = await system.get_device_info(client)

        hw = data["hardware"]
        sw = data["software"]
        disp = data["displays"]["main_display"]
        lid = data["clamshell"]
        bat = data["power_battery"]
        foc = data["current_focus"]
        net = data["network"]

        lid_color = "green" if lid["lid_state"] == "open" else "red"
        content = (
            f"[bold yellow]Model:[/bold yellow] {hw['manufacturer']} {hw['model']} ({hw['brand']})\n"
            f"[bold yellow]CPU ABI:[/bold yellow] {hw['cpu_abi']} | [bold yellow]Android:[/bold yellow] {sw['android_version']} (API {sw['sdk_int']})\n"
            f"[bold yellow]Display:[/bold yellow] {disp['resolution']} @ {disp['density_dpi']} dpi (Screen Power: [green]{disp['screen_power']}[/green])\n"
            f"[bold yellow]Clamshell Lid:[/bold yellow] [{lid_color}]{lid['lid_state'].upper()}[/{lid_color}]\n"
            f"[bold yellow]Battery:[/bold yellow] {bat['level_percent']}% | {bat['temperature_c']}°C | Voltage: {bat['voltage_mv']} mV\n"
            f"[bold yellow]Wi-Fi IP:[/bold yellow] {net.get('ip') or 'Not connected'}\n"
            f"[bold yellow]Current Focus:[/bold yellow] {foc['package']} / {foc['activity']}"
        )

        console.print(Panel(content, title="📱 Fujitsu arrows ケータイ F-03L Status", border_style="bright_blue"))

    asyncio.run(_run())


@app.command()
def screenshot(
    output: str = typer.Option("f03l_screen.png", "--output", "-o", help="File path to save screenshot."),
    serial: Optional[str] = typer.Option(None, "--serial", "-s", help="Device serial."),
    adb_path: str = typer.Option("adb", "--adb-path", help="Path to adb executable."),
):
    """Capture a screenshot and save it locally."""
    async def _run():
        from keitai_mcp.tools import screen
        client = ADBClient(serial=serial, adb_path=adb_path)
        with console.status(f"[cyan]Capturing screen to {output}..."):
            res = await screen.take_screenshot(client, save_path=output, return_image=False)
        console.print(f"[bold green]✔ Screenshot saved successfully to:[/bold green] [yellow]{output}[/yellow]")

    asyncio.run(_run())


@app.command()
def key(
    key_name: str = typer.Argument(..., help="Key name (e.g. UP, DOWN, CENTER, BACK, F1, 1, 2)."),
    long_press: bool = typer.Option(False, "--long-press", "-l", help="Perform long press."),
    count: int = typer.Option(1, "--count", "-c", help="Number of times to press."),
    serial: Optional[str] = typer.Option(None, "--serial", "-s", help="Device serial."),
    adb_path: str = typer.Option("adb", "--adb-path", help="Path to adb executable."),
):
    """Send physical key press event to the Keitai."""
    async def _run():
        from keitai_mcp.tools import keypad
        client = ADBClient(serial=serial, adb_path=adb_path)
        res = await keypad.press_key(client, key=key_name, long_press=long_press, count=count)
        console.print(f"[bold green]✔ Key sent:[/bold green] {res['key']} (Keycode {res['keycode']}) x{res['count']}")

    asyncio.run(_run())


@app.command()
def ui(
    focused_only: bool = typer.Option(False, "--focused-only", "-f", help="Show only focused element."),
    clickable_only: bool = typer.Option(False, "--clickable-only", "-c", help="Show only interactive elements."),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output raw JSON hierarchy."),
    serial: Optional[str] = typer.Option(None, "--serial", "-s", help="Device serial."),
    adb_path: str = typer.Option("adb", "--adb-path", help="Path to adb executable."),
):
    """Inspect the current UI hierarchy and focus layout."""
    async def _run():
        from keitai_mcp.tools import ui as ui_tools
        client = ADBClient(serial=serial, adb_path=adb_path)
        fmt = "json" if json_output else "tree"
        with console.status("[cyan]Dumping UI hierarchy..."):
            out = await ui_tools.inspect_ui(
                client,
                focused_only=focused_only,
                clickable_only=clickable_only,
                output_format=fmt,
            )
        console.print(out)

    asyncio.run(_run())


@app.command()
def apps(
    all_packages: bool = typer.Option(False, "--all", "-a", help="List all packages including system."),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Filter by substring."),
    serial: Optional[str] = typer.Option(None, "--serial", "-s", help="Device serial."),
    adb_path: str = typer.Option("adb", "--adb-path", help="Path to adb executable."),
):
    """List installed applications on the Keitai."""
    async def _run():
        from keitai_mcp.tools import apps as apps_tools
        client = ADBClient(serial=serial, adb_path=adb_path)
        with console.status("[cyan]Fetching installed packages..."):
            pkgs = await apps_tools.list_installed_apps(
                client,
                third_party_only=not all_packages,
                filter_query=query,
            )

        title = f"Installed {'All' if all_packages else 'Third-Party'} Apps ({len(pkgs)})"
        table = Table(title=title, border_style="cyan")
        table.add_column("Package Name", style="bold green")

        for p in pkgs:
            table.add_row(p)

        console.print(table)

    asyncio.run(_run())


def main():
    """Main entrypoint for CLI execution."""
    app()


if __name__ == "__main__":
    main()
