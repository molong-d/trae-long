from datetime import datetime
from typing import Dict, Any


class BaseFetcher:
    def __init__(self, config: dict):
        self.config = config
        self.category = config.get("category", "general")

    def fetch(self) -> list:
        raise NotImplementedError("Each fetcher must implement fetch()")

    def create_item(self, title: str, url: str, summary: str, published_at: str = None, raw: dict = None) -> dict:
        return {
            "source": self.source_name,
            "category": self.category,
            "title": title,
            "url": url,
            "published_at": published_at or datetime.utcnow().isoformat(),
            "fetched_at": datetime.utcnow().isoformat(),
            "summary": summary,
            "raw": raw or {}
        }
