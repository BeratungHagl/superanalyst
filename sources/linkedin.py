"""LinkedIn: Unternehmensprofil via Firecrawl (optional)."""
import os
from firecrawl.v2.client import FirecrawlClient
from dotenv import load_dotenv

load_dotenv()


def get_linkedin(company_name: str, linkedin_url: str = "") -> dict:
    """Scrapt LinkedIn-Unternehmensprofil falls URL bekannt oder findbar."""
    client = FirecrawlClient(api_key=os.getenv("FIRECRAWL_API_KEY"))

    result = {
        "source": "linkedin",
        "url": linkedin_url,
        "content": "",
        "available": False,
        "error": None,
    }

    if not linkedin_url:
        result["error"] = "Keine LinkedIn-URL angegeben"
        return result

    try:
        scraped = client.scrape(
            linkedin_url,
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
