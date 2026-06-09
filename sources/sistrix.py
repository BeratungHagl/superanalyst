"""Sistrix: SEO-Sichtbarkeit via offizieller API."""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SISTRIX_BASE = "https://api.sistrix.com"


def _get(endpoint: str, params: dict) -> dict:
    params["api_key"] = os.getenv("SISTRIX_API_KEY")
    params["format"] = "json"
    resp = httpx.get(f"{SISTRIX_BASE}/{endpoint}", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_sistrix(domain: str) -> dict:
    """Holt SEO-Sichtbarkeit, Top-Keywords und Trend für eine Domain."""
    # Domain bereinigen
    domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/").split("/")[0]

    result = {
        "source": "sistrix",
        "domain": domain,
        "sichtbarkeitsindex": None,
        "trend": None,
        "top_keywords": [],
        "available": False,
        "error": None,
    }

    try:
        # Sichtbarkeitsindex
        si_data = _get("domain/sivisibility", {"domain": domain})
        items = si_data.get("answer", [{}])[0].get("sivisibility", [])
        if items:
            result["sichtbarkeitsindex"] = items[-1].get("value")
            # Trend: Vergleich letzter vs vorletzter Wert
            if len(items) >= 2:
                delta = round(items[-1].get("value", 0) - items[-2].get("value", 0), 4)
                result["trend"] = f"{'+' if delta >= 0 else ''}{delta}"
            result["available"] = True
    except Exception as e:
        result["error"] = f"Sichtbarkeit: {e}"

    try:
        # Top-Keywords
        kw_data = _get("domain/keywords", {"domain": domain, "limit": 10})
        keywords = kw_data.get("answer", [{}])[0].get("keyword", [])
        result["top_keywords"] = [
            {"keyword": kw.get("value"), "position": kw.get("position")}
            for kw in keywords[:10]
        ]
    except Exception as e:
        if result["error"]:
            result["error"] += f" | Keywords: {e}"
        else:
            result["error"] = f"Keywords: {e}"

    return result
