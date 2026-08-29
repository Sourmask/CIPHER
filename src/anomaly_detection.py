"""Explainable, rule-based anomaly detectors for the synthetic prototype.

The detectors use only operational source fields.  ``ground_truth.csv`` is not
read here or anywhere in the prediction pipeline.
"""

from collections import defaultdict

import numpy as np
import pandas as pd


def _scale_0_to_100(values):
    values = pd.Series(values, dtype=float).fillna(0.0)
    low, high = values.min(), values.max()
    if high == low:
        return pd.Series(0.0, index=values.index)
    return (values - low) / (high - low) * 100


def detect_communication_anomalies(cdr):
    """Score unusually intense daily communication per person using z-scores."""
    calls = cdr.copy()
    calls["date"] = pd.to_datetime(calls["timestamp"]).dt.date
    sent = calls.rename(columns={"caller_id": "person_id", "receiver_id": "contact"})
    received = calls.rename(columns={"receiver_id": "person_id", "caller_id": "contact"})
    activity = pd.concat([
        sent[["person_id", "contact", "date", "duration_sec"]],
        received[["person_id", "contact", "date", "duration_sec"]],
    ], ignore_index=True)
    daily = activity.groupby(["person_id", "date"]).agg(
        calls_per_day=("contact", "size"),
        unique_contacts=("contact", "nunique"),
        total_duration_sec=("duration_sec", "sum"),
    ).reset_index()

    for column in ("calls_per_day", "unique_contacts", "total_duration_sec"):
        std = daily[column].std(ddof=0)
        daily[f"{column}_z"] = 0.0 if std == 0 else (daily[column] - daily[column].mean()) / std
    daily["daily_anomaly"] = daily[[
        "calls_per_day_z", "unique_contacts_z", "total_duration_sec_z"
    ]].clip(lower=0).mean(axis=1)
    peak = daily.loc[daily.groupby("person_id")["daily_anomaly"].idxmax()].copy()
    peak["communication_anomaly"] = _scale_0_to_100(peak["daily_anomaly"])
    return peak[["person_id", "communication_anomaly", "date", "calls_per_day", "unique_contacts"]]


def detect_financial_anomalies(transactions):
    """Score unusual transaction volume, amount, and counterpart diversity."""
    outgoing = transactions.rename(columns={"sender_id": "person_id", "receiver_id": "counterparty"})
    incoming = transactions.rename(columns={"receiver_id": "person_id", "sender_id": "counterparty"})
    activity = pd.concat([
        outgoing[["person_id", "counterparty", "amount"]],
        incoming[["person_id", "counterparty", "amount"]],
    ], ignore_index=True)
    features = activity.groupby("person_id").agg(
        transaction_count=("amount", "size"), total_amount=("amount", "sum"),
        unique_counterparties=("counterparty", "nunique"),
    ).reset_index()
    z_columns = []
    for column in ("transaction_count", "total_amount", "unique_counterparties"):
        std = features[column].std(ddof=0)
        z_column = f"{column}_z"
        features[z_column] = 0.0 if std == 0 else (features[column] - features[column].mean()) / std
        z_columns.append(z_column)
    features["financial_anomaly"] = _scale_0_to_100(features[z_columns].clip(lower=0).mean(axis=1))
    return features[["person_id", "financial_anomaly", "transaction_count", "total_amount"]]


def detect_transaction_cycles(transactions):
    """Find three-person rapid circular transfers with comparable amounts."""
    tx = transactions.copy()
    tx["timestamp"] = pd.to_datetime(tx["timestamp"])
    by_pair = defaultdict(list)
    for _, row in tx.iterrows():
        by_pair[(row["sender_id"], row["receiver_id"])] .append(row)

    cycles, people = [], defaultdict(int)
    nodes = sorted(set(tx["sender_id"]).union(tx["receiver_id"]))
    for first in nodes:
        first_targets = {target for sender, target in by_pair if sender == first}
        for second in first_targets:
            second_targets = {target for sender, target in by_pair if sender == second}
            for third in second_targets:
                if third == first or (third, first) not in by_pair:
                    continue
                canonical = min((first, second, third), (second, third, first), (third, first, second))
                if canonical != (first, second, third):
                    continue
                candidates = [by_pair[(first, second)], by_pair[(second, third)], by_pair[(third, first)]]
                for a in candidates[0]:
                    for b in candidates[1]:
                        for c in candidates[2]:
                            rows = (a, b, c)
                            amounts = [float(row["amount"]) for row in rows]
                            duration = max(row["timestamp"] for row in rows) - min(row["timestamp"] for row in rows)
                            if duration <= pd.Timedelta(days=1) and max(amounts) / min(amounts) <= 1.15:
                                cycle = {"cycle": " -> ".join([first, second, third, first]),
                                         "timestamp": min(row["timestamp"] for row in rows).isoformat(),
                                         "amount": round(sum(amounts) / 3, 2)}
                                cycles.append(cycle)
                                for person in (first, second, third):
                                    people[person] += 1
    return pd.DataFrame(cycles), pd.DataFrame([
        {"person_id": person, "transaction_cycle_count": count, "cycle_score": 100.0}
        for person, count in people.items()
    ])


def detect_layering_chains(transactions, minimum_amount=200_000):
    """Find rapid, high-value three-hop transfer chains with declining amounts."""
    tx = transactions.copy()
    tx["timestamp"] = pd.to_datetime(tx["timestamp"])
    outgoing = defaultdict(list)
    for _, row in tx.iterrows():
        outgoing[row["sender_id"]].append(row)

    chains, people = [], defaultdict(int)
    for _, first in tx[tx["amount"] >= minimum_amount].iterrows():
        for second in outgoing[first["receiver_id"]]:
            for third in outgoing[second["receiver_id"]]:
                rows = (first, second, third)
                amounts = [float(row["amount"]) for row in rows]
                duration = max(row["timestamp"] for row in rows) - min(row["timestamp"] for row in rows)
                if (duration <= pd.Timedelta(days=1) and amounts[0] >= amounts[1] >= amounts[2]
                        and amounts[2] >= amounts[0] * 0.70):
                    path = [first["sender_id"], first["receiver_id"], second["receiver_id"], third["receiver_id"]]
                    chains.append({"chain": " -> ".join(path), "timestamp": min(
                        row["timestamp"] for row in rows).isoformat(), "initial_amount": amounts[0]})
                    for person in path:
                        people[person] += 1
    return pd.DataFrame(chains), pd.DataFrame([
        {"person_id": person, "layering_chain_count": count, "layering_score": 100.0}
        for person, count in people.items()
    ])
