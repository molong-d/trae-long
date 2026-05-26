import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from .base import BaseFetcher


class ArxivFetcher(BaseFetcher):
    source_name = "arxiv"

    def fetch(self) -> list:
        items = []
        queries = self.config.get("queries", ["cat:cs.AI"])
        limit = self.config.get("limit", 10)

        for query in queries:
            try:
                search_query = urllib.parse.urlencode({
                    "search_query": query,
                    "start": 0,
                    "max_results": limit,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending"
                })

                url = f"http://export.arxiv.org/api/query?{search_query}"

                req = urllib.request.Request(url, headers={
                    "User-Agent": "LocalIntelligenceHub/1.0 (mailto:contact@example.com)"
                })

                with urllib.request.urlopen(req, timeout=30) as response:
                    xml_data = response.read().decode("utf-8")

                root = ET.fromstring(xml_data)

                ns = {
                    "atom": "http://www.w3.org/2005/Atom",
                    "arxiv": "http://arxiv.org/schemas/atom"
                }

                for entry in root.findall("atom:entry", ns):
                    title = entry.find("atom:title", ns)
                    title_text = title.text.replace("\n", " ").strip() if title is not None else ""

                    summary_elem = entry.find("atom:summary", ns)
                    summary_text = summary_elem.text.replace("\n", " ").strip() if summary_elem is not None else ""

                    link_elem = entry.find("atom:id", ns)
                    link = link_elem.text if link_elem is not None else ""

                    published_elem = entry.find("atom:published", ns)
                    published = published_elem.text if published_elem is not None else None

                    authors = []
                    for author in entry.findall("atom:author", ns):
                        name = author.find("atom:name", ns)
                        if name is not None:
                            authors.append(name.text)
                    author_str = ", ".join(authors[:3])
                    if len(authors) > 3:
                        author_str += f" et al. ({len(authors)} total)"

                    full_summary = f"Authors: {author_str}\n{summary_text[:300]}"

                    items.append(self.create_item(
                        title=title_text,
                        url=link,
                        summary=full_summary,
                        published_at=published,
                        raw={"authors": authors, "query": query}
                    ))

            except Exception as e:
                print(f"arXiv fetch error for query '{query}': {e}")

        return items[:limit * len(queries)]
