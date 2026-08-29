from pathlib import Path

from data_loader import load_data
from graph_builder import (
    add_intelligence_report_relationships,
    build_graph,
    graph_summary,
)
from nlp_extractor import process_intelligence_reports
from network_analysis import (
    calculate_bridge_scores,
    calculate_centrality,
    calculate_influence_score,
    detect_communities,
)
from anomaly_detection import (
    detect_communication_anomalies,
    detect_financial_anomalies,
    detect_layering_chains,
    detect_transaction_cycles,
)
from dashboard_export import export_dashboard_data


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def scale_0_to_100(values):
    values = values.fillna(0.0)
    if values.max() == values.min():
        return values * 0.0
    return (values - values.min()) / (values.max() - values.min()) * 100


def main():

    print("\n🚔 SIH 26189 — Criminal Network Analysis")
    print("------------------------------------------")

    # 1. Load data
    data = load_data()

    print("\n[1] Loading datasets...")
    for name, df in data.items():
        print(f"    ✓ {name}: {len(df)} records")

    # 2. Build graph
    print("\n[2] Building knowledge graph...")

    G = build_graph(
        data["persons"],
        data["cdr"],
        data["transactions"],
        data["vehicles"],
        data["sightings"],
        data["incidents"],
    )

    summary = graph_summary(G)

    print(f"    Nodes: {summary['nodes']}")
    print(f"    Edges: {summary['edges']}")
    print(f"    Persons: {summary['persons']}")
    print(f"    Vehicles: {summary['vehicles']}")
    print(f"    Locations: {summary['locations']}")
    print(f"    Incidents: {summary['incidents']}")

    # 3. Extract report entities and integrate evidence into the graph
    print("\n[3] Extracting intelligence-report entities...")
    extracted_relationships = process_intelligence_reports(
        data["intelligence_reports"], data["persons"], data["locations"]
    )
    add_intelligence_report_relationships(
        G, data["intelligence_reports"], extracted_relationships
    )
    updated_summary = graph_summary(G)
    print(f"    Extracted relationships: {len(extracted_relationships)}")
    print(f"    Graph after intelligence integration: {updated_summary['nodes']} nodes, "
          f"{updated_summary['edges']} edges, {updated_summary['reports']} reports")
    print("    Sample evidence relationships:")
    print(extracted_relationships[
        ["report_id", "entity_id", "relationship", "match_type", "confidence"]
    ].head(8).to_string(index=False))

    # 4. Network analysis
    print("\n[4] Running network analysis...")

    results = calculate_centrality(G)
    results = calculate_influence_score(results)

    # 5. Communities
    print("\n[5] Detecting communities...")

    communities = detect_communities(G)

    results["community"] = results["person_id"].map(communities)

    # 6. Explainable anomaly and bridge signals
    print("\n[6] Detecting analytical patterns...")
    communication = detect_communication_anomalies(data["cdr"])
    financial = detect_financial_anomalies(data["transactions"])
    cycles, cycle_scores = detect_transaction_cycles(data["transactions"])
    chains, layering_scores = detect_layering_chains(data["transactions"])
    bridge_scores = calculate_bridge_scores(G, communities)

    results = results.merge(
        communication[["person_id", "communication_anomaly"]], on="person_id", how="left"
    ).merge(
        financial[["person_id", "financial_anomaly"]], on="person_id", how="left"
    ).merge(
        cycle_scores[["person_id", "transaction_cycle_count", "cycle_score"]], on="person_id", how="left"
    ).merge(
        layering_scores[["person_id", "layering_chain_count", "layering_score"]], on="person_id", how="left"
    ).merge(
        bridge_scores[["person_id", "cross_community_edges", "bridge_score"]], on="person_id", how="left"
    )
    signal_columns = [
        "communication_anomaly", "financial_anomaly", "transaction_cycle_count",
        "cycle_score", "layering_chain_count", "layering_score",
        "cross_community_edges", "bridge_score",
    ]
    results[signal_columns] = results[signal_columns].fillna(0.0)
    results["network_influence"] = scale_0_to_100(results["influence_score"])
    results["investigation_priority_score"] = (
        results["network_influence"] * 0.25
        + results["communication_anomaly"] * 0.20
        + results["financial_anomaly"] * 0.15
        + results["bridge_score"] * 0.20
        + results["cycle_score"] * 0.10
        + results["layering_score"] * 0.10
    )
    results = results.sort_values("investigation_priority_score", ascending=False)
    OUTPUT_DIR.mkdir(exist_ok=True)
    cycles.to_csv(OUTPUT_DIR / "transaction_cycles.csv", index=False)
    chains.to_csv(OUTPUT_DIR / "layering_chains.csv", index=False)
    print(f"    Communication anomaly leader: {communication.loc[communication['communication_anomaly'].idxmax(), 'person_id']}")
    print(f"    Transaction cycles detected: {len(cycles)}")
    print(f"    Layering chains detected: {len(chains)}")

    # 7. Save results
    output_file = OUTPUT_DIR / "entity_scores.csv"

    results.to_csv(output_file, index=False)
    dashboard_file = export_dashboard_data(
        G, results, data["intelligence_reports"], data["locations"],
        extracted_relationships, cycles, chains
    )

    print(f"\n✓ Results saved to:")
    print(f"  {output_file}")
    print(f"  Dashboard data: {dashboard_file}")

    # 8. Display top entities
    print("\n========== TOP 10 INVESTIGATION PRIORITIES ==========\n")

    print(
        results[
            [
                "person_id",
                "name",
                "investigation_priority_score",
                "communication_anomaly",
                "bridge_score",
                "community",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\n===================================================\n")


if __name__ == "__main__":
    main()
