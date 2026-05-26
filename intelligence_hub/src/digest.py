from datetime import datetime
from typing import Dict, List
from .db import Database
from .scoring import ImportanceScorer


class DigestGenerator:
    def __init__(self, db: Database):
        self.db = db

    def generate(self) -> str:
        items = self.db.get_high_score_items(hours=24, min_score=20)

        lines = []
        lines.append("# Local Intelligence Hub - Daily Digest\n")
        lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        lines.append(f"**High Score Items (24h):** {len(items)}\n")
        lines.append("\n---\n\n")

        if not items:
            lines.append("*No high-scoring items in the last 24 hours.*\n")
            return "".join(lines)

        watchlist_items = [item for item in items if ImportanceScorer.check_watchlist_match(item)]
        high_priority_items = [item for item in items if item["importance_score"] >= 50]

        if watchlist_items:
            lines.append("## Watchlist Matched\n\n")
            for item in watchlist_items[:15]:
                score = item["importance_score"]
                score_marker = "**[HIGH]** " if score >= 50 else ""
                lines.append(f"- {score_marker}{item['title']}\n")
                lines.append(f"  - Source: {item['source']} | Score: {score} | Time: {item.get('published_at', item['created_at'])}\n")
                if item.get("url"):
                    lines.append(f"  - Link: {item['url']}\n")
                if item.get("summary"):
                    summary_preview = item["summary"][:200] + "..." if len(item["summary"]) > 200 else item["summary"]
                    lines.append(f"  - Summary: {summary_preview}\n")
                lines.append("\n")
            lines.append("\n")

        if high_priority_items:
            lines.append("## High Priority (Score >= 50)\n\n")
            for item in high_priority_items[:20]:
                lines.append(f"- {item['title']}\n")
                lines.append(f"  - Source: {item['source']} | Score: {item['importance_score']} | Time: {item.get('published_at', item['created_at'])}\n")
                if item.get("url"):
                    lines.append(f"  - Link: {item['url']}\n")
                lines.append("\n")
            lines.append("\n")

        by_category: Dict[str, List[Dict]] = {}
        for item in items:
            category = item.get("category", "unknown")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)

        for category, category_items in sorted(by_category.items()):
            lines.append(f"## {category.upper()} ({len(category_items)} items)\n\n")
            for item in category_items:
                score = item["importance_score"]
                score_marker = "**[HIGH]** " if score >= 50 else ""
                watchlist_marker = "**[WATCH]** " if ImportanceScorer.check_watchlist_match(item) else ""
                lines.append(f"- {score_marker}{watchlist_marker}{item['title']}\n")
                lines.append(f"  - Source: {item['source']} | Score: {score} | Time: {item.get('published_at', item['created_at'])}\n")
                if item.get("url"):
                    lines.append(f"  - Link: {item['url']}\n")
                if item.get("summary"):
                    summary_preview = item["summary"][:200] + "..." if len(item["summary"]) > 200 else item["summary"]
                    lines.append(f"  - Summary: {summary_preview}\n")
                lines.append("\n")
            lines.append("\n")

        lines.append("---\n\n")
        lines.append("*This digest is auto-generated. Information should be verified before use.*\n")
        lines.append("*This is a news aggregation tool, not financial or investment advice.*\n")

        return "".join(lines)

    def generate_summary(self) -> str:
        stats = self.db.get_stats()
        items = self.db.get_high_score_items(hours=24, min_score=30)

        summary = f"Total items: {stats['total_items']}\n"
        summary += f"High priority items (24h): {len(items)}\n"
        summary += f"Categories: {', '.join(stats['categories'].keys())}\n"

        return summary
