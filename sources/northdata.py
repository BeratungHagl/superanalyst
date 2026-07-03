"""Northdata: Firmendaten via Firecrawl-Scraping."""
import os
from firecrawl.v2.client import FirecrawlClient
from dotenv import load_dotenv

load_dotenv()


def get_northdata(company_name: str, location: str = "") -> dict:
    """Scrapt Northdata für Firmendaten und Finanzkennzahlen."""
    client = FirecrawlClient(api_key=os.getenv("FIRECRAWL_API_KEY"))

    query = company_name
    if location:
        query += f" {location}"

    search_url = f"https://www.northdata.de/{query.replace(' ', '%20')}"

    try:
        result = client.scrape(
            search_url,
            formats=["markdown"],
            only_main_content=True,
        )
        data = result.model_dump()
        markdown = data.get("markdown") or ""

        return {
            "source": "northdata",
            "url": search_url,
            "content": markdown,
            "available": bool(markdown.strip()),
        }
    except Exception as e:
        return {
            "source": "northdata",
            "url": search_url,
            "content": "",
            "available": False,
            "error": str(e),
        }
