SYSTEM_PROMPT = """Du bist ein erfahrener Strategy Analyst und M&A-Berater.
Du analysierst Unternehmenswebsites und erstellst strukturierte Ersthypothesen
für Beratungsgespräche. Deine Analysen sind präzise, kritisch und praxisorientiert.
Antworte ausschließlich auf Deutsch."""

EXTRACTION_PROMPT = """Analysiere den folgenden Website-Inhalt und extrahiere strukturierte Informationen.

Website-Inhalt:
{content}

Erstelle eine vollständige JSON-Antwort mit folgenden Feldern:

{{
  "firmenname": "Offizieller Firmenname",
  "website": "Website-URL",
  "branche": "Branche / Sektor",
  "standort": "Hauptstandort (Stadt, Land)",
  "unternehmensgroesse": "Schätzung: Micro (<10), Klein (10-49), Mittel (50-249), Groß (250+)",
  "rechtsform": "GmbH / AG / GbR etc. falls erkennbar",
  "impressum_url": "URL des Impressums falls gefunden",
  "ansprechpartner": ["Name 1", "Name 2"]
}}

Schätze fehlende Felder anhand des Kontexts. Gib nur valides JSON zurück."""

ANALYSIS_PROMPT = """Du bist Strategy Analyst. Analysiere dieses Unternehmen anhand der Website-Inhalte.

Unternehmen: {firmenname}
Website: {website}

Website-Inhalte:
{content}

Beantworte alle folgenden Fragen präzise und kritisch. Sei direkt und konkret — keine allgemeinen Phrasen.

**UNTERNEHMEN**
1. Was verkauft das Unternehmen? (Produkte/Dienstleistungen konkret benennen)
2. Welche Leistungen werden angeboten? (Vollständige Liste)
3. Welche Probleme werden für Kunden gelöst?

**ZIELGRUPPE**
4. Wer ist die wahrscheinlich angesprochene Zielgruppe?
5. Welche Kundengruppen werden adressiert?
6. Wie spezifisch ist die Zielgruppe definiert? (sehr spezifisch / mittel / generisch)

**POSITIONIERUNG**
7. Wie klar ist die Positionierung? (1-10 mit Begründung)
8. Wodurch unterscheidet sich das Unternehmen vom Wettbewerb?
9. Ist die Kommunikation generisch oder konkret? Beispiele nennen.

**LEISTUNGSVERSPRECHEN**
10. Welches Leistungsversprechen wird kommuniziert?
11. Wird eher über Leistungen oder Ergebnisse gesprochen?

**WACHSTUM & CHANCEN**
12. Wo bestehen mögliche Wachstumshemmnisse?
13. Welche Schwachstellen fallen auf?
14. Welche Chancen sind erkennbar?

**BERATUNGSHYPOTHESEN**
15. Was ist das wahrscheinliche Ziel eines Erstkontakts mit diesem Unternehmen?
16. Welche Herausforderungen hat das Unternehmen vermutlich?
17. Welche Analysebereiche sind für ein Beratungsgespräch besonders relevant?

Strukturiere deine Antwort klar nach den obigen Kategorien."""

DEMAND_INTELLIGENCE_PROMPT = """Du bist ein SEO- und Demand-Analyst. Analysiere die Nachfragesituation für dieses Unternehmen.

Unternehmen: {firmenname}
Branche: {branche}

Verfügbare Daten:
{content}

Beantworte folgende Fragen präzise auf Basis der vorliegenden Daten:

1. SICHTBARKEIT: Wie sichtbar ist das Unternehmen online? (Sistrix-Index, organische Reichweite, Markenbekanntheit)
2. GEFUNDENE THEMEN: Für welche konkreten Themen, Keywords und Suchanfragen wird das Unternehmen gefunden?
3. NACHFRAGEPOTENZIALE: Welche Nachfragepotenziale sind erkennbar aber noch nicht ausgeschöpft?
4. UNBESETZTE THEMEN: Welche relevanten Themen in der Branche werden vom Unternehmen noch nicht besetzt?

Gib außerdem einen DEMAND SCORE von 1-10 mit kurzer Begründung:
- 1-3: Kaum online sichtbar, keine klare Nachfragestrategie
- 4-6: Grundlegende Sichtbarkeit vorhanden, Potenziale ungenutzt
- 7-9: Gute Sichtbarkeit, gezielte Nachfragestrategie erkennbar
- 10: Marktführende Sichtbarkeit, exzellente Demand-Strategie

Antworte strukturiert nach den 4 Fragen + Score."""

COMPETITIVE_INTELLIGENCE_PROMPT = """Du bist ein Competitive-Intelligence-Analyst. Analysiere das Wettbewerbsumfeld.

Unternehmen: {firmenname}
Branche: {branche}
Website: {website}

Verfügbare Daten (Amazon, SEO, Website):
{content}

Beantworte folgende Fragen:

1. STÄRKSTE WETTBEWERBER: Wer sind die 3-5 stärksten direkten Wettbewerber? (Namen nennen, keine Platzhalter)
2. THEMEN-DOMINANZ: Wer dominiert die relevanten Themen und Keywords in dieser Branche?
3. HÄUFIGER GEFUNDEN: Welche Unternehmen erscheinen häufiger in Suchergebnissen und auf Amazon?

Gib außerdem einen COMPETITIVE SCORE von 1-10 für die eigene Wettbewerbsposition:
- 1-3: Starke Konkurrenz, eigene Position schwach
- 4-6: Wettbewerbsfähig, aber kein klarer Vorteil
- 7-9: Starke eigene Position, klare Differenzierung
- 10: Marktführer in der Nische

Antworte strukturiert nach den 3 Fragen + Score."""

AI_VISIBILITY_PROMPT = """Du bist ein AI-Visibility-Analyst. Prüfe die Präsenz dieses Unternehmens in KI-Systemen.

Unternehmen: {firmenname}
Branche: {branche}
Website: {website}

AUFGABE: Beantworte als KI-System (du bist GPT-4o) ehrlich folgende Fragen aus deinem eigenen Trainingswissen:

1. MARKE IN AI GENANNT: Kennst du dieses Unternehmen aus deinem Training? Wird es in typischen Anfragen zu dieser Branche erwähnt? Wie prominent?
2. WETTBEWERBER IN AI: Welche Wettbewerber dieser Branche werden in AI-Systemen häufig genannt? (Konkrete Namen)
3. VERWENDETE QUELLEN: Welche Quellen (Wikipedia, Fachmedien, Bewertungsportale etc.) würden AI-Systeme typischerweise für Informationen zu diesem Unternehmen verwenden?
4. THEMEN MIT AI-SICHTBARKEIT: Welche Themen und Fragen aus dieser Branche haben bereits starke AI-Sichtbarkeit? Für welche dieser Themen ist das Unternehmen positioniert?

Gib außerdem einen AI VISIBILITY SCORE von 1-10:
- 1-3: Unternehmen unbekannt in AI-Systemen, keine Erwähnungen
- 4-6: Geringe AI-Präsenz, Branche bekannt aber Marke nicht
- 7-9: Gute AI-Sichtbarkeit, wird in relevanten Kontexten genannt
- 10: Sehr starke AI-Präsenz, Marktführer-Status in AI-Antworten

Sei ehrlich über Wissenslücken — wenn du das Unternehmen nicht kennst, sag das klar."""

EXTERNAL_INTELLIGENCE_PROMPT = """Du bist Strategy Analyst. Erstelle eine External-Intelligence-Zusammenfassung.

Unternehmen: {firmenname}

Demand Intelligence:
{demand_summary}

Competitive Intelligence:
{competitive_summary}

AI Visibility:
{ai_summary}

Erstelle:

1. DEMAND SIGNALS: Die 3-5 wichtigsten Erkenntnisse aus der Demand-Analyse (kurze, prägnante Bullets)
2. COMPETITIVE SIGNALS: Die 3-5 wichtigsten Erkenntnisse aus der Wettbewerbsanalyse
3. AI VISIBILITY: Die 3-5 wichtigsten Erkenntnisse zur AI-Sichtbarkeit
4. CHANCEN: Konkrete Chancen die sich aus der External Intelligence ergeben (3-5 Punkte)
5. RISIKEN: Konkrete Risiken die sich abzeichnen (3-5 Punkte)

Sei prägnant und konkret. Keine allgemeinen Phrasen."""

EXECUTIVE_SUMMARY_PROMPT = """Du bist Strategy Analyst. Erstelle ein Executive Summary für einen Beratungskunden.

Unternehmen: {firmenname}
Branche: {branche}

Gesamtanalyse:
{full_summary}

Scores:
- Positionierung: {positionierung_score}/10
- Demand: {demand_score}/10
- Competitive: {competitive_score}/10
- AI Visibility: {ai_visibility_score}/10
- Gesamt: {gesamt_score}/10

Erstelle MAXIMAL 10 prägnante Bullet Points die das Wichtigste zusammenfassen.
Jeder Bullet sollte eine konkrete, handlungsrelevante Erkenntnis enthalten.
Format: Starte jeden Bullet mit einem Emoji das den Tenor signalisiert (✅ positiv, ⚠️ neutral/Achtung, 🔴 kritisch, 💡 Chance).
Gib nur die JSON-Liste zurück: {{"bullets": ["...", "..."]}}"""
