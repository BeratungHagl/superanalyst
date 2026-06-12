import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import concurrent.futures
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scraper import scrape_website
from analyst import extract_profile, run_full_analysis
from report import generate_report
from sources.northdata import get_northdata
from sources.sistrix import get_sistrix
from sources.amazon import get_amazon
from sources.linkedin import get_linkedin
from sources.google import get_google_news
from sources.hunter import get_hunter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _clean_url(url: str) -> str:
    # Strip BOM, zero-width spaces, and other invisible Unicode that
    # gets silently embedded when copying URLs from Excel / Word / some browsers
    return url.strip().lstrip("﻿​‌‍­")


class AnalyzeRequest(BaseModel):
    url: str
    linkedin_url: str = ""
    enable_google: bool = False

    def model_post_init(self, _):
        self.url = _clean_url(self.url)
        if self.linkedin_url:
            self.linkedin_url = _clean_url(self.linkedin_url)


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    def stream():
        try:
            extra_sources = {}

            # 1. Scraping
            yield sse("progress", {"step": "scraping", "msg": "🌐 Website wird gescrapt..."})
            scraped = scrape_website(req.url)
            pages = len(scraped.get("pages", []))
            yield sse("progress", {"step": "scraping_done", "msg": f"✅ {pages} Seite(n) gefunden"})

            # 2. Profil
            yield sse("progress", {"step": "profile", "msg": "📋 Unternehmensprofil wird extrahiert..."})
            profile = extract_profile(scraped)
            yield sse("progress", {"step": "profile_done", "msg": f"✅ {profile.firmenname} | {profile.branche} | {profile.standort}"})

            # 3. Externe Quellen parallel
            yield sse("progress", {"step": "sources", "msg": "📡 Externe Datenquellen werden abgerufen..."})

            icons = {"northdata": "🏢", "sistrix": "📈", "amazon": "🛒", "linkedin": "💼", "google": "🔎", "hunter": "👤"}

            def fetch_all():
                tasks = {
                    "northdata": lambda: get_northdata(profile.firmenname, profile.standort),
                    "sistrix": lambda: get_sistrix(req.url),
                    "amazon": lambda: get_amazon(profile.firmenname),
                    "hunter": lambda: get_hunter(req.url),
                    "linkedin": lambda: get_linkedin(profile.firmenname, req.linkedin_url) if req.linkedin_url else {"available": False},
                    "google": lambda: get_google_news(profile.firmenname) if req.enable_google else {"available": False},
                }
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
                    futures = {ex.submit(fn): key for key, fn in tasks.items()}
                    for future in concurrent.futures.as_completed(futures):
                        key = futures[future]
                        try:
                            data = future.result()
                            extra_sources[key] = data
                        except Exception as e:
                            extra_sources[key] = {"available": False, "error": str(e)}

            fetch_all()

            for key, data in extra_sources.items():
                icon = icons.get(key, "✅")
                if data.get("available"):
                    yield sse("progress", {"step": f"source_{key}", "msg": f"  {icon} {key.capitalize()} ✅"})
                else:
                    yield sse("progress", {"step": f"source_{key}", "msg": f"  ⚠️ {key.capitalize()}: nicht verfügbar"})

            # 4. Vollanalyse
            log = []
            def progress_cb(msg):
                log.append(msg)

            yield sse("progress", {"step": "analysis", "msg": "🧠 KI-Analyse läuft..."})
            results = run_full_analysis(profile, scraped, extra_sources, progress_callback=progress_cb)

            for msg in log:
                yield sse("progress", {"step": "analysis_detail", "msg": msg})

            # 5. Report
            yield sse("progress", {"step": "report", "msg": "📄 Report wird generiert..."})
            report_md = generate_report(profile, results, extra_sources)

            # Scoring für UI
            scoring = results["scoring"]
            yield sse("done", {
                "report": report_md,
                "firmenname": profile.firmenname,
                "scoring": {
                    "positionierung": scoring.positionierung_score,
                    "demand": scoring.demand_score,
                    "competitive": scoring.competitive_score,
                    "ai_visibility": scoring.ai_visibility_score,
                    "gesamt": scoring.gesamt_score,
                }
            })

        except Exception as e:
            yield sse("error", {"msg": str(e)})

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/health")
def health():
    return {"status": "ok"}
