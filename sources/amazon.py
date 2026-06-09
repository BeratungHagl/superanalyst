"""Amazon Research: Eigene Präsenz + Wettbewerber via Firecrawl."""
import os
from firecrawl.v2.client import FirecrawlClient
from dotenv import load_dotenv

load_dotenv()


def get_amazon(company_name: str, products: str = "") -> dict:
    """Prüft Amazon-Präsenz des Unternehmens und Wettbewerbsumfeld."""
    client = FirecrawlClient(api_key=os.getenv("FIRECRAWL_API_KEY"))

    search_term = products if products else company_name
    amazon_url = f"https://www.amazon.de/s?k={search_term.replace(' ', '+')}"

    result = {
        "source": "amazon",
        "search_term": search_term,
        "search_url": amazon_url,
        "own_presence": "",
        "competitors": "",
        "available": False,
        "error": None,
    }

    try:
        scraped = client.scrape(
            amazon_url,
            formats=["markdown"],
            only_main_content=True,
        )
        data = scraped.model_dump()
        markdown = data.get("markdown") or ""

        if markdown.strip():
            result["own_presence"] = markdown
            result["available"] = True

        # Zweite Suche: Marke/Seller direkt
        seller_url = f"https://www.amazon.de/s?k={company_name.replace(' ', '+')}+shop"
        scraped2 = client.scrape(
            seller_url,
            formats=["markdown"],
            only_main_content=True,
        )
        data2 = scraped2.model_dump()
        result["competitors"] = data2.get("markdown") or ""

    except Exception as e:
        result["error"] = str(e)

    return result
