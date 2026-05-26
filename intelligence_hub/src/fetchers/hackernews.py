import json
import urllib.request
from datetime import datetime
from .base import BaseFetcher


class HackernewsFetcher(BaseFetcher):
    source_name = "hackernews"

    def fetch(self) -> list:
        items = []
        limit = self.config.get("limit", 30)

        try:
            top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            req = urllib.request.Request(top_stories_url, headers={"User-Agent": "LocalIntelligenceHub/1.0"})

            with urllib.request.urlopen(req, timeout=30) as response:
                story_ids = json.loads(response.read().decode("utf-8"))

            story_ids = story_ids[:limit]

            for story_id in story_ids:
                try:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    item_req = urllib.request.Request(item_url, headers={"User-Agent": "LocalIntelligenceHub/1.0"})

                    with urllib.request.urlopen(item_req, timeout=10) as item_response:
                        story = json.loads(item_response.read().decode("utf-8"))

                    if story and story.get("title"):
                        title = story.get("title", "")
                        url = story.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                        summary = f"Score: {story.get('score', 0)}, Comments: {story.get('descendants', 0)}"
                        published = datetime.fromtimestamp(story.get("time", 0)).isoformat() if story.get("time") else None

                        items.append(self.create_item(
                            title=title,
                            url=url,
                            summary=summary,
                            published_at=published,
                            raw=story
                        ))

                except Exception as e:
                    print(f"Failed to fetch story {story_id}: {e}")
                    continue

        except Exception as e:
            print(f"HackerNews fetch error: {e}")

        return items
