#!/usr/bin/env python3
import sys
import os
import json
import time
import signal
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "intelligence_hub"))

from src.db import Database
from src.scoring import ImportanceScorer
from src.digest import DigestGenerator
from src.dashboard import DashboardServer


def load_config():
    config_path = PROJECT_ROOT / "intelligence_hub" / "config" / "sources.json"
    with open(config_path, "r") as f:
        return json.load(f)


def resolve_path(relative_path):
    return PROJECT_ROOT / relative_path


def setup_logging(log_path):
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )


def cmd_init_db(args):
    config = load_config()
    db_path = resolve_path(config["app"]["db_path"])
    db = Database(db_path)
    db.init_db()
    print(f"Database initialized at: {db_path}")
    return 0


def cmd_fetch_once(args):
    config = load_config()
    setup_logging(str(resolve_path(config["app"]["log_path"])))
    logger = logging.getLogger(__name__)

    db_path = resolve_path(config["app"]["db_path"])
    db = Database(db_path)
    db.init_db()

    from src.fetchers import get_all_fetchers

    total_items = 0
    failed_sources = []

    for fetcher_class in get_all_fetchers():
        source_name = fetcher_class.__name__.replace("Fetcher", "").lower()
        if source_name not in config["sources"]:
            continue

        source_config = config["sources"][source_name]
        if not source_config.get("enabled", False):
            logger.info(f"Skipping disabled source: {source_name}")
            continue

        logger.info(f"Fetching from: {source_name}")
        try:
            fetcher = fetcher_class(source_config)
            items = fetcher.fetch()

            for item in items:
                item["importance_score"] = ImportanceScorer.calculate(item)
                db.insert_item(item)
                total_items += 1

            db.record_fetch_run(source_name, "success", len(items))
            logger.info(f"Fetched {len(items)} items from {source_name}")
        except Exception as e:
            logger.error(f"Failed to fetch from {source_name}: {e}")
            db.record_fetch_run(source_name, "error", 0, str(e))
            failed_sources.append(source_name)

    print(f"Fetch complete. Total new items: {total_items}")
    if failed_sources:
        print(f"Failed sources: {', '.join(failed_sources)}")
    return 0


def cmd_digest(args):
    config = load_config()
    db_path = resolve_path(config["app"]["db_path"])
    db = Database(db_path)

    generator = DigestGenerator(db)
    digest_content = generator.generate()

    digest_path = resolve_path(config["app"]["digest_path"])
    Path(digest_path).parent.mkdir(parents=True, exist_ok=True)
    with open(digest_path, "w") as f:
        f.write(digest_content)

    print(f"Digest generated: {digest_path}")
    return 0


def cmd_serve(args):
    config = load_config()
    host = config["app"]["dashboard_host"]
    port = config["app"]["dashboard_port"]

    db_path = resolve_path(config["app"]["db_path"])
    server = DashboardServer(db_path, host, port)

    def signal_handler(sig, frame):
        print("\nShutting down server...")
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Starting dashboard server at http://{host}:{port}")
    print("Press Ctrl+C to stop")
    server.serve_forever()


def cmd_status(args):
    config = load_config()
    db_path = resolve_path(config["app"]["db_path"])
    db = Database(db_path)

    stats = db.get_stats()

    print("=" * 50)
    print("Local Intelligence Hub - Status")
    print("=" * 50)
    print(f"Total items: {stats['total_items']}")
    print(f"Categories:")

    for category, count in stats["categories"].items():
        print(f"  - {category}: {count}")

    print("\nRecent fetch runs:")
    for run in stats["recent_runs"]:
        print(f"  - {run['source']}: {run['status']} ({run['item_count']} items) at {run['finished_at'] or run['started_at']}")

    return 0


def cmd_watch(args):
    config = load_config()
    interval = args.interval if hasattr(args, 'interval') else 300
    min_interval = config["fetch"]["min_watch_interval_seconds"]

    if interval < min_interval:
        print(f"Error: interval must be at least {min_interval} seconds")
        return 1

    print(f"Starting watch mode with interval: {interval} seconds")
    print("Press Ctrl+C to stop")

    def signal_handler(sig, frame):
        print("\nStopping watch mode...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running fetch-once...")
        os.system(f"python3 {__file__} fetch-once")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Generating digest...")
        os.system(f"python3 {__file__} digest")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sleep for {interval} seconds...")
        time.sleep(interval)


def main():
    if len(sys.argv) < 2:
        print("Local Intelligence Hub MVP")
        print("Usage:")
        print("  python3 main.py init-db")
        print("  python3 main.py fetch-once")
        print("  python3 main.py digest")
        print("  python3 main.py serve")
        print("  python3 main.py status")
        print("  python3 main.py watch --interval 300")
        return 1

    command = sys.argv[1]

    if command == "init-db":
        return cmd_init_db(sys.argv[2:] if len(sys.argv) > 2 else [])
    elif command == "fetch-once":
        return cmd_fetch_once(sys.argv[2:] if len(sys.argv) > 2 else [])
    elif command == "digest":
        return cmd_digest(sys.argv[2:] if len(sys.argv) > 2 else [])
    elif command == "serve":
        return cmd_serve(sys.argv[2:] if len(sys.argv) > 2 else [])
    elif command == "status":
        return cmd_status(sys.argv[2:] if len(sys.argv) > 2 else [])
    elif command == "watch":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--interval", type=int, default=300)
        args = parser.parse_args(sys.argv[2:] if len(sys.argv) > 2 else [])
        return cmd_watch(args)
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
