import json
import urllib.request
import urllib.parse
from .base import BaseFetcher


class CoingeckoFetcher(BaseFetcher):
    source_name = "coingecko"

    COIN_ID_MAP = {
        "bitcoin": "bitcoin",
        "ethereum": "ethereum",
        "solana": "solana",
        "cardano": "cardano",
        "ripple": "ripple",
        "dogecoin": "dogecoin",
        "polkadot": "polkadot",
        "avalanche": "avalanche-2",
        "chainlink": "chainlink",
        "polygon": "matic-network"
    }

    def fetch(self) -> list:
        items = []
        coins = self.config.get("coins", ["bitcoin", "ethereum"])

        coin_ids = [self.COIN_ID_MAP.get(c.lower(), c.lower()) for c in coins]
        ids_param = ",".join(coin_ids)

        try:
            params = urllib.parse.urlencode({
                "ids": ids_param,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_last_updated_at": "true"
            })

            url = f"https://api.coingecko.com/api/v3/simple/price?{params}"

            req = urllib.request.Request(url, headers={
                "User-Agent": "LocalIntelligenceHub/1.0",
                "Accept": "application/json"
            })

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            for coin_name, coin_data in data.items():
                price = coin_data.get("usd", 0)
                change_24h = coin_data.get("usd_24h_change", 0)
                last_updated = coin_data.get("last_updated_at", 0)

                from datetime import datetime
                updated_time = datetime.fromtimestamp(last_updated).isoformat() if last_updated else None

                title = f"{coin_name.capitalize()} Price Update"
                url = f"https://www.coingecko.com/en/coins/{coin_name}"

                summary = f"Price: ${price:,.2f} USD | 24h Change: {change_24h:+.2f}%"

                items.append(self.create_item(
                    title=title,
                    url=url,
                    summary=summary,
                    published_at=updated_time,
                    raw={
                        "coin_id": coin_name,
                        "price_usd": price,
                        "change_24h": change_24h,
                        "last_updated": last_updated
                    }
                ))

        except Exception as e:
            print(f"CoinGecko fetch error: {e}")

        return items
