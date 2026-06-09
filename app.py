import concurrent.futures
import streamlit as st
from scraper import scrape_website
from analyst import extract_profile, run_full_analysis
from report import generate_report
from sources.northdata import get_northdata
from sources.sistrix import get_sistrix
from sources.amazon import get_amazon
from sources.linkedin import get_linkedin
from sources.google import get_google_news

st.set_page_config(
    page_title="Super Analyst",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Super Analyst V2")
st.caption("KI-gestützte Unternehmensanalyse mit Demand, Competitive & AI Visibility Intelligence")

st.divider()

url = st.text_input("Unternehmenswebsite *", placeholder="https://www.beispiel.de")

with st.expander("⚙️ Optionale Quellen"):
    linkedin_url = st.text_input("LinkedIn-URL", placeholder="https://www.linkedin.com/company/...")
    enable_google = st.checkbox("Google News einbeziehen", value=False)

start = st.button("Analyse starten", type="primary", disabled=not url)

if start and url:
    extra_sources = {}
    report_md = None

    with st.status("Analyse läuft...", expanded=True) as status:

        # 1. Website scrapen
        st.write("🌐 Website wird gescrapt...")
        scraped = scrape_website(url)
        pages_found = len(scraped.get("pages", []))
        st.write(f"✅ {pages_found} Seite(n) gefunden")

        # 2. Profil extrahieren
        st.write("📋 Unternehmensprofil wird extrahiert...")
        profile = extract_profile(scraped)
        st.write(f"✅ Profil: **{profile.firmenname}** | {profile.branche} | {profile.standort}")

        # 3. Zusatzquellen parallel
        st.write("📡 Externe Datenquellen werden abgerufen...")

        def fetch_northdata():
            return "northdata", get_northdata(profile.firmenname, profile.standort)

        def fetch_sistrix():
            return "sistrix", get_sistrix(url)

        def fetch_amazon():
            return "amazon", get_amazon(profile.firmenname)

        def fetch_linkedin():
            if linkedin_url:
                return "linkedin", get_linkedin(profile.firmenname, linkedin_url)
            return "linkedin", {"available": False}

        def fetch_google():
            if enable_google:
                return "google", get_google_news(profile.firmenname)
            return "google", {"available": False}

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fn) for fn in [fetch_northdata, fetch_sistrix, fetch_amazon, fetch_linkedin, fetch_google]]
            icons = {"northdata": "🏢", "sistrix": "📈", "amazon": "🛒", "linkedin": "💼", "google": "🔎"}
            for future in concurrent.futures.as_completed(futures):
                try:
                    key, data = future.result()
                    extra_sources[key] = data
                    if data.get("available"):
                        st.write(f"  {icons.get(key, '✅')} {key.capitalize()} ✅")
                    else:
                        st.write(f"  {icons.get(key, '⚠️')} {key.capitalize()}: nicht verfügbar")
                except Exception as e:
                    st.write(f"  ❌ Fehler: {e}")

        # 4. Vollanalyse
        log_lines = []
        def progress(msg):
            st.write(msg)
            log_lines.append(msg)

        results = run_full_analysis(profile, scraped, extra_sources, progress_callback=progress)

        # 5. Report
        st.write("📄 Report wird generiert...")
        report_md = generate_report(profile, results, extra_sources)
        st.write("✅ Fertig!")

        status.update(label="✅ Analyse abgeschlossen!", state="complete")

    if report_md:
        # Scoring-Übersicht anzeigen
        scoring = results["scoring"]
        st.divider()
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Positionierung", f"{scoring.positionierung_score}/10")
        col2.metric("Demand", f"{scoring.demand_score}/10")
        col3.metric("Competitive", f"{scoring.competitive_score}/10")
        col4.metric("AI Visibility", f"{scoring.ai_visibility_score}/10")
        col5.metric("🏆 Gesamt", f"{scoring.gesamt_score}/10")

        st.divider()
        st.subheader(f"Report: {profile.firmenname}")
        st.markdown(report_md)

        st.divider()
        filename = f"superanalyst_{profile.firmenname.lower().replace(' ', '_')}.md"
        st.download_button(
            label="📥 Report herunterladen (.md)",
            data=report_md,
            file_name=filename,
            mime="text/markdown",
        )
