from typing import Dict, Any


class ImportanceScorer:
    KEYWORDS_HIGH = {
        "war", "conflict", "warzone", "military",
        "election", "vote", "ballot",
        "central bank", "rate cut", "rate hike", "interest rate",
        "inflation", "recession", "depression",
        "earthquake", "tsunami", "hurricane", "typhoon",
        "pandemic", "epidemic", "outbreak",
        "sanctions", "embargo",
        "bankruptcy", "default",
        "acquisition", "merger", "takeover",
        "bankruptcy filing",
    }

    KEYWORDS_MEDIUM = {
        "ai", "artificial intelligence", "machine learning", "deep learning",
        "chip", "semiconductor", "nvidia", "amd", "intel",
        "openai", "anthropic", "google", "microsoft", "apple", "tesla",
        "bitcoin", "ethereum", "crypto", "blockchain",
        "sec", "sec investigation", "sec lawsuit",
        "earnings", "revenue", "profit", "loss",
        "ipo", "stock", "market",
        "supply chain", "shortage",
        "regulation", "law", "bill", "act",
        "research", "discovery", "breakthrough",
        "launch", "release", "announcement",
    }

    KEYWORDS_LOW = {
        "trending", "viral", "popular",
        "analysis", "opinion", "commentary",
        "review", "preview",
    }

    SOURCE_WEIGHTS = {
        "gdelt": 1.2,
        "sec_edgar": 1.3,
        "coingecko": 0.9,
        "hackernews": 1.0,
        "arxiv": 1.1,
        "rss": 1.0,
    }

    @classmethod
    def calculate(cls, item: Dict[str, Any]) -> int:
        base_score = 10

        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()

        combined_text = title + " " + summary

        title_matches_high = sum(1 for kw in cls.KEYWORDS_HIGH if kw in title)
        summary_matches_high = sum(1 for kw in cls.KEYWORDS_HIGH if kw in summary)
        high_score = (title_matches_high * 20) + (summary_matches_high * 10)

        title_matches_medium = sum(1 for kw in cls.KEYWORDS_MEDIUM if kw in title)
        summary_matches_medium = sum(1 for kw in cls.KEYWORDS_MEDIUM if kw in summary)
        medium_score = (title_matches_medium * 10) + (summary_matches_medium * 5)

        title_matches_low = sum(1 for kw in cls.KEYWORDS_LOW if kw in title)
        summary_matches_low = sum(1 for kw in cls.KEYWORDS_LOW if kw in summary)
        low_score = (title_matches_low * 3) + (summary_matches_low * 1)

        keyword_score = high_score + medium_score + low_score

        source = item.get("source", "").lower()
        source_weight = cls.SOURCE_WEIGHTS.get(source, 1.0)
        source_score = base_score * source_weight

        final_score = int((source_score + keyword_score) * source_weight)

        return min(max(final_score, 0), 100)
