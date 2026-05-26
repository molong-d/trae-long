from .base import BaseFetcher
from .gdelt import GdeltFetcher
from .hackernews import HackernewsFetcher
from .arxiv_api import ArxivFetcher
from .sec_edgar import SecEdgarFetcher
from .coingecko import CoingeckoFetcher
from .rss import RssFetcher


def get_all_fetchers():
    return [
        GdeltFetcher,
        HackernewsFetcher,
        ArxivFetcher,
        SecEdgarFetcher,
        CoingeckoFetcher,
        RssFetcher,
    ]
