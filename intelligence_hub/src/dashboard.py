from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import html
from pathlib import Path
from typing import Dict, Any
from .db import Database


class DashboardHandler(BaseHTTPRequestHandler):
    db: Database = None

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_html()
        elif self.path == "/api/items":
            self.serve_items_api()
        elif self.path == "/api/status":
            self.serve_status_api()
        else:
            self.send_error(404)

    def serve_html(self):
        items = self.get_items_from_db()
        stats = self.get_stats_from_db()

        html_content = self.generate_html(items, stats)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def serve_items_api(self):
        items = self.get_items_from_db()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(items).encode("utf-8"))

    def serve_status_api(self):
        stats = self.get_stats_from_db()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode("utf-8"))

    def get_items_from_db(self, limit: int = 100):
        if self.db:
            return self.db.get_items(limit=limit)
        return []

    def get_stats_from_db(self):
        if self.db:
            return self.db.get_stats()
        return {"total_items": 0, "categories": {}, "recent_runs": []}

    def escape_html(self, text: str) -> str:
        if text is None:
            return ""
        return html.escape(str(text))

    def generate_html(self, items: list, stats: Dict) -> str:
        categories_html = ""
        for cat, count in sorted(stats.get("categories", {}).items()):
            safe_cat = self.escape_html(cat)
            categories_html += f'<a href="/?category={safe_cat}" class="filter-link">{safe_cat} ({count})</a> '

        items_html = ""
        for item in items:
            score_class = "high" if item["importance_score"] >= 50 else "medium" if item["importance_score"] >= 30 else "low"
            score_marker = '[HIGH]' if item["importance_score"] >= 50 else ''

            title = self.escape_html(item.get("title", ""))
            url = self.escape_html(item.get("url", ""))
            source = self.escape_html(item.get("source", ""))
            category = self.escape_html(item.get("category", ""))
            published = self.escape_html(item.get("published_at", item.get("created_at", "")))[:19]
            importance = item.get("importance_score", 0)

            if url:
                link_html = f'<a href="{url}" target="_blank">{title}</a>'
            else:
                link_html = title

            items_html += f"""
            <tr>
                <td>{link_html}</td>
                <td><span class="source-badge">{source}</span></td>
                <td><span class="category-badge">{category}</span></td>
                <td>{published}</td>
                <td><span class="score {score_class}">{score_marker} {importance}</span></td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local Intelligence Hub</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        .stats {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-item {{ display: inline-block; margin-right: 30px; }}
        .stat-label {{ font-weight: bold; color: #666; }}
        .filters {{ margin-bottom: 20px; }}
        .filter-link {{ margin-right: 10px; color: #0066cc; text-decoration: none; }}
        .filter-link:hover {{ text-decoration: underline; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f8f8; font-weight: 600; }}
        tr:hover {{ background: #fafafa; }}
        .source-badge, .category-badge {{ background: #e0e0e0; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }}
        .score {{ padding: 2px 8px; border-radius: 4px; font-weight: bold; }}
        .score.high {{ background: #ff4444; color: white; }}
        .score.medium {{ background: #ffaa00; color: white; }}
        .score.low {{ background: #44aa44; color: white; }}
        .disclaimer {{ margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px; font-size: 0.9em; color: #856404; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Local Intelligence Hub</h1>

        <div class="stats">
            <div class="stat-item"><span class="stat-label">Total Items:</span> {stats.get("total_items", 0)}</div>
            <div class="stat-item"><span class="stat-label">Categories:</span> {len(stats.get("categories", {}))}</div>
        </div>

        <div class="filters">
            <strong>Filter by category:</strong> {categories_html or "No categories yet"}
        </div>

        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Source</th>
                    <th>Category</th>
                    <th>Published</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                {items_html or "<tr><td colspan='5'>No items yet. Run 'fetch-once' first.</td></tr>"}
            </tbody>
        </table>

        <div class="disclaimer">
            <strong>Disclaimer:</strong> This is a news aggregation tool for informational purposes only.
            All information should be verified before making any decisions.
            This is NOT financial or investment advice.
        </div>
    </div>
</body>
</html>
"""
        return html


class DashboardServer:
    def __init__(self, db_path: Path, host: str = "127.0.0.1", port: int = 8765):
        self.db_path = db_path
        self.host = host
        self.port = port
        self.db = Database(db_path)
        self.server = None

    def serve_forever(self):
        DashboardHandler.db = self.db
        self.server = HTTPServer((self.host, self.port), DashboardHandler)
        print(f"Server running at http://{self.host}:{self.port}")
        self.server.serve_forever()

    def shutdown(self):
        if self.server:
            self.server.shutdown()
