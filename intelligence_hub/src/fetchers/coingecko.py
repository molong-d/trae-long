import json
import urllib.request
import urllib.parse
import logging
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
        coins = self.config.get("coins", ["bitcoin", "ethereum", "solana"])
        vs_currency = self.config.get("vs_currency", "usd")

        logger = logging.getLogger(__name__)

        coin_ids = [self.COIN_ID_MAP.get(c.lower(), c.lower()) for c in coins]
        ids_param = ",".join(coin_ids)

        try:
            params = urllib.parse.urlencode({
                "ids": ids_param,
                "vs_currencies": vs_currency,
                "include_24hr_change": "true",
                "include_last_updated_at": "true"
            })

            url = f"https://api.coingecko.com/api/v3/simple/price?{params}"
            logger.info(f"CoinGecko request URL: {url}")

            req = urllib.request.Request(url, headers={
                "User-Agent": "LocalIntelligenceHub/1.0",
                "Accept": "application/json"
            })

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            if not data:
                logger.warning(f"CoinGecko returned empty response for coins: {coins}")
                return items

            logger.info(f"CoinGecko returned data for {len(data)} coins")

            for coin_name, coin_data in data.items():
                price = coin_data.get(vs_currency, 0)
                change_key = f"{vs_currency}_24h_change"
                change_24h = coin_data.get(change_key, 0)
                last_updated = coin_data.get("last_updated_at", 0)

                from datetime import datetime
                updated_time = datetime.fromtimestamp(last_updated).isoformat() if last_updated else None

                title = f"{coin_name.capitalize()} Price Update"
                coin_url = f"https://www.coingecko.com/en/coins/{coin_name}"

                summary = f"Price: ${price:,.2f} USD | 24h Change: {change_24h:+.2f}%"

                items.append(self.create_item(
                    title=title,
                    url=coin_url,
                    summary=summary,
                    published_at=updated_time,
                    raw={
                        "coin_id": coin_name,
                        "price_usd": price,
                        "change_24h": change_24h,
                        "last_updated": last_updated
                    }
                ))

        except urllib.error.HTTPError as e:
            logger.error(f"CoinGecko HTTP error: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            logger.error(f"CoinGecko URL error: {e.reason}")
        except Exception as e:
            logger.error(f"CoinGecko fetch error: {e}")

        if not items:
            logger.warning(f"CoinGecko returned 0 items for coins: {coins}")

        return items
