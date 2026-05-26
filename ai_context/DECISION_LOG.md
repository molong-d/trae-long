# Decision Log

## Architecture Decisions

### Why Python Standard Library Only?

1. **Zero dependencies**: No package installation required
2. **Portability**: Works anywhere Python 3 is installed
3. **Simplicity**: Easier to audit, maintain, and debug
4. **MVP focus**: Prioritizes functionality over complexity

### Why SQLite?

1. **Built-in**: sqlite3 is part of Python standard library
2. **Serverless**: No database server setup required
3. **Single file**: Easy to backup, move, or delete
4. **ACID compliant**: Reliable data storage
5. **Sufficient for MVP**: Single-user local tool

### Why Polling Instead of Real-time Streaming?

1. **Simplicity**: Polling is easier to implement and debug
2. **API compatibility**: Most free APIs don't support WebSocket
3. **Rate limiting**: Polling respects API limits naturally
4. **MVP scope**: Near-real-time is sufficient for情报聚合

### Why Rule-based Scoring Instead of ML?

1. **Interpretability**: Clear why an item scored high
2. **No training data**: ML requires labeled data
3. **No dependencies**: ML libraries add complexity
4. **MVP scope**: Keyword matching is sufficient for prioritization

### Why No Automatic Trading/Investment Features?

1. **Risk management**: Automated financial decisions carry high risk
2. **Legal compliance**: Automated trading may violate regulations
3. **Liability**: We cannot be responsible for financial losses
4. **Task specification**: Explicitly prohibited

### Why No Large-scale Scraping?

1. **Legal risk**: May violate website terms of service
2. **Ethical considerations**: Excessive requests burden servers
3. **API-first**: Prefer official APIs for reliable data
4. **Task specification**: Explicitly prohibited

### Why SEC EDGAR Disabled by Default?

1. **User-Agent requirement**: SEC requires accurate contact info
2. **Rate limiting**: SEC has strict rate limits
3. **User responsibility**: Users should configure their own User-Agent
4. **Safety first**: Avoid accidental violations

## Design Decisions

### Item Schema
- Unified format across all fetchers for consistent processing
- SHA256 hash for deduplication (using URL or title+source)
- Importance score calculated at fetch time

### Database Schema
- Two tables: items (data) and fetch_runs (metadata)
- Indexes on frequently queried columns
- No foreign keys (simple MVP design)

### CLI Commands
- Simple subcommands: init-db, fetch-once, digest, serve, status, watch
- Consistent command structure following Unix conventions
- Watch mode with safe Ctrl+C handling

### Dashboard
- Single HTML page with no external dependencies
- Standard library http.server (no Flask/FastAPI)
- JSON API endpoints for programmatic access
