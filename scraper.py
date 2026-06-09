import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()


def scrape_website(url: str) -> dict:
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    result = app.crawl_url(
        url,
        params={
            "limit": 8,
            "scrapeOptions": {"formats": ["markdown"]},
            "includePaths": [
                "/", "/leistungen", "/services", "/ueber-uns", "/about",
                "/impressum", "/referenzen", "/loesungen", "/karriere",
                "/produkte", "/angebot", "/kontakt"
            ],
        },
        poll_interval=3,
    )

    pages = []
    if hasattr(result, "data"):
        for page in result.data:
            markdown = getattr(page, "markdown", None) or ""
            metadata = getattr(page, "metadata", {}) or {}
            if markdown.strip():
                pages.append({
                    "url": metadata.get("url", metadata.get("sourceURL", "")),
                    "title": metadata.get("title", ""),
                    "description": metadata.get("description", ""),
                    "content": markdown,
                })

    return {"url": url, "pages": pages}
