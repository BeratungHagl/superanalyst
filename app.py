import concurrent.futures
import streamlit as st
from scraper import scrape_website
from analyst import extract_profile, analyze_strategy
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

st.title("🔍 Super Analyst")
st.caption("KI-gestützte Unternehmensanalyse — Input: Website-URL")

st.divider()

url = st.text_input(
    "Unternehmenswebsite *",
    placeholder="https://www.beispiel.de",
)

with st.expander("⚙️ Optionale Quellen"):
    linkedin_url = st.text_input("LinkedIn-URL", placeholder="https://www.linkedin.com/company/...")
    enable_google = st.checkbox("Google News einbeziehen", value=False)

start = st.button("Analyse starten", type="primary", disabled=not url)

if start and url:
    report_md = None
    extra_sources = {}

    with st.status("Analyse läuft...", expanded=True) as status:

        # 1. Website scrapen
        st.write("🌐 Website wird gescrapt...")
        scraped = scrape_website(url)
        pages_found = len(scraped.get("pages", []))
        st.write(f"✅ {pages_found} Seite(n) gefunden")

        # 2. Profil extrahieren (brauchen wir für Northdata/Amazon)
        st.write("📋 Unternehmensprofil wird extrahiert...")
        profile = extract_profile(scraped)
        st.write(f"✅ Profil erstellt: **{profile.firmenname}**")

        # 3. Zusatzquellen parallel laden
        st.write("📡 Zusatzquellen werden abgerufen...")

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

        tasks = [fetch_northdata, fetch_sistrix, fetch_amazon, fetch_linkedin, fetch_google]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fn) for fn in tasks]
            for future in concurrent.futures.as_completed(futures):
                try:
                    key, data = future.result()
                    extra_sources[key] = data
                    icons = {"northdata": "🏢", "sistrix": "📈", "amazon": "🛒", "linkedin": "💼", "google": "🔎"}
                    if data.get("available"):
                        st.write(f"  {icons.get(key, '✅')} {key.capitalize()} geladen")
                    else:
                        err = data.get("error", "nicht verfügbar")
                        st.write(f"  ⚠️ {key.capitalize()}: {err}")
                except Exception as e:
                    st.write(f"  ❌ Fehler: {e}")

        # 4. Strategische Analyse
        st.write("🧠 Strategische Analyse wird durchgeführt...")
        analysis = analyze_strategy(profile, scraped, extra_sources)
        st.write("✅ Analyse abgeschlossen")

        # 5. Report
        st.write("📄 Report wird generiert...")
        report_md = generate_report(profile, analysis, extra_sources)
        st.write("✅ Report fertig")

        status.update(label="Analyse abgeschlossen!", state="complete")

    if report_md:
        st.divider()
        st.subheader(f"Analysereport: {profile.firmenname}")
        st.markdown(report_md)

        st.divider()
        filename = f"superanalyst_{profile.firmenname.lower().replace(' ', '_')}.md"
        st.download_button(
            label="📥 Report als Markdown herunterladen",
            data=report_md,
            file_name=filename,
            mime="text/markdown",
        )
