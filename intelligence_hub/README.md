# Local Intelligence Hub

A local intelligence aggregation MVP for collecting and analyzing world events, technology, finance, science, and cryptocurrency market data.

## Project Overview

This is a **local intelligence aggregation tool**, not a commercial system. It collects data from various public sources for informational purposes only.

**This is NOT financial or investment advice. Information should be verified before use.**

## Features

- **Multi-source data aggregation**: GDELT (world events), Hacker News (tech), arXiv (research papers), SEC EDGAR (financial filings), CoinGecko (crypto), RSS feeds
- **Local SQLite database storage**
- **Importance scoring**: Rule-based scoring system (0-100) to prioritize items
- **Daily digest generation**: Markdown format reports
- **Local web dashboard**: View aggregated intelligence at http://127.0.0.1:8765
- **Near real-time polling**: Configurable watch mode for periodic fetching

## Data Sources

| Source | Category | Description |
|--------|----------|-------------|
| GDELT | World | International news and events via GDELT API |
| Hacker News | Tech | Top tech stories, AI, startups, developer news |
| arXiv | Science | AI/ML/NLP research papers |
| SEC EDGAR | Finance | Company filings and regulatory documents |
| CoinGecko | Crypto | Cryptocurrency prices and market data |
| RSS | Custom | Configurable RSS feeds |

## Quick Start

### 1. Initialize Database

```bash
python3 intelligence_hub/src/main.py init-db
```

### 2. Fetch Data Once

```bash
python3 intelligence_hub/src/main.py fetch-once
```

### 3. Generate Digest

```bash
python3 intelligence_hub/src/main.py digest
```

### 4. View Dashboard

```bash
python3 intelligence_hub/src/main.py serve
```

Then open: http://127.0.0.1:8765

### 5. Check Status

```bash
python3 intelligence_hub/src/main.py status
```

### 6. Watch Mode (Periodic Fetching)

```bash
python3 intelligence_hub/src/main.py watch --interval 300
```

This fetches data every 300 seconds (5 minutes). Minimum interval is 60 seconds.

## Configuration

Edit `intelligence_hub/config/sources.json` to customize:

- Enable/disable data sources
- Set keywords for GDELT
- Configure arXiv queries
- Add CIKs for SEC EDGAR
- Configure RSS feeds

**Important**: If enabling SEC EDGAR, replace the placeholder `user_agent` with your real contact information:

```json
"sec_edgar": {
    "user_agent": "Your Name your@email.com"
}
```

## Real-time Behavior

This MVP uses **near-real-time polling**, not true millisecond-level streaming.

- Watch mode checks sources at configurable intervals
- Each source may have its own API rate limits
- Some sources may be temporarily unavailable

## Risks and Limitations

1. **Information accuracy**: Aggregated news should be verified; this tool does not fact-check
2. **Financial data delay**: Crypto/stock data may be delayed
3. **API rate limits**: Free APIs have usage limits
4. **RSS/API failures**: External services may be unavailable
5. **Polling interval**: Not real-time streaming
6. **No investment advice**: This is informational only

## Testing

```bash
python3 intelligence_hub/tests/test_basic.py
```

## Project Structure

```
intelligence_hub/
├── config/
│   └── sources.json          # Configuration file
├── data/
│   └── intelligence.db       # SQLite database
├── logs/
│   └── fetch.log             # Fetch logs
├── reports/
│   └── latest_digest.md      # Generated digest
├── src/
│   ├── main.py               # CLI entry point
│   ├── db.py                 # Database operations
│   ├── scoring.py            # Importance scoring
│   ├── digest.py             # Digest generation
│   ├── dashboard.py          # Web dashboard
│   └── fetchers/
│       ├── __init__.py
│       ├── gdelt.py
│       ├── hackernews.py
│       ├── arxiv_api.py
│       ├── sec_edgar.py
│       ├── coingecko.py
│       └── rss.py
├── tests/
│   └── test_basic.py
├── requirements.txt
└── README.md
```

## Future Extensions

- Additional data sources (news APIs, social media)
- Better scoring models (ML-based)
- Export formats (PDF, email)
- Alerts/notifications
- WebSocket for real-time updates
- Multiple user support

## Disclaimer

This tool aggregates news and information from public sources for **informational purposes only**.

- NOT financial or investment advice
- NOT responsible for decisions made based on this data
- All information should be verified
- API availability depends on third-party services
