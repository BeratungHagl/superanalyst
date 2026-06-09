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
