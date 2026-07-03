import os
from firecrawl.v2.client import FirecrawlClient
from dotenv import load_dotenv

load_dotenv()


def scrape_website(url: str) -> dict:
    client = FirecrawlClient(api_key=os.getenv("FIRECRAWL_API_KEY"))

    result = client.crawl(
        url,
        limit=8,
        include_paths=[
            "/", "/leistungen", "/services", "/ueber-uns", "/about",
            "/impressum", "/referenzen", "/loesungen", "/karriere",
            "/produkte", "/angebot", "/kontakt"
        ],
        formats=["markdown"],
        only_main_content=True,
        poll_interval=3,
    )

    pages = []
    result_dict = result.model_dump()
    for page in result_dict.get("data") or []:
        markdown = page.get("markdown") or ""
        metadata = page.get("metadata") or {}
        if markdown.strip():
            pages.append({
                "url": metadata.get("url") or metadata.get("source_url") or "",
                "title": metadata.get("title") or "",
                "description": metadata.get("description") or "",
                "content": markdown,
            })

    return {"url": url, "pages": pages}
