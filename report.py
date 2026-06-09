from datetime import date
from models import CompanyProfile, StrategicAnalysis


def generate_report(profile: CompanyProfile, analysis: StrategicAnalysis) -> str:
    today = date.today().strftime("%d.%m.%Y")

    ansprechpartner = (
        "\n".join(f"  - {p}" for p in profile.ansprechpartner)
        if profile.ansprechpartner
        else "  - Nicht identifiziert"
    )

    report = f"""# Unternehmensanalyse: {profile.firmenname}
*Erstellt am {today} | Super Analyst*

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

*Dieser Report wurde automatisch auf Basis öffentlich zugänglicher Website-Inhalte erstellt.*
*Super Analyst | {today}*
"""
    return report
