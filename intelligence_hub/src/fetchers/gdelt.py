import json
import urllib.request
import urllib.parse
from datetime import datetime
from .base import BaseFetcher


class GdeltFetcher(BaseFetcher):
    source_name = "gdelt"

    def fetch(self) -> list:
        items = []
        keywords = self.config.get("keywords", [])
        keywords_str = " ".join(keywords) if keywords else "world news"

        try:
            query_params = urllib.parse.urlencode({
                "format": "json",
                "mode": "artlist",
                "query": keywords_str,
                "maxrecords": self.config.get("limit", 20)
            })

            url = f"https://api.gdeltproject.org/api/v2/doc/doc?{query_params}"

            req = urllib.request.Request(url, headers={
                "User-Agent": "LocalIntelligenceHub/1.0"
            })

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            articles = data.get("articles", [])

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

        except Exception as e:
            print(f"GDELT fetch error: {e}")

        return items
