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
    """Alle gescrapten Seiten zu einem Text zusammenführen."""
    parts = []
    for page in scraped.get("pages", []):
        parts.append(f"--- Seite: {page.get('url', '')} ---\n{page.get('content', '')}")
    return "\n\n".join(parts)[:60000]  # Token-Limit einhalten


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


def analyze_strategy(profile: CompanyProfile, scraped: dict) -> StrategicAnalysis:
    """Schritt 2: Strategische Tiefenanalyse."""
    content = _build_content(scraped)

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

    # Antwort in strukturiertes Modell parsen
    sections = _parse_analysis(raw)
    return StrategicAnalysis(**sections)


def _parse_analysis(text: str) -> dict:
    """Parst die freie LLM-Antwort in die Modell-Felder."""
    # Zweiter LLM-Call: Strukturierung der Antwort als JSON
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
