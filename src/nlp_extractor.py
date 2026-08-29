"""Deterministic entity extraction and resolution for intelligence reports."""

import re

import pandas as pd


PERSON_ID_PATTERN = re.compile(r"\bP\d{3}\b", flags=re.IGNORECASE)


def _normalise(value):
    """Normalise text for case-insensitive deterministic matching."""
    return re.sub(r"\s+", " ", str(value).strip().casefold())


def build_entity_resolver(persons, locations):
    """Build canonical lookup tables from the structured source of truth."""
    people_by_id, person_terms = {}, {}
    for _, row in persons.iterrows():
        person_id = row["person_id"]
        people_by_id[person_id] = {"name": row["name"], "alias": row["alias"]}
        for field, confidence in (("name", 0.95), ("alias", 0.90)):
            value = row[field]
            if pd.notna(value) and str(value).strip():
                person_terms[_normalise(value)] = (person_id, field, confidence)

    locations_by_id, location_terms = {}, {}
    for _, row in locations.iterrows():
        location_id = row["location_id"]
        locations_by_id[location_id] = row["location_name"]
        location_terms[_normalise(row["location_name"])] = (location_id, 0.95)

    return {
        "people_by_id": people_by_id,
        "person_terms": person_terms,
        "locations_by_id": locations_by_id,
        "location_terms": location_terms,
    }


def extract_entities(text, resolver):
    """Extract canonical person and location mentions from one report."""
    text_normalised = _normalise(text)
    people, locations = {}, {}

    for raw_person_id in PERSON_ID_PATTERN.findall(str(text)):
        person_id = raw_person_id.upper()
        if person_id in resolver["people_by_id"]:
            people[person_id] = {
                "person_id": person_id, "matched_text": raw_person_id,
                "match_type": "person_id", "confidence": 1.0,
            }

    # Longer terms first prevents short aliases from superseding full names.
    for term, (person_id, match_type, confidence) in sorted(
        resolver["person_terms"].items(), key=lambda item: len(item[0]), reverse=True
    ):
        if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text_normalised):
            current = people.get(person_id)
            if current is None or confidence > current["confidence"]:
                people[person_id] = {
                    "person_id": person_id, "matched_text": term,
                    "match_type": match_type, "confidence": confidence,
                }
            elif current is not None and match_type not in current["match_type"].split("+"):
                current["match_type"] = f"{current['match_type']}+{match_type}"

    for term, (location_id, confidence) in resolver["location_terms"].items():
        if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text_normalised):
            locations[location_id] = {
                "location_id": location_id, "matched_text": term,
                "match_type": "location_name", "confidence": confidence,
            }
    return {"people": list(people.values()), "locations": list(locations.values())}


def process_intelligence_reports(reports, persons, locations):
    """Return evidence records for resolved report/entity relationships."""
    resolver = build_entity_resolver(persons, locations)
    results = []
    for _, row in reports.iterrows():
        entities = extract_entities(row["report_text"], resolver)
        base = {"report_id": row["report_id"], "date": row["date"]}
        for person in entities["people"]:
            results.append({
                **base, "entity_type": "person", "entity_id": person["person_id"],
                "relationship": "MENTIONED_IN", "matched_text": person["matched_text"],
                "match_type": person["match_type"], "confidence": person["confidence"],
            })

        report_location_id = row.get("location_id")
        if pd.notna(report_location_id) and report_location_id in resolver["locations_by_id"]:
            results.append({
                **base, "entity_type": "location", "entity_id": report_location_id,
                "relationship": "OCCURRED_AT",
                "matched_text": resolver["locations_by_id"][report_location_id],
                "match_type": "report_location_id", "confidence": 1.0,
            })
        for location in entities["locations"]:
            if location["location_id"] != report_location_id:
                results.append({
                    **base, "entity_type": "location", "entity_id": location["location_id"],
                    "relationship": "OCCURRED_AT", "matched_text": location["matched_text"],
                    "match_type": location["match_type"], "confidence": location["confidence"],
                })
    return pd.DataFrame(results)
