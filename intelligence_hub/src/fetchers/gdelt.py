import json
import urllib.request
import urllib.parse
import logging
from datetime import datetime
from .base import BaseFetcher


class GdeltFetcher(BaseFetcher):
    source_name = "gdelt"

    def fetch(self) -> list:
        items = []
        keywords = self.config.get("keywords", [])
        keywords_str = " ".join(keywords) if keywords else "world news"
        limit = self.config.get("limit", 20)
        timespan = self.config.get("timespan", "1d")

        logger = logging.getLogger(__name__)

        try:
            query_params = urllib.parse.urlencode({
                "format": "json",
                "mode": "artlist",
                "query": keywords_str,
                "maxrecords": limit,
                "timespan": timespan
            })

            url = f"https://api.gdeltproject.org/api/v2/doc/doc?{query_params}"
            logger.info(f"GDELT request URL: {url}")

            req = urllib.request.Request(url, headers={
                "User-Agent": "LocalIntelligenceHub/1.0"
            })

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            articles = data.get("articles", [])

            if not articles:
                logger.warning(f"GDELT returned 0 items. URL: {url}, Status: {response.status if 'response' in dir() else 'unknown'}")
            else:
                logger.info(f"GDELT returned {len(articles)} items")

            for article in articles:
                title = article.get("title", "")
                article_url = article.get("url", "")
                summary = article.get("socialimage", "") + " " + article.get("domain", "")
                published = article.get("seendate", "")

                if title and article_url:
                    items.append(self.create_item(
                        title=title,
                        url=article_url,
                        summary=summary[:500],
                        published_at=published[:14] if published else None,
                        raw=article
                    ))

        except urllib.error.HTTPError as e:
            logger.error(f"GDELT HTTP error: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            logger.error(f"GDELT URL error: {e.reason}")
        except Exception as e:
            logger.error(f"GDELT fetch error: {e}")

        if not items:
            logger.warning(f"GDELT returned 0 items for keywords: {keywords_str}")

        return items
