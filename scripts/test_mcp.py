import asyncio

from app.mcp_client import convert_currency, get_weather


async def main():
    print(await get_weather("Singapore", 3))
    print(await convert_currency(60000, "INR", "SGD"))


if __name__ == "__main__":
    asyncio.run(main())
