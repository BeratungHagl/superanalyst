"""Google Search: News & Erwähnungen via Firecrawl (optional)."""
import os
from firecrawl.v2.client import FirecrawlClient
from dotenv import load_dotenv

load_dotenv()


def get_google_news(company_name: str) -> dict:
    """Sucht nach aktuellen News und Presseartikeln zum Unternehmen."""
    client = FirecrawlClient(api_key=os.getenv("FIRECRAWL_API_KEY"))

    query = f"{company_name} Presse News Unternehmen"
    search_url = f"https://www.google.de/search?q={query.replace(' ', '+')}&tbm=nws"

    result = {
        "source": "google",
        "query": query,
        "content": "",
        "available": False,
        "error": None,
    }

    try:
        scraped = client.scrape(
            search_url,
            formats=["markdown"],
            only_main_content=True,
        )
        data = scraped.model_dump()
        markdown = data.get("markdown") or ""
        result["content"] = markdown
        result["available"] = bool(markdown.strip())
    except Exception as e:
        result["error"] = str(e)

    return result
