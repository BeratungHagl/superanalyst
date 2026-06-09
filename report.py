from datetime import date
from models import CompanyProfile, StrategicAnalysis


def generate_report(
    profile: CompanyProfile,
    analysis: StrategicAnalysis,
    extra_sources: dict | None = None,
) -> str:
    today = date.today().strftime("%d.%m.%Y")
    extra_sources = extra_sources or {}

    ansprechpartner = (
        "\n".join(f"  - {p}" for p in profile.ansprechpartner)
        if profile.ansprechpartner
        else "  - Nicht identifiziert"
    )

    # Zusatzquellen-Abschnitt
    sources_section = _build_sources_section(extra_sources)

    report = f"""# Unternehmensanalyse: {profile.firmenname}
*Erstellt am {today} | Super Analyst V2*

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

{sources_section}

---

## 1. Unternehmen

### Was wird verkauft?
{analysis.was_wird_verkauft}

### Leistungen
{analysis.leistungen}

### Welche Probleme werden gelöst?
{analysis.probleme_die_geloest_werden}

---

## 2. Zielgruppe

### Wahrscheinliche Zielgruppe
{analysis.zielgruppe}

### Adressierte Kundengruppen
{analysis.kundengruppen}

### Spezifität der Zielgruppe
{analysis.spezifitaet_zielgruppe}

---

## 3. Positionierung

### Klarheit der Positionierung
{analysis.klarheit_positionierung}

### Differenzierung vom Wettbewerb
{analysis.differenzierung}

### Kommunikationsstil
{analysis.kommunikation_generisch_oder_konkret}

---

## 4. Leistungsversprechen

### Kommuniziertes Leistungsversprechen
{analysis.leistungsversprechen}

### Leistungen vs. Ergebnisse
{analysis.leistungen_vs_ergebnisse}

---

## 5. Wachstum & Chancen

### Mögliche Wachstumshemmnisse
{analysis.wachstumshemmnisse}

### Identifizierte Schwachstellen
{analysis.schwachstellen}

### Erkennbare Chancen
{analysis.chancen}

---

## 6. Beratungshypothesen

### Ziel des Erstkontakts (Hypothese)
{analysis.ziel_des_kontakts}

### Vermutete Herausforderungen
{analysis.vermutete_herausforderungen}

### Relevante Analysebereiche
{analysis.relevante_analysebereiche}

---

*Dieser Report wurde automatisch auf Basis öffentlich zugänglicher Daten erstellt.*
*Quellen: Website, Northdata, Sistrix, Amazon{", LinkedIn" if extra_sources.get("linkedin", {}).get("available") else ""}{", Google News" if extra_sources.get("google", {}).get("available") else ""}*
*Super Analyst V2 | {today}*
"""
    return report


def _build_sources_section(extra_sources: dict) -> str:
    lines = ["## Datenquellen\n"]

    # Northdata
    nd = extra_sources.get("northdata", {})
    lines.append(f"| **Northdata** | {'✅ Verfügbar' if nd.get('available') else '⚠️ Nicht verfügbar'} |")

    # Sistrix
    sx = extra_sources.get("sistrix", {})
    if sx.get("available"):
        si_val = sx.get("sichtbarkeitsindex", "–")
        trend = sx.get("trend", "–")
        lines.append(f"| **Sistrix SEO** | ✅ Sichtbarkeitsindex: {si_val} (Trend: {trend}) |")
        kws = sx.get("top_keywords", [])
        if kws:
            kw_str = ", ".join(f"{k['keyword']} (#{k['position']})" for k in kws[:5])
            lines.append(f"| **Top-Keywords** | {kw_str} |")
    else:
        lines.append(f"| **Sistrix SEO** | ⚠️ Nicht verfügbar |")

    # Amazon
    az = extra_sources.get("amazon", {})
    lines.append(f"| **Amazon** | {'✅ Präsenz gefunden' if az.get('available') else '⚠️ Keine Daten'} |")

    # LinkedIn
    li = extra_sources.get("linkedin", {})
    lines.append(f"| **LinkedIn** | {'✅ Profil geladen' if li.get('available') else '–'} |")

    # Google
    gn = extra_sources.get("google", {})
    lines.append(f"| **Google News** | {'✅ News gefunden' if gn.get('available') else '–'} |")

    table_header = "| Quelle | Status |\n|---|---|"
    rows = "\n".join(lines[1:])
    return f"{lines[0]}{table_header}\n{rows}"
