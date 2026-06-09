import streamlit as st
from scraper import scrape_website
from analyst import extract_profile, analyze_strategy
from report import generate_report

st.set_page_config(
    page_title="Super Analyst",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Super Analyst")
st.caption("KI-gestützte Unternehmensanalyse — Input: Website-URL")

st.divider()

url = st.text_input(
    "Unternehmenswebsite",
    placeholder="https://www.beispiel.de",
)

start = st.button("Analyse starten", type="primary", disabled=not url)

if start and url:
    report_md = None

    with st.status("Analyse läuft...", expanded=True) as status:

        st.write("🌐 Website wird gescrapt...")
        scraped = scrape_website(url)
        pages_found = len(scraped.get("pages", []))
        st.write(f"✅ {pages_found} Seite(n) gefunden")

        st.write("📋 Unternehmensprofil wird extrahiert...")
        profile = extract_profile(scraped)
        st.write(f"✅ Profil erstellt: **{profile.firmenname}**")

        st.write("🧠 Strategische Analyse wird durchgeführt...")
        analysis = analyze_strategy(profile, scraped)
        st.write("✅ Analyse abgeschlossen")

        st.write("📄 Report wird generiert...")
        report_md = generate_report(profile, analysis)
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
