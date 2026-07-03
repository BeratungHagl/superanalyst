"""Hunter.io: Ansprechpartner & E-Mail-Daten via offizieller API."""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

HUNTER_BASE = "https://api.hunter.io/v2"


def get_hunter(domain: str) -> dict:
    """Findet Ansprechpartner und E-Mails für eine Domain."""
    api_key = os.getenv("HUNTER_API_KEY")

    # Domain bereinigen
    domain = (
        domain.replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        .rstrip("/")
        .split("/")[0]
    )

    result = {
        "source": "hunter",
        "domain": domain,
        "organisation": None,
        "kontakte": [],
        "email_pattern": None,
        "emails_gefunden": 0,
        "available": False,
        "error": None,
    }

    try:
        resp = httpx.get(
            f"{HUNTER_BASE}/domain-search",
            params={"domain": domain, "api_key": api_key, "limit": 10},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})

        result["organisation"] = data.get("organization")
        result["email_pattern"] = data.get("pattern")
        result["emails_gefunden"] = data.get("emails_count", 0)

        kontakte = []
        for email_data in data.get("emails", []):
            first = email_data.get("first_name", "")
            last = email_data.get("last_name", "")
            name = f"{first} {last}".strip()
            kontakt = {
                "name": name or "Unbekannt",
                "email": email_data.get("value", ""),
                "position": email_data.get("position", ""),
                "abteilung": email_data.get("department", ""),
                "linkedin": email_data.get("linkedin", ""),
                "confidence": email_data.get("confidence", 0),
            }
            if kontakt["email"]:
                kontakte.append(kontakt)

        result["kontakte"] = kontakte
        result["available"] = bool(kontakte or result["emails_gefunden"] > 0)

    except Exception as e:
        result["error"] = str(e)

    return result
