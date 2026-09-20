import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Currency Server")


@mcp.tool(description="Convert an amount from one currency to another using latest exchange rates.")
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    from_code = from_currency.upper().strip()
    to_code = to_currency.upper().strip()

    if amount <= 0:
        return {"error": "Amount must be greater than zero."}

    if from_code == to_code:
        return {
            "amount": amount,
            "from_currency": from_code,
            "to_currency": to_code,
            "rate": 1,
            "converted_amount": round(amount, 2),
            "date": None,
            "source": "No conversion needed because both currencies are the same.",
        }

    url = f"https://api.frankfurter.dev/v2/rate/{from_code.lower()}/{to_code.lower()}"

    try:
        response = httpx.get(
            url,
            timeout=15,
            follow_redirects=True,
            headers={"accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

        rate = data.get("rate")
        if rate is None:
            return {
                "error": "Currency rate was not available from the exchange-rate service.",
                "details": data,
            }

        converted_amount = round(amount * float(rate), 2)

        return {
            "amount": amount,
            "from_currency": from_code,
            "to_currency": to_code,
            "rate": rate,
            "converted_amount": converted_amount,
            "date": data.get("date"),
            "source": "Frankfurter exchange-rate API",
        }

    except httpx.HTTPStatusError as exc:
        return {
            "error": "Currency conversion service returned an HTTP error.",
            "status_code": exc.response.status_code,
            "details": exc.response.text[:300],
        }
    except Exception as exc:
        return {
            "error": "Currency conversion failed.",
            "details": str(exc),
        }


if __name__ == "__main__":
    mcp.run()