import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from .base import BaseFetcher


class RssFetcher(BaseFetcher):
    source_name = "rss"

    def fetch(self) -> list:
        items = []
        feeds = self.config.get("feeds", [])

        for feed_config in feeds:
            feed_name = feed_config.get("name", "Unknown Feed")
            feed_url = feed_config.get("url", "")
            feed_category = feed_config.get("category", self.category)

            if not feed_url:
                continue

            feed_items = self._fetch_single_feed(feed_url, feed_name, feed_category)
            items.extend(feed_items)

        return items

    def _fetch_single_feed(self, url: str, feed_name: str, category: str) -> list:
        items = []

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "LocalIntelligenceHub/1.0",
                "Accept": "application/rss+xml, application/xml, text/xml"
            })

            with urllib.request.urlopen(req, timeout=30) as response:
                xml_data = response.read().decode("utf-8")

            root = ET.fromstring(xml_data)

            channel = root.find("channel")
            if channel is None:
                for item in root.findall(".//item"):
                    items.extend(self._parse_rss_item(item, feed_name, category))
            else:
                for item in channel.findall("item"):
                    items.extend(self._parse_rss_item(item, feed_name, category))

        except Exception as e:
            print(f"RSS fetch error for {feed_name} ({url}): {e}")

        return items

    def _parse_rss_item(self, item: ET.Element, feed_name: str, category: str) -> list:
        items = []

        title_elem = item.find("title")
        title = title_elem.text if title_elem is not None else "No Title"

        link_elem = item.find("link")
        link = link_elem.text if link_elem is not None else ""

        if not link:
            for enclosure in item.findall("link"):
                if enclosure.get("rel") == "alternate" or enclosure.get("type", "").startswith("text"):
                    link = enclosure.text or ""
                    break

        description_elem = item.find("description")
        summary = ""
        if description_elem is not None and description_elem.text:
            summary = description_elem.text
            summary = summary.replace("<![CDATA[", "").replace("]]>", "")
            summary = summary.strip()[:500]

        pub_date_elem = item.find("pubDate")
        published_at = None
        if pub_date_elem is not None and pub_date_elem.text:
            published_at = self._parse_date(pub_date_elem.text)

        if title:
            items.append(self.create_item(
                title=title,
                url=link,
                summary=summary,
                published_at=published_at,
                raw={"feed_name": feed_name}
            ))

        return items

    def _parse_date(self, date_str: str) -> str:
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(date_str)
                return dt.isoformat()
            except:
                try:
                    dt = datetime.strptime(date_str[:25].strip(), fmt.replace("%z", "").replace("%Z", ""))
                    return dt.isoformat()
                except:
                    continue

        return date_str[:19] if len(date_str) >= 19 else date_str
