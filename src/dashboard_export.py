"""Create the compact JSON dataset consumed by the React investigator dashboard."""

import json
from collections import defaultdict
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DATA_FILE = PROJECT_DIR / "dashboard" / "public" / "data" / "analysis.json"


def _json_value(value):
    """Convert pandas/numpy values to JSON-safe Python values."""
    if hasattr(value, "item"):
        value = value.item()
    if value != value:  # NaN
        return None
    return value


def export_dashboard_data(G, scores, reports, locations, extracted_relationships, cycles, chains):
    """Export scores, provenance, patterns, and a person-only graph projection."""
    people = [
        {key: _json_value(value) for key, value in row.items()}
        for row in scores.to_dict(orient="records")
    ]
    report_text = reports.set_index("report_id")["report_text"].to_dict()
    evidence_by_report = defaultdict(list)
    for row in extracted_relationships.to_dict(orient="records"):
        clean_row = {key: _json_value(value) for key, value in row.items()}
        evidence_by_report[row["report_id"]].append(clean_row)

    graph_edges = defaultdict(lambda: {"count": 0, "relationships": set(), "report_ids": set()})
    timeline_events = defaultdict(list)
    for source, target, attributes in G.edges(data=True):
        relationship = attributes.get("relationship", "RELATED")
        timestamp = attributes.get("timestamp") or G.nodes[target].get("date")
        if (G.nodes[source].get("node_type") == "person" and timestamp
                and relationship in {"CALLED", "TRANSFERRED", "MENTIONED_IN"}):
            event = {
                "timestamp": str(timestamp), "relationship": relationship,
                "counterparty": target if G.nodes[target].get("node_type") == "person" else None,
                "report_id": attributes.get("report_id"),
                "amount": _json_value(attributes.get("amount")),
                "duration_sec": _json_value(attributes.get("duration")),
                "location_id": attributes.get("location"),
            }
            timeline_events[source].append(event)
            if G.nodes[target].get("node_type") == "person" and relationship in {"CALLED", "TRANSFERRED"}:
                timeline_events[target].append({**event, "counterparty": source})
        if (G.nodes[source].get("node_type") != "person"
                or G.nodes[target].get("node_type") != "person"):
            continue
        key = tuple(sorted((source, target)))
        graph_edges[key]["count"] += 1
        graph_edges[key]["relationships"].add(attributes.get("relationship", "RELATED"))
        if attributes.get("report_id"):
            graph_edges[key]["report_ids"].add(attributes["report_id"])

    location_lookup = locations.set_index("location_id")
    report_location_counts = reports["location_id"].value_counts()
    location_footprint = [
        {
            "location_id": location_id,
            "name": location_lookup.loc[location_id, "location_name"],
            "city": location_lookup.loc[location_id, "city"],
            "report_count": int(report_location_counts.get(location_id, 0)),
        }
        for location_id in location_lookup.index
        if report_location_counts.get(location_id, 0)
    ]

    payload = {
        "summary": {
            "nodes": G.number_of_nodes(), "edges": G.number_of_edges(),
            "people": len(people), "reports": len(reports),
            "cycles_detected": len(cycles), "layering_chains_detected": len(chains),
        },
        "people": people,
        "reports": [
            {"report_id": report_id, "text": text,
             "evidence": evidence_by_report.get(report_id, [])}
            for report_id, text in report_text.items()
        ],
        "patterns": {
            "transaction_cycles": cycles.to_dict(orient="records"),
            "layering_chains": chains.to_dict(orient="records"),
        },
        "graph_edges": [
            {"source": source, "target": target, "count": value["count"],
             "relationships": sorted(value["relationships"]),
             "report_ids": sorted(value["report_ids"])}
            for (source, target), value in graph_edges.items()
        ],
        "timelines": {
            person_id: sorted(events, key=lambda event: event["timestamp"], reverse=True)[:60]
            for person_id, events in timeline_events.items()
        },
        "location_footprint": sorted(
            location_footprint, key=lambda location: location["report_count"], reverse=True
        ),
    }
    DASHBOARD_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return DASHBOARD_DATA_FILE
