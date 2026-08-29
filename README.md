## SIH 26189 — Criminal Network Analysis System

This prototype turns structured records and intelligence reports into
evidence-backed investigation leads. It is a decision-support tool: analytical
priority scores require investigator review and are not criminality judgments.

### Run the analytics pipeline

```bash
python3 src/main.py
```

This generates entity scores, transaction-pattern evidence, and the React
dashboard dataset at `dashboard/public/data/analysis.json`.

### Run the live API and React investigator dashboard

```bash
uvicorn api:app --app-dir src --reload
```

In a second terminal:

```bash
cd dashboard
npm install
npm run dev
```

Open the local URL printed by Vite. The dashboard reads the live API at
`http://127.0.0.1:8000/api` and its **Refresh analysis** action reprocesses
the current CSV files. If the API is unavailable, it safely falls back to the
last generated JSON export for offline demos.
