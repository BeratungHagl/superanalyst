from pydantic import BaseModel
from typing import Optional


class CompanyProfile(BaseModel):
    firmenname: str
    website: str
    branche: str
    standort: str
    unternehmensgroesse: str
    rechtsform: Optional[str] = None
    impressum_url: Optional[str] = None
    ansprechpartner: Optional[list[str]] = None


class StrategicAnalysis(BaseModel):
    # Unternehmen
    was_wird_verkauft: str
    leistungen: str
    probleme_die_geloest_werden: str

    # Zielgruppe
    zielgruppe: str
    kundengruppen: str
    spezifitaet_zielgruppe: str

    # Positionierung
    klarheit_positionierung: str
    differenzierung: str
    kommunikation_generisch_oder_konkret: str

    # Leistungsversprechen
    leistungsversprechen: str
    leistungen_vs_ergebnisse: str

    # Wachstum
    wachstumshemmnisse: str
    schwachstellen: str
    chancen: str

    # Hypothesen
    ziel_des_kontakts: str
    vermutete_herausforderungen: str
    relevante_analysebereiche: str


class DemandIntelligence(BaseModel):
    sichtbarkeit: str                  # Wie sichtbar ist das Unternehmen?
    gefundene_themen: str              # Für welche Themen wird es gefunden?
    nachfragepotenziale: str           # Welche Nachfragepotenziale sind erkennbar?
    unbesetzte_themen: str             # Welche Themen werden noch nicht besetzt?
    demand_score: int                  # 1–10
    demand_score_begruendung: str


class CompetitiveIntelligence(BaseModel):
    staerkste_wettbewerber: str        # Wer sind die stärksten Wettbewerber?
    themen_dominanz: str               # Wer dominiert relevante Themen?
    haeufiger_gefunden: str            # Welche Unternehmen werden häufiger gefunden?
    competitive_score: int             # 1–10 (eigene Position vs. Wettbewerb)
    competitive_score_begruendung: str


class AIVisibilityIntelligence(BaseModel):
    marke_in_ai_genannt: str           # Wird die Marke in AI-Systemen genannt?
    wettbewerber_in_ai: str            # Welche Wettbewerber werden genannt?
    verwendete_quellen: str            # Welche Quellen werden verwendet?
    themen_mit_ai_sichtbarkeit: str    # Welche Themen besitzen bereits AI-Sichtbarkeit?
    ai_visibility_score: int           # 1–10
    ai_visibility_score_begruendung: str


class Scoring(BaseModel):
    positionierung_score: int          # 1–10
    positionierung_begruendung: str
    demand_score: int
    competitive_score: int
    ai_visibility_score: int
    gesamt_score: int                  # Gewichteter Durchschnitt
    gesamt_begruendung: str


class ExternalIntelligence(BaseModel):
    demand_signals: str                # Wichtigste Erkenntnisse Demand
    competitive_signals: str           # Wichtigste Erkenntnisse Competitive
    ai_visibility_summary: str         # Wichtigste Erkenntnisse AI Visibility
    chancen: str                       # Erkennbare Chancen
    risiken: str                       # Erkennbare Risiken


class ExecutiveSummary(BaseModel):
    bullets: list[str]                 # Max. 10 Bullet Points
