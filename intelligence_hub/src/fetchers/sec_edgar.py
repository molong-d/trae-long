import json
import urllib.request
from .base import BaseFetcher


class SecEdgarFetcher(BaseFetcher):
    source_name = "sec_edgar"

    def fetch(self) -> list:
        items = []
        ciks = self.config.get("ciks", [])
        user_agent = self.config.get("user_agent", "LocalIntelligenceHub contact@example.com")

        if not ciks:
            print("SEC EDGAR: No CIKs configured")
            return items

        for cik in ciks:
            try:
                url = f"https://data.sec.gov/submissions/CIK{cik}.json"

                req = urllib.request.Request(url, headers={
                    "User-Agent": user_agent,
                    "Accept": "application/json"
                })

                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode("utf-8"))

                company_name = data.get("name", "Unknown Company")
                recent_filings = data.get("filings", {}).get("recent", {})

                forms = recent_filings.get("form", [])[:10]
                dates = recent_filings.get("filingDate", [])
                links = recent_filings.get("FilingSummary", [])

                for i, form in enumerate(forms):
                    title = f"{company_name} - {form} Filing"
                    filing_date = dates[i] if i < len(dates) else None
                    filing_link = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form}"

                    items.append(self.create_item(
                        title=title,
                        url=filing_link,
                        summary=f"CIK: {cik} | Company: {company_name}",
                        published_at=filing_date,
                        raw={"cik": cik, "company_name": company_name, "form": form}
                    ))

            except Exception as e:
                print(f"SEC EDGAR fetch error for CIK {cik}: {e}")

        return items
