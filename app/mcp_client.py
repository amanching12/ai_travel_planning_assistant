import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

BASE_DIR = Path(__file__).resolve().parents[1]


def _client() -> MultiServerMCPClient:
    server_dir = BASE_DIR / "mcp_servers"
    return MultiServerMCPClient(
        {
            "weather": {
                "command": sys.executable,
                "args": [str(server_dir / "weather_server.py")],
                "transport": "stdio",
            },
            "currency": {
                "command": sys.executable,
                "args": [str(server_dir / "currency_server.py")],
                "transport": "stdio",
            },
        }
    )


async def _tool_by_name(name_fragment: str):
    tools = await _client().get_tools()
    for tool in tools:
        if name_fragment in tool.name:
            return tool
    raise RuntimeError(f"MCP tool not found: {name_fragment}")


async def get_weather(city: str = "Singapore", days: int = 3) -> dict:
    tool = await _tool_by_name("get_weather_forecast")
    return await tool.ainvoke({"city": city, "days": days})


async def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    tool = await _tool_by_name("convert_currency")
    return await tool.ainvoke(
        {"amount": amount, "from_currency": from_currency, "to_currency": to_currency}
    )
