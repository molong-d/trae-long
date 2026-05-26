#!/usr/bin/env python3
import sys
import os
import json
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import Database
from src.scoring import ImportanceScorer
from src.digest import DigestGenerator


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db = Database(Path(self.temp_db.name))
        self.db.init_db()

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_init_db(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.assertIn("items", tables)
        self.assertIn("fetch_runs", tables)

    def test_insert_item(self):
        item = {
            "source": "test",
            "category": "test",
            "title": "Test Item",
            "url": "https://example.com/test",
            "published_at": "2024-01-01T00:00:00",
            "fetched_at": "2024-01-01T00:00:00",
            "summary": "Test summary",
            "raw": {}
        }

        result = self.db.insert_item(item)
        self.assertTrue(result)

    def test_duplicate_hash(self):
        item = {
            "source": "test",
            "category": "test",
            "title": "Test Item",
            "url": "https://example.com/test",
            "published_at": "2024-01-01T00:00:00",
            "fetched_at": "2024-01-01T00:00:00",
            "summary": "Test summary",
            "raw": {}
        }

        result1 = self.db.insert_item(item)
        result2 = self.db.insert_item(item)

        self.assertTrue(result1)
        self.assertFalse(result2)

    def test_get_items(self):
        item = {
            "source": "test",
            "category": "test",
            "title": "Test Item",
            "url": "https://example.com/test",
            "published_at": "2024-01-01T00:00:00",
            "fetched_at": "2024-01-01T00:00:00",
            "summary": "Test summary",
            "raw": {}
        }

        self.db.insert_item(item)
        items = self.db.get_items()

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Test Item")

    def test_get_items_with_source_filter(self):
        item = {
            "source": "hackernews",
            "category": "tech",
            "title": "HN Item",
            "url": "https://example.com/hn",
            "published_at": "2024-01-01T00:00:00",
            "fetched_at": "2024-01-01T00:00:00",
            "summary": "Summary",
            "raw": {}
        }

        self.db.insert_item(item)
        items = self.db.get_items(source="hackernews")

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["source"], "hackernews")

    def test_get_stats(self):
        item = {
            "source": "test",
            "category": "test",
            "title": "Test Item",
            "url": "https://example.com/test",
            "published_at": "2024-01-01T00:00:00",
            "fetched_at": "2024-01-01T00:00:00",
            "summary": "Test summary",
            "importance_score": 50,
            "raw": {}
        }

        self.db.insert_item(item)
        stats = self.db.get_stats()

        self.assertEqual(stats["total_items"], 1)
        self.assertIn("test", stats["categories"])
        self.assertEqual(stats["categories"]["test"], 1)
        self.assertIn("sources", stats)
        self.assertIn("last_fetch_time", stats)


class TestScoring(unittest.TestCase):
    def test_score_range(self):
        test_items = [
            {"title": "Normal news item", "summary": "A regular news story"},
            {"title": "War in Ukraine", "summary": "Conflict escalation news"},
            {"title": "AI breakthrough", "summary": "New machine learning research"},
            {"title": "Bitcoin price surge", "summary": "Crypto market update"},
        ]

        for item in test_items:
            item["source"] = "test"
            item["category"] = "test"
            item["url"] = "https://example.com"
            score = ImportanceScorer.calculate(item)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_high_priority_keywords(self):
        item = {
            "source": "gdelt",
            "category": "world",
            "title": "War and election crisis",
            "summary": "Central bank rate hike causing inflation",
            "url": "https://example.com"
        }

        score = ImportanceScorer.calculate(item)
        self.assertGreater(score, 30)

    def test_source_weights(self):
        item_base = {
            "category": "test",
            "title": "Test",
            "summary": "Test summary",
            "url": "https://example.com"
        }

        item_sec = dict(item_base)
        item_sec["source"] = "sec_edgar"

        item_normal = dict(item_base)
        item_normal["source"] = "rss"

        score_sec = ImportanceScorer.calculate(item_sec)
        score_normal = ImportanceScorer.calculate(item_normal)

        self.assertGreater(score_sec, score_normal)

    def test_watchlist_keywords(self):
        ImportanceScorer._watchlist = None
        ImportanceScorer._watchlist_enabled = True

        item_no_watchlist = {
            "source": "rss",
            "category": "tech",
            "title": "AI announces new model",
            "summary": "Latest AI development",
            "url": "https://example.com"
        }
        ImportanceScorer._watchlist = ["openai", "nvidia", "bitcoin"]

        item_with_watchlist = {
            "source": "rss",
            "category": "tech",
            "title": "OpenAI announces new model",
            "summary": "Latest AI development",
            "url": "https://example.com"
        }
        score_with_watchlist = ImportanceScorer.calculate(item_with_watchlist)

        ImportanceScorer._watchlist = []
        score_no_watchlist = ImportanceScorer.calculate(item_no_watchlist)

        self.assertGreater(score_with_watchlist, score_no_watchlist)

    def test_watchlist_match(self):
        ImportanceScorer._watchlist = None
        ImportanceScorer._watchlist_enabled = True
        ImportanceScorer._watchlist = ["openai", "nvidia", "bitcoin"]

        item_match = {
            "title": "OpenAI announces GPT-5",
            "summary": "New model released"
        }

        item_no_match = {
            "title": "Weather forecast",
            "summary": "Sunny day ahead"
        }

        self.assertTrue(ImportanceScorer.check_watchlist_match(item_match))
        self.assertFalse(ImportanceScorer.check_watchlist_match(item_no_match))


class TestConfig(unittest.TestCase):
    def test_sources_json(self):
        config_path = Path(__file__).parent.parent / "config" / "sources.json"

        with open(config_path, "r") as f:
            config = json.load(f)

        self.assertIn("app", config)
        self.assertIn("sources", config)
        self.assertIn("gdelt", config["sources"])
        self.assertIn("hackernews", config["sources"])
        self.assertIn("arxiv", config["sources"])
        self.assertIn("sec_edgar", config["sources"])
        self.assertIn("coingecko", config["sources"])
        self.assertIn("rss", config["sources"])

    def test_watchlist_config(self):
        config_path = Path(__file__).parent.parent / "config" / "sources.json"

        with open(config_path, "r") as f:
            config = json.load(f)

        self.assertIn("watchlist", config)
        self.assertTrue(config["watchlist"].get("enabled", False))
        self.assertIn("keywords", config["watchlist"])
        self.assertGreater(len(config["watchlist"]["keywords"]), 0)

    def test_config_paths(self):
        config_path = Path(__file__).parent.parent / "config" / "sources.json"

        with open(config_path, "r") as f:
            config = json.load(f)

        self.assertIn("db_path", config["app"])
        self.assertIn("log_path", config["app"])
        self.assertIn("digest_path", config["app"])
        self.assertIn("dashboard_host", config["app"])
        self.assertIn("dashboard_port", config["app"])

    def test_rss_feeds_config(self):
        config_path = Path(__file__).parent.parent / "config" / "sources.json"

        with open(config_path, "r") as f:
            config = json.load(f)

        self.assertIn("feeds", config["sources"]["rss"])
        self.assertGreater(len(config["sources"]["rss"]["feeds"]), 0)

        for feed in config["sources"]["rss"]["feeds"]:
            self.assertIn("name", feed)
            self.assertIn("url", feed)
            self.assertIn("category", feed)


class TestDigest(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db = Database(Path(self.temp_db.name))
        self.db.init_db()
        self.generator = DigestGenerator(self.db)
        ImportanceScorer._watchlist = None

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_generate_empty(self):
        digest = self.generator.generate()
        self.assertIsInstance(digest, str)
        self.assertIn("Local Intelligence Hub", digest)

    def test_generate_with_items(self):
        for i in range(5):
            item = {
                "source": "test",
                "category": "test",
                "title": f"Test Item {i}",
                "url": f"https://example.com/{i}",
                "published_at": "2024-01-01T00:00:00",
                "fetched_at": "2024-01-01T00:00:00",
                "summary": "Test summary",
                "importance_score": 50,
                "raw": {}
            }
            self.db.insert_item(item)

        digest = self.generator.generate()
        self.assertIn("Test Item", digest)

    def test_digest_watchlist_section(self):
        ImportanceScorer._watchlist_enabled = True
        ImportanceScorer._watchlist = ["openai", "ai"]

        item = {
            "source": "hackernews",
            "category": "tech",
            "title": "OpenAI announces GPT-5",
            "url": "https://example.com/openai",
            "published_at": "2024-01-01T00:00:00",
            "fetched_at": "2024-01-01T00:00:00",
            "summary": "Latest AI news",
            "importance_score": 60,
            "raw": {}
        }
        self.db.insert_item(item)

        digest = self.generator.generate()
        self.assertIn("Watchlist Matched", digest)


if __name__ == "__main__":
    unittest.main()
