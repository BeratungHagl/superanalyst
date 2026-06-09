from datetime import date
from models import (
    CompanyProfile, StrategicAnalysis,
    DemandIntelligence, CompetitiveIntelligence, AIVisibilityIntelligence,
    Scoring, ExternalIntelligence, ExecutiveSummary,
)


def _score_bar(score: int) -> str:
    filled = "█" * score
    empty = "░" * (10 - score)
    return f"{filled}{empty} {score}/10"


def generate_report(
    profile: CompanyProfile,
    results: dict,
    extra_sources: dict | None = None,
) -> str:
    today = date.today().strftime("%d.%m.%Y")
    extra_sources = extra_sources or {}

    strategy: StrategicAnalysis = results["strategy"]
    demand: DemandIntelligence = results["demand"]
    competitive: CompetitiveIntelligence = results["competitive"]
    ai: AIVisibilityIntelligence = results["ai_visibility"]
    scoring: Scoring = results["scoring"]
    external: ExternalIntelligence = results["external"]
    executive: ExecutiveSummary = results["executive"]

    ansprechpartner = (
        "\n".join(f"  - {p}" for p in profile.ansprechpartner)
        if profile.ansprechpartner
        else "  - Nicht identifiziert"
    )

    bullets_md = "\n".join(f"- {b}" for b in executive.bullets)

    # Quellen-Status
    sources_rows = _build_sources_table(extra_sources)

    report = f"""# Unternehmensanalyse: {profile.firmenname}
*Erstellt am {today} | Super Analyst V2*

---

## Executive Summary

{bullets_md}

---

## Scoring-Übersicht

| Dimension | Score | Bewertung |
|---|---|---|
| **Positionierung** | {_score_bar(scoring.positionierung_score)} | {scoring.positionierung_begruendung} |
| **Demand** | {_score_bar(scoring.demand_score)} | {demand.demand_score_begruendung} |
| **Competitive** | {_score_bar(scoring.competitive_score)} | {competitive.competitive_score_begruendung} |
| **AI Visibility** | {_score_bar(scoring.ai_visibility_score)} | {ai.ai_visibility_score_begruendung} |
| **🏆 Gesamt** | {_score_bar(scoring.gesamt_score)} | {scoring.gesamt_begruendung} |

---

## Unternehmensprofil

| Feld | Information |
|---|---|
| **Firmenname** | {profile.firmenname} |
| **Website** | {profile.website} |
| **Branche** | {profile.branche} |
| **Standort** | {profile.standort} |
| **Unternehmensgröße** | {profile.unternehmensgroesse} |
| **Rechtsform** | {profile.rechtsform or "–"} |
| **Impressum** | {profile.impressum_url or "–"} |

### Ansprechpartner
{ansprechpartner}

---

## Datenquellen

{sources_rows}

---

## External Intelligence

### Demand Signals
{external.demand_signals}

### Competitive Signals
{external.competitive_signals}

### AI Visibility
{external.ai_visibility_summary}

### Chancen
{external.chancen}

### Risiken
{external.risiken}

---

## Demand Intelligence

### Sichtbarkeit
{demand.sichtbarkeit}

### Gefundene Themen & Keywords
{demand.gefundene_themen}

### Nachfragepotenziale
{demand.nachfragepotenziale}

### Unbesetzte Themen
{demand.unbesetzte_themen}

**Demand Score: {_score_bar(demand.demand_score)}**
*{demand.demand_score_begruendung}*

---

## Competitive Intelligence

### Stärkste Wettbewerber
{competitive.staerkste_wettbewerber}

### Themen-Dominanz
{competitive.themen_dominanz}

### Häufiger gefunden
{competitive.haeufiger_gefunden}

**Competitive Score: {_score_bar(competitive.competitive_score)}**
*{competitive.competitive_score_begruendung}*

---

## AI Visibility Intelligence

### Markennennung in AI-Systemen
{ai.marke_in_ai_genannt}

### Wettbewerber in AI-Systemen
{ai.wettbewerber_in_ai}

### Verwendete Quellen
{ai.verwendete_quellen}

### Themen mit AI-Sichtbarkeit
{ai.themen_mit_ai_sichtbarkeit}

**AI Visibility Score: {_score_bar(ai.ai_visibility_score)}**
*{ai.ai_visibility_score_begruendung}*

---

## Strategische Analyse

### 1. Unternehmen

**Was wird verkauft?**
{strategy.was_wird_verkauft}

**Leistungen**
{strategy.leistungen}

**Welche Probleme werden gelöst?**
{strategy.probleme_die_geloest_werden}

### 2. Zielgruppe

**Wahrscheinliche Zielgruppe**
{strategy.zielgruppe}

**Adressierte Kundengruppen**
{strategy.kundengruppen}

**Spezifität**
{strategy.spezifitaet_zielgruppe}

### 3. Positionierung

**Klarheit der Positionierung**
{strategy.klarheit_positionierung}

**Differenzierung**
{strategy.differenzierung}

**Kommunikationsstil**
{strategy.kommunikation_generisch_oder_konkret}

**Positionierung Score: {_score_bar(scoring.positionierung_score)}**

### 4. Leistungsversprechen

{strategy.leistungsversprechen}

*Leistungen vs. Ergebnisse: {strategy.leistungen_vs_ergebnisse}*

### 5. Wachstum

**Wachstumshemmnisse**
{strategy.wachstumshemmnisse}

**Schwachstellen**
{strategy.schwachstellen}

**Chancen**
{strategy.chancen}

---

## Beratungshypothesen

| Aspekt | Hypothese |
|---|---|
| **Ziel des Erstkontakts** | {strategy.ziel_des_kontakts} |
| **Vermutete Herausforderungen** | {strategy.vermutete_herausforderungen} |
| **Relevante Analysebereiche** | {strategy.relevante_analysebereiche} |

---

*Dieser Report wurde automatisch auf Basis öffentlich zugänglicher Daten erstellt.*
*Super Analyst V2 | {today}*
"""
    return report


def _build_sources_table(extra_sources: dict) -> str:
    sx = extra_sources.get("sistrix", {})
    si_info = f"Sichtbarkeitsindex {sx.get('sichtbarkeitsindex')} (Trend: {sx.get('trend')})" if sx.get("available") else "–"

    rows = [
        ("Northdata", "✅" if extra_sources.get("northdata", {}).get("available") else "⚠️ n.v."),
        ("Sistrix SEO", f"✅ {si_info}" if sx.get("available") else "⚠️ n.v."),
        ("Amazon", "✅" if extra_sources.get("amazon", {}).get("available") else "⚠️ n.v."),
        ("LinkedIn", "✅" if extra_sources.get("linkedin", {}).get("available") else "–"),
        ("Google News", "✅" if extra_sources.get("google", {}).get("available") else "–"),
    ]

    table = "| Quelle | Status |\n|---|---|\n"
    table += "\n".join(f"| **{name}** | {status} |" for name, status in rows)
    return table
