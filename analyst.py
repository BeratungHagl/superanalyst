import os
import json
import concurrent.futures
from openai import OpenAI
from dotenv import load_dotenv
from models import (
    CompanyProfile, StrategicAnalysis,
    DemandIntelligence, CompetitiveIntelligence, AIVisibilityIntelligence,
    Scoring, ExternalIntelligence, ExecutiveSummary,
)
from prompts import (
    SYSTEM_PROMPT, EXTRACTION_PROMPT, ANALYSIS_PROMPT,
    DEMAND_INTELLIGENCE_PROMPT, COMPETITIVE_INTELLIGENCE_PROMPT,
    AI_VISIBILITY_PROMPT, EXTERNAL_INTELLIGENCE_PROMPT, EXECUTIVE_SUMMARY_PROMPT,
)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _chat(messages: list, json_mode: bool = False, temperature: float = 0.3) -> str:
    kwargs = {"model": MODEL, "messages": messages, "temperature": temperature}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content


def _build_website_content(scraped: dict) -> str:
    parts = []
    for page in scraped.get("pages", []):
        parts.append(f"--- Seite: {page.get('url', '')} ---\n{page.get('content', '')}")
    return "\n\n".join(parts)[:40000]


def _build_enriched_content(scraped: dict, extra_sources: dict) -> str:
    parts = [_build_website_content(scraped)]

    nd = extra_sources.get("northdata", {})
    if nd.get("available") and nd.get("content"):
        parts.append(f"--- NORTHDATA ---\n{nd['content'][:5000]}")

    sx = extra_sources.get("sistrix", {})
    if sx.get("available"):
        si_text = f"Sichtbarkeitsindex: {sx.get('sichtbarkeitsindex')} (Trend: {sx.get('trend')})\n"
        kws = sx.get("top_keywords", [])
        if kws:
            si_text += "Top-Keywords:\n" + "\n".join(
                f"  - {kw['keyword']} (Position {kw['position']})" for kw in kws
            )
        parts.append(f"--- SISTRIX (SEO) ---\n{si_text}")

    az = extra_sources.get("amazon", {})
    if az.get("available"):
        parts.append(f"--- AMAZON ('{az.get('search_term')}') ---\n{az.get('own_presence', '')[:5000]}")
        if az.get("competitors"):
            parts.append(f"--- AMAZON WETTBEWERBER ---\n{az.get('competitors', '')[:3000]}")

    li = extra_sources.get("linkedin", {})
    if li.get("available") and li.get("content"):
        parts.append(f"--- LINKEDIN ---\n{li['content'][:3000]}")

    gn = extra_sources.get("google", {})
    if gn.get("available") and gn.get("content"):
        parts.append(f"--- GOOGLE NEWS ---\n{gn['content'][:3000]}")

    return "\n\n".join(parts)[:70000]


def _parse_json(text: str, schema_hint: str) -> dict:
    """Parst freien Analysetext in ein JSON-Objekt."""
    result = _chat(
        messages=[
            {"role": "system", "content": "Extrahiere strukturierte Daten. Antworte nur mit validem JSON."},
            {"role": "user", "content": f"Schema:\n{schema_hint}\n\nText:\n{text}"},
        ],
        json_mode=True,
        temperature=0.1,
    )
    return json.loads(result)


# ---------------------------------------------------------------------------
# Schritt 1: Profil extrahieren
# ---------------------------------------------------------------------------

def extract_profile(scraped: dict) -> CompanyProfile:
    content = _build_website_content(scraped)
    raw = _chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": EXTRACTION_PROMPT.format(content=content)},
        ],
        json_mode=True,
        temperature=0.2,
    )
    data = json.loads(raw)
    data["website"] = scraped.get("url", data.get("website", ""))
    return CompanyProfile(**data)


# ---------------------------------------------------------------------------
# Schritt 2: Strategische Basisanalyse
# ---------------------------------------------------------------------------

def analyze_strategy(
    profile: CompanyProfile,
    scraped: dict,
    extra_sources: dict | None = None,
) -> StrategicAnalysis:
    content = _build_enriched_content(scraped, extra_sources or {})
    raw = _chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": ANALYSIS_PROMPT.format(
                firmenname=profile.firmenname,
                website=profile.website,
                content=content,
            )},
        ],
        temperature=0.4,
    )
    schema = """{
  "was_wird_verkauft": "...", "leistungen": "...", "probleme_die_geloest_werden": "...",
  "zielgruppe": "...", "kundengruppen": "...", "spezifitaet_zielgruppe": "...",
  "klarheit_positionierung": "...", "differenzierung": "...", "kommunikation_generisch_oder_konkret": "...",
  "leistungsversprechen": "...", "leistungen_vs_ergebnisse": "...",
  "wachstumshemmnisse": "...", "schwachstellen": "...", "chancen": "...",
  "ziel_des_kontakts": "...", "vermutete_herausforderungen": "...", "relevante_analysebereiche": "..."
}"""
    return StrategicAnalysis(**_parse_json(raw, schema))


# ---------------------------------------------------------------------------
# Schritt 3: Intelligence-Module (parallel)
# ---------------------------------------------------------------------------

def analyze_demand(profile: CompanyProfile, extra_sources: dict) -> DemandIntelligence:
    content = _build_enriched_content({}, extra_sources)
    raw = _chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": DEMAND_INTELLIGENCE_PROMPT.format(
                firmenname=profile.firmenname,
                branche=profile.branche,
                content=content,
            )},
        ],
        temperature=0.4,
    )
    schema = """{
  "sichtbarkeit": "...", "gefundene_themen": "...",
  "nachfragepotenziale": "...", "unbesetzte_themen": "...",
  "demand_score": 7, "demand_score_begruendung": "..."
}"""
    return DemandIntelligence(**_parse_json(raw, schema))


def analyze_competitive(profile: CompanyProfile, extra_sources: dict) -> CompetitiveIntelligence:
    content = _build_enriched_content({}, extra_sources)
    raw = _chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": COMPETITIVE_INTELLIGENCE_PROMPT.format(
                firmenname=profile.firmenname,
                branche=profile.branche,
                website=profile.website,
                content=content,
            )},
        ],
        temperature=0.4,
    )
    schema = """{
  "staerkste_wettbewerber": "...", "themen_dominanz": "...", "haeufiger_gefunden": "...",
  "competitive_score": 6, "competitive_score_begruendung": "..."
}"""
    return CompetitiveIntelligence(**_parse_json(raw, schema))


def analyze_ai_visibility(profile: CompanyProfile) -> AIVisibilityIntelligence:
    raw = _chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": AI_VISIBILITY_PROMPT.format(
                firmenname=profile.firmenname,
                branche=profile.branche,
                website=profile.website,
            )},
        ],
        temperature=0.5,
    )
    schema = """{
  "marke_in_ai_genannt": "...", "wettbewerber_in_ai": "...",
  "verwendete_quellen": "...", "themen_mit_ai_sichtbarkeit": "...",
  "ai_visibility_score": 5, "ai_visibility_score_begruendung": "..."
}"""
    return AIVisibilityIntelligence(**_parse_json(raw, schema))


# ---------------------------------------------------------------------------
# Schritt 4: Scoring + External Intelligence + Executive Summary
# ---------------------------------------------------------------------------

def build_scoring(
    strategy: StrategicAnalysis,
    demand: DemandIntelligence,
    competitive: CompetitiveIntelligence,
    ai: AIVisibilityIntelligence,
) -> Scoring:
    # Positionierungsscore aus dem Strategietext extrahieren
    raw = _chat(
        messages=[
            {"role": "system", "content": "Antworte nur mit validem JSON."},
            {"role": "user", "content": f"""Lies diesen Text und extrahiere den Positionierungsscore (1-10).
Falls kein expliziter Score vorhanden ist, schätze ihn basierend auf der Beschreibung.

Text: {strategy.klarheit_positionierung}

JSON: {{"positionierung_score": 7, "positionierung_begruendung": "..."}}"""},
        ],
        json_mode=True,
        temperature=0.1,
    )
    pos_data = json.loads(raw)
    pos_score = pos_data.get("positionierung_score", 5)
    pos_begruendung = pos_data.get("positionierung_begruendung", "")

    # Gewichteter Gesamtscore
    gesamt = round(
        pos_score * 0.25 +
        demand.demand_score * 0.30 +
        competitive.competitive_score * 0.25 +
        ai.ai_visibility_score * 0.20
    )

    return Scoring(
        positionierung_score=pos_score,
        positionierung_begruendung=pos_begruendung,
        demand_score=demand.demand_score,
        competitive_score=competitive.competitive_score,
        ai_visibility_score=ai.ai_visibility_score,
        gesamt_score=gesamt,
        gesamt_begruendung=(
            f"Gewichtung: Positionierung 25% ({pos_score}), "
            f"Demand 30% ({demand.demand_score}), "
            f"Competitive 25% ({competitive.competitive_score}), "
            f"AI Visibility 20% ({ai.ai_visibility_score})"
        ),
    )


def build_external_intelligence(
    profile: CompanyProfile,
    demand: DemandIntelligence,
    competitive: CompetitiveIntelligence,
    ai: AIVisibilityIntelligence,
) -> ExternalIntelligence:
    raw = _chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": EXTERNAL_INTELLIGENCE_PROMPT.format(
                firmenname=profile.firmenname,
                demand_summary=f"{demand.sichtbarkeit}\n{demand.nachfragepotenziale}\n{demand.unbesetzte_themen}",
                competitive_summary=f"{competitive.staerkste_wettbewerber}\n{competitive.themen_dominanz}",
                ai_summary=f"{ai.marke_in_ai_genannt}\n{ai.wettbewerber_in_ai}\n{ai.themen_mit_ai_sichtbarkeit}",
            )},
        ],
        temperature=0.4,
    )
    schema = """{
  "demand_signals": "...", "competitive_signals": "...", "ai_visibility_summary": "...",
  "chancen": "...", "risiken": "..."
}"""
    return ExternalIntelligence(**_parse_json(raw, schema))


def build_executive_summary(
    profile: CompanyProfile,
    strategy: StrategicAnalysis,
    scoring: Scoring,
    external: ExternalIntelligence,
) -> ExecutiveSummary:
    full = f"""
Leistungen: {strategy.leistungen}
Zielgruppe: {strategy.zielgruppe}
Positionierung: {strategy.klarheit_positionierung}
Chancen: {external.chancen}
Risiken: {external.risiken}
Demand Signals: {external.demand_signals}
Competitive Signals: {external.competitive_signals}
AI Visibility: {external.ai_visibility_summary}
"""
    raw = _chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": EXECUTIVE_SUMMARY_PROMPT.format(
                firmenname=profile.firmenname,
                branche=profile.branche,
                full_summary=full,
                positionierung_score=scoring.positionierung_score,
                demand_score=scoring.demand_score,
                competitive_score=scoring.competitive_score,
                ai_visibility_score=scoring.ai_visibility_score,
                gesamt_score=scoring.gesamt_score,
            )},
        ],
        json_mode=True,
        temperature=0.4,
    )
    data = json.loads(raw)
    bullets = data.get("bullets", [])[:10]
    return ExecutiveSummary(bullets=bullets)


# ---------------------------------------------------------------------------
# Haupt-Pipeline
# ---------------------------------------------------------------------------

def run_full_analysis(
    profile: CompanyProfile,
    scraped: dict,
    extra_sources: dict | None = None,
    progress_callback=None,
) -> dict:
    """Führt alle Analysen durch und gibt ein vollständiges Ergebnis zurück."""
    extra = extra_sources or {}

    def _cb(msg):
        if progress_callback:
            progress_callback(msg)

    # Strategische Analyse
    _cb("🧠 Strategische Basisanalyse...")
    strategy = analyze_strategy(profile, scraped, extra)

    # Intelligence-Module parallel
    _cb("📊 Intelligence-Module werden parallel analysiert...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f_demand = executor.submit(analyze_demand, profile, extra)
        f_competitive = executor.submit(analyze_competitive, profile, extra)
        f_ai = executor.submit(analyze_ai_visibility, profile)

        demand = f_demand.result()
        _cb("  ✅ Demand Intelligence abgeschlossen")
        competitive = f_competitive.result()
        _cb("  ✅ Competitive Intelligence abgeschlossen")
        ai = f_ai.result()
        _cb("  ✅ AI Visibility Intelligence abgeschlossen")

    # Scoring
    _cb("🏆 Scoring wird berechnet...")
    scoring = build_scoring(strategy, demand, competitive, ai)

    # External Intelligence
    _cb("🌐 External Intelligence wird zusammengefasst...")
    external = build_external_intelligence(profile, demand, competitive, ai)

    # Executive Summary
    _cb("📋 Executive Summary wird erstellt...")
    executive = build_executive_summary(profile, strategy, scoring, external)

    return {
        "strategy": strategy,
        "demand": demand,
        "competitive": competitive,
        "ai_visibility": ai,
        "scoring": scoring,
        "external": external,
        "executive": executive,
    }
