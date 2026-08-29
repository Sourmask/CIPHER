import networkx as nx
import pandas as pd


def build_graph(persons, cdr, transactions, vehicles, sightings, incidents):
    """
    Build a heterogeneous criminal-network graph from the
    synthetic multi-source datasets.
    """

    G = nx.MultiDiGraph()

    # -------------------------
    # PERSON NODES
    # -------------------------
    for _, row in persons.iterrows():
        G.add_node(
            row["person_id"],
            node_type="person",
            name=row["name"],
            alias=row["alias"],
            age=row["age"],
            city=row["city"],
            organization=row["organization_id"],
        )

    # -------------------------
    # VEHICLE NODES
    # -------------------------
    for _, row in vehicles.iterrows():
        G.add_node(
            row["vehicle_id"],
            node_type="vehicle",
            registration=row["registration_number"],
            vehicle_type=row["vehicle_type"],
            color=row["color"],
        )

        # Person → Vehicle
        G.add_edge(
            row["owner_id"],
            row["vehicle_id"],
            relationship="OWNS",
        )

    # -------------------------
    # LOCATION NODES
    # -------------------------
    location_ids = set(sightings["location_id"].dropna())

    for location_id in location_ids:
        G.add_node(
            location_id,
            node_type="location",
        )

    # -------------------------
    # CDR / CALL RELATIONSHIPS
    # -------------------------
    for _, row in cdr.iterrows():

        G.add_edge(
            row["caller_id"],
            row["receiver_id"],
            relationship="CALLED",
            timestamp=row["timestamp"],
            duration=row["duration_sec"],
            location=row["tower_location_id"],
            pattern=row["pattern_tag"],
        )

    # -------------------------
    # FINANCIAL TRANSACTIONS
    # -------------------------
    for _, row in transactions.iterrows():

        G.add_edge(
            row["sender_id"],
            row["receiver_id"],
            relationship="TRANSFERRED",
            timestamp=row["timestamp"],
            amount=row["amount"],
            transaction_type=row["transaction_type"],
            pattern=row["pattern_tag"],
        )

    # -------------------------
    # VEHICLE SIGHTINGS
    # -------------------------
    for _, row in sightings.iterrows():

        G.add_edge(
            row["vehicle_id"],
            row["location_id"],
            relationship="SEEN_AT",
            timestamp=row["timestamp"],
            source=row["source"],
        )

    # -------------------------
    # INCIDENT RELATIONSHIPS
    # -------------------------
    for _, row in incidents.iterrows():

        incident_id = row["incident_id"]

        # Create incident node
        G.add_node(
            incident_id,
            node_type="incident",
            date=row["date"],
            crime_type=row["crime_type"],
            description=row["description"],
        )

        # Connect mentioned people to incident
        if pd.notna(row["mentioned_person_ids"]):

            people = str(row["mentioned_person_ids"]).split("|")

            for person_id in people:

                if person_id in G:
                    G.add_edge(
                        person_id,
                        incident_id,
                        relationship="MENTIONED_IN",
                    )

    return G


def graph_summary(G):
    """Return basic graph statistics."""

    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "persons": sum(
            1 for _, data in G.nodes(data=True)
            if data.get("node_type") == "person"
        ),
        "vehicles": sum(
            1 for _, data in G.nodes(data=True)
            if data.get("node_type") == "vehicle"
        ),
        "locations": sum(
            1 for _, data in G.nodes(data=True)
            if data.get("node_type") == "location"
        ),
        "incidents": sum(
            1 for _, data in G.nodes(data=True)
            if data.get("node_type") == "incident"
        ),
        "reports": sum(
            1 for _, data in G.nodes(data=True)
            if data.get("node_type") == "report"
        ),
    }


def add_intelligence_report_relationships(G, reports, extracted_relationships):
    """Add report evidence and derived co-mention associations to ``G``."""
    report_lookup = reports.set_index("report_id")
    for report_id, report in report_lookup.iterrows():
        G.add_node(
            report_id, node_type="report", date=report["date"],
            source="intelligence_reports.csv", text=report["report_text"],
        )

    mentioned_people = {}
    for _, record in extracted_relationships.iterrows():
        report_id, entity_id = record["report_id"], record["entity_id"]
        evidence = {
            "relationship": record["relationship"], "source": "intelligence_reports.csv",
            "report_id": report_id, "timestamp": record["date"],
            "confidence": float(record["confidence"]), "match_type": record["match_type"],
            "matched_text": record["matched_text"],
        }
        if record["relationship"] == "MENTIONED_IN" and entity_id in G:
            G.add_edge(entity_id, report_id, **evidence)
            mentioned_people.setdefault(report_id, []).append(entity_id)
        elif record["relationship"] == "OCCURRED_AT" and entity_id in G:
            G.add_edge(report_id, entity_id, **evidence)

    for report_id, person_ids in mentioned_people.items():
        for index, source_person in enumerate(person_ids):
            for target_person in person_ids[index + 1:]:
                G.add_edge(
                    source_person, target_person, relationship="ASSOCIATED_WITH",
                    source="intelligence_reports.csv", report_id=report_id,
                    timestamp=report_lookup.loc[report_id, "date"], confidence=0.75,
                    match_type="co_mentioned_in_report",
                )
    return G
