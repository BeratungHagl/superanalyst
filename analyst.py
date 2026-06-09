import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from models import CompanyProfile, StrategicAnalysis
from prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT, ANALYSIS_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


def _build_content(scraped: dict) -> str:
    """Website-Seiten zu einem Text zusammenführen."""
    parts = []
    for page in scraped.get("pages", []):
        parts.append(f"--- Seite: {page.get('url', '')} ---\n{page.get('content', '')}")
    return "\n\n".join(parts)[:40000]


def _build_enriched_content(scraped: dict, extra_sources: dict) -> str:
    """Website + alle Zusatzquellen zu einem Analysetext zusammenführen."""
    parts = [_build_content(scraped)]

    # Northdata
    nd = extra_sources.get("northdata", {})
    if nd.get("available") and nd.get("content"):
        parts.append(f"--- NORTHDATA (Firmendaten) ---\n{nd['content'][:5000]}")

    # Sistrix
    sx = extra_sources.get("sistrix", {})
    if sx.get("available"):
        si_text = f"Sichtbarkeitsindex: {sx.get('sichtbarkeitsindex')} (Trend: {sx.get('trend')})\n"
        keywords = sx.get("top_keywords", [])
        if keywords:
            si_text += "Top-Keywords:\n" + "\n".join(
                f"  - {kw['keyword']} (Position {kw['position']})" for kw in keywords
            )
        parts.append(f"--- SISTRIX (SEO) ---\n{si_text}")

    # Amazon
    az = extra_sources.get("amazon", {})
    if az.get("available"):
        parts.append(f"--- AMAZON (Suchergebnisse für '{az.get('search_term')}') ---\n{az.get('own_presence', '')[:5000]}")
        if az.get("competitors"):
            parts.append(f"--- AMAZON (Wettbewerber) ---\n{az.get('competitors', '')[:3000]}")

    # LinkedIn
    li = extra_sources.get("linkedin", {})
    if li.get("available") and li.get("content"):
        parts.append(f"--- LINKEDIN ---\n{li['content'][:3000]}")

    # Google News
    gn = extra_sources.get("google", {})
    if gn.get("available") and gn.get("content"):
        parts.append(f"--- GOOGLE NEWS ---\n{gn['content'][:3000]}")

    return "\n\n".join(parts)[:70000]


def extract_profile(scraped: dict) -> CompanyProfile:
    """Schritt 1: Strukturierte Firmendaten aus Website extrahieren."""
    content = _build_content(scraped)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": EXTRACTION_PROMPT.format(content=content)},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    data = json.loads(response.choices[0].message.content)
    data["website"] = scraped.get("url", data.get("website", ""))
    return CompanyProfile(**data)


def analyze_strategy(
    profile: CompanyProfile,
    scraped: dict,
    extra_sources: dict | None = None,
) -> StrategicAnalysis:
    """Schritt 2: Strategische Tiefenanalyse mit allen Datenquellen."""
    content = _build_enriched_content(scraped, extra_sources or {})

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": ANALYSIS_PROMPT.format(
                    firmenname=profile.firmenname,
                    website=profile.website,
                    content=content,
                ),
            },
        ],
        temperature=0.4,
    )

    raw = response.choices[0].message.content
    sections = _parse_analysis(raw)
    return StrategicAnalysis(**sections)


def _parse_analysis(text: str) -> dict:
    """Parst die freie LLM-Antwort in die Modell-Felder."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Du extrahierst strukturierte Daten aus Analysetexten. Antworte nur mit validem JSON.",
            },
            {
                "role": "user",
                "content": f"""Extrahiere aus folgendem Analysetext die Inhalte in dieses JSON-Schema:

{{
  "was_wird_verkauft": "...",
  "leistungen": "...",
  "probleme_die_geloest_werden": "...",
  "zielgruppe": "...",
  "kundengruppen": "...",
  "spezifitaet_zielgruppe": "...",
  "klarheit_positionierung": "...",
  "differenzierung": "...",
  "kommunikation_generisch_oder_konkret": "...",
  "leistungsversprechen": "...",
  "leistungen_vs_ergebnisse": "...",
  "wachstumshemmnisse": "...",
  "schwachstellen": "...",
  "chancen": "...",
  "ziel_des_kontakts": "...",
  "vermutete_herausforderungen": "...",
  "relevante_analysebereiche": "..."
}}

Analysetext:
{text}""",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    return json.loads(response.choices[0].message.content)
