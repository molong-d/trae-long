# Known Failures

## Expected Failures

### Network-Dependent Sources

#### GDELT
- **Status**: May fail if GDELT API is down
- **Handling**: Log error, continue with other sources
- **Rate limits**: Unknown, but generally generous

#### Hacker News
- **Status**: Usually reliable
- **Rate limits**: Firebase has generous limits
- **Handling**: Individual story fetch failures are skipped

#### arXiv
- **Status**: Usually reliable
- **Rate limits**: 1 request per 3 seconds recommended
- **Handling**: Catch exceptions, continue with next query

#### SEC EDGAR
- **Status**: Disabled by default
- **Rate limits**: 10 requests/second max, must have valid User-Agent
- **Handling**: User must configure their own User-Agent

#### CoinGecko
- **Status**: Free tier has rate limits
- **Rate limits**: ~10-50 requests/minute
- **Handling**: Catch 429 errors, wait and retry

#### RSS Feeds
- **Status**: Varies by feed
- **Handling**: Each feed handled independently, failures logged

## Known Limitations

### Deduplication
- Uses SHA256 hash of URL or title+source
- May miss duplicates if titles vary slightly
- May incorrectly deduplicate if URLs redirect

### Scoring
- Rule-based only, no ML
- Keywords are English-centric
- May miss non-English high-priority news

### Real-time
- Not truly real-time, uses polling
- Minimum interval is 60 seconds
- API delays may cause data lag

### Database
- SQLite single-user only
- No backup automation
- No data migration tools

### Dashboard
- No authentication
- No search functionality
- No pagination controls
- Basic HTML only, no modern UI

## API Failures to Handle

### Connection Errors
```
urllib.error.URLError
urllib.error.HTTPError
socket.timeout
```
**Handling**: Log error, record in fetch_runs, continue

### Parse Errors
```
json.JSONDecodeError
xml.etree.ElementTree.ParseError
```
**Handling**: Log error, skip malformed data

### Rate Limit Errors
```
HTTP 429 Too Many Requests
```
**Handling**: Log warning, back off, continue

### Auth Errors
```
HTTP 401 Unauthorized
HTTP 403 Forbidden
```
**Handling**: Log error, check configuration

## Not Yet Implemented

### Features Not Included
1. Data export (PDF, CSV, email)
2. Alert system
3. Multiple user support
4. WebSocket updates
5. ML-based scoring
6. Sentiment analysis
7. Topic clustering
8. Scheduled tasks (cron-like)
9. Data retention policies
10. Incremental updates

### Sources Not Included
1. Twitter/X API
2. Reddit API
3. News API (newsapi.org, etc.)
4. Bloomberg
5. Reuters
6. Academic databases
7. Government data feeds
8. Social media aggregation
