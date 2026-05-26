import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class Database:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                category TEXT,
                title TEXT NOT NULL,
                url TEXT,
                published_at TEXT,
                fetched_at TEXT NOT NULL,
                summary TEXT,
                content_hash TEXT UNIQUE,
                importance_score INTEGER DEFAULT 0,
                raw_json TEXT,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fetch_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                status TEXT NOT NULL,
                item_count INTEGER DEFAULT 0,
                error_message TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_content_hash ON items(content_hash)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_category ON items(category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_source ON items(source)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_published_at ON items(published_at)
        """)

        conn.commit()
        conn.close()

    def generate_hash(self, item: Dict[str, Any]) -> str:
        content = item.get("url") or (item.get("title", "") + item.get("source", ""))
        return hashlib.sha256(content.encode()).hexdigest()

    def item_exists(self, content_hash: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM items WHERE content_hash = ?", (content_hash,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def insert_item(self, item: Dict[str, Any]) -> bool:
        content_hash = self.generate_hash(item)

        if self.item_exists(content_hash):
            return False

        conn = self.get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT INTO items (
                source, category, title, url, published_at, fetched_at,
                summary, content_hash, importance_score, raw_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.get("source", ""),
            item.get("category", ""),
            item.get("title", ""),
            item.get("url", ""),
            item.get("published_at", ""),
            item.get("fetched_at", now),
            item.get("summary", ""),
            content_hash,
            item.get("importance_score", 0),
            json.dumps(item.get("raw", {})),
            now
        ))

        conn.commit()
        conn.close()
        return True

    def record_fetch_run(self, source: str, status: str, item_count: int, error_message: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()

        started_at = datetime.utcnow().isoformat()
        finished_at = datetime.utcnow().isoformat() if status in ("success", "error") else None

        cursor.execute("""
            INSERT INTO fetch_runs (source, started_at, finished_at, status, item_count, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (source, started_at, finished_at, status, item_count, error_message))

        conn.commit()
        conn.close()

    def get_items(self, limit: int = 100, category: str = None, source: str = None,
                  min_score: int = None) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM items WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if source:
            query += " AND source = ?"
            params.append(source)

        if min_score is not None:
            query += " AND importance_score >= ?"
            params.append(min_score)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_high_score_items(self, hours: int = 24, min_score: int = 30) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM items
            WHERE importance_score >= ?
            AND datetime(created_at) >= datetime('now', '-' || ? || ' hours')
            ORDER BY importance_score DESC, created_at DESC
        """, (min_score, hours))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_stats(self) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM items")
        total_items = cursor.fetchone()["count"]

        cursor.execute("SELECT category, COUNT(*) as count FROM items GROUP BY category")
        categories = {row["category"]: row["count"] for row in cursor.fetchall()}

        cursor.execute("""
            SELECT * FROM fetch_runs
            ORDER BY started_at DESC
            LIMIT 10
        """)
        recent_runs = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            "total_items": total_items,
            "categories": categories,
            "recent_runs": recent_runs
        }
