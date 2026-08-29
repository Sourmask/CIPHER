import networkx as nx
import pandas as pd


def _scale_0_to_100(values):
    values = pd.Series(values, dtype=float).fillna(0.0)
    if values.max() == values.min():
        return pd.Series(0.0, index=values.index)
    return (values - values.min()) / (values.max() - values.min()) * 100


def calculate_centrality(G):
    """Calculate network centrality metrics for person nodes."""

    # Use an undirected version for structural analysis
    undirected = G.to_undirected()

    degree = nx.degree_centrality(undirected)
    betweenness = nx.betweenness_centrality(undirected)
    pagerank = nx.pagerank(G)

    results = []

    for node, data in G.nodes(data=True):

        if data.get("node_type") != "person":
            continue

        results.append({
            "person_id": node,
            "name": data.get("name"),
            "degree_centrality": degree.get(node, 0),
            "betweenness_centrality": betweenness.get(node, 0),
            "pagerank": pagerank.get(node, 0),
        })

    return pd.DataFrame(results)


def calculate_influence_score(results):
    """Create a combined influence score."""

    results = results.copy()

    results["influence_score"] = (
        results["degree_centrality"] * 0.30
        + results["betweenness_centrality"] * 0.40
        + results["pagerank"] * 0.30
    )

    return results.sort_values(
        "influence_score",
        ascending=False
    )


def detect_communities(G):
    """Detect communities among person nodes."""

    person_nodes = [
        node
        for node, data in G.nodes(data=True)
        if data.get("node_type") == "person"
    ]

    subgraph = G.subgraph(person_nodes).to_undirected()

    communities = nx.community.greedy_modularity_communities(subgraph)

    community_map = {}

    for community_id, community in enumerate(communities, start=1):
        for person in community:
            community_map[person] = community_id

    return community_map


def calculate_bridge_scores(G, communities):
    """Score people that connect otherwise separate detected communities."""
    people = {
        node for node, data in G.nodes(data=True)
        if data.get("node_type") == "person"
    }
    cross_community_edges = {person: 0 for person in people}
    for source, target in G.edges():
        if (source in people and target in people and source in communities
                and target in communities and communities[source] != communities[target]):
            cross_community_edges[source] += 1
            cross_community_edges[target] += 1

    person_graph = G.subgraph(people).to_undirected()
    betweenness = nx.betweenness_centrality(person_graph)
    results = pd.DataFrame({
        "person_id": sorted(people),
        "cross_community_edges": [cross_community_edges[person] for person in sorted(people)],
        "bridge_betweenness": [betweenness.get(person, 0.0) for person in sorted(people)],
    })
    results["bridge_score"] = _scale_0_to_100(
        0.7 * results["bridge_betweenness"] + 0.3 * _scale_0_to_100(results["cross_community_edges"])
    )
    return results
