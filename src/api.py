"""Live FastAPI interface for the investigator dashboard.

Run from the project root with: uvicorn api:app --app-dir src --reload
"""

import json
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

PROJECT_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DATA_FILE = PROJECT_DIR / "dashboard" / "public" / "data" / "analysis.json"

app = FastAPI(title="SIH 26189 Investigation Analytics API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["GET", "POST"], allow_headers=["*"])


def load_dashboard_data():
    if not DASHBOARD_DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="No analysis export exists. Run POST /api/reanalyse first.")
    return json.loads(DASHBOARD_DATA_FILE.read_text(encoding="utf-8"))


@app.get("/api/health")
def health():
    return {"status": "ok", "analysis_available": DASHBOARD_DATA_FILE.exists()}


@app.get("/api/dashboard")
def dashboard():
    return load_dashboard_data()


@app.get("/api/entities/{person_id}")
def entity_profile(person_id: str):
    data = load_dashboard_data()
    person_id = person_id.upper()
    entity = next((person for person in data["people"] if person["person_id"] == person_id), None)
    if entity is None:
        raise HTTPException(status_code=404, detail=f"Entity {person_id} was not found.")
    evidence = [report for report in data["reports"] if any(item["entity_id"] == person_id for item in report["evidence"])]
    return {"entity": entity, "timeline": data["timelines"].get(person_id, []), "evidence": evidence}


@app.get("/api/patterns")
def patterns():
    return load_dashboard_data()["patterns"]


@app.post("/api/reanalyse")
def reanalyse():
    """Rebuild all outputs from the currently supplied CSV files."""
    completed = subprocess.run([sys.executable, "src/main.py"], cwd=PROJECT_DIR, capture_output=True, text=True)
    if completed.returncode != 0:
        raise HTTPException(status_code=500, detail=completed.stderr[-2000:])
    data = load_dashboard_data()
    return {"message": "Analysis refreshed from current source data.", "summary": data["summary"]}
