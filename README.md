<div align="center">

# 🔍 CIPHER

### Criminal Intelligence & Pattern-Hunting Engine

**An AI-powered investigation-support and criminal network analysis platform**

Built for **Smart India Hackathon 2026** — Problem Statement **SIH26189**
*AI-Powered Criminal Network Analysis System*

*Connect the records. Discover the relationships. Follow the evidence.*

</div>

---

## Table of Contents

- [Problem Statement](#-problem-statement)
- [CIPHER's Approach](#-ciphers-approach)
- [Architecture](#️-architecture)
- [Data Ingestion](#1-data-ingestion)
- [Synthetic Crime Simulation](#2-synthetic-crime-simulation)
- [Simulated Criminal Networks](#3-simulated-criminal-networks)
- [Knowledge Graph](#4-knowledge-graph)
- [Intelligence Reports & NLP](#5-intelligence-reports--nlp)
- [Entity Resolution](#6-entity-resolution)
- [Network Intelligence](#7-network-intelligence)
- [Community Detection](#8-community-detection)
- [Bridge Analysis](#9-bridge-analysis)
- [Communication Anomaly Detection](#10-communication-anomaly-detection)
- [Financial Anomaly Detection](#11-financial-anomaly-detection)
- [Circular Transaction Detection](#12-circular-transaction-detection)
- [Transaction Layering Detection](#13-transaction-layering-detection)
- [Cross-Source Intelligence](#14-cross-source-intelligence)
- [Investigation Priority Score](#15-investigation-priority-score)
- [Evidence Layer](#16-evidence-layer)
- [Investigation Timeline](#17-investigation-timeline)
- [Location Footprint](#18-location-footprint)
- [Investigation Dashboard](#19-investigation-dashboard)
- [Analytics → Dashboard Data Contract](#20-analytics--dashboard-data-contract)
- [FastAPI Backend](#21-fastapi-backend)
- [Technology Stack](#22-technology-stack)
- [Project Structure](#23-project-structure)
- [Evaluation & Ground Truth](#24-evaluation--ground-truth)
- [Current Results](#25-current-results)
- [Roadmap](#26-roadmap)
- [Why CIPHER?](#27-why-cipher)

---

## 🚔 Problem Statement

| | |
|---|---|
| **Problem Statement ID** | SIH26189 |
| **Title** | AI-Powered Criminal Network Analysis System |
| **Event** | Smart India Hackathon 2026 |

### Background

Modern criminal activities are increasingly organized and interconnected. Criminals often operate through networks involving associates, intermediaries, financial channels, communication links, locations, and events.

Law enforcement agencies collect large volumes of data from sources such as:

- FIRs and police reports
- Call Detail Records (CDRs)
- Financial transaction records
- Surveillance reports
- Social media intelligence
- Criminal history databases
- Intelligence agency reports

Despite having access to this information, investigators frequently face challenges in identifying hidden relationships among suspects because the data is fragmented, unstructured, and distributed across multiple systems. Manual analysis can be slow, labor-intensive, and prone to missing critical connections.

With advances in **AI, Machine Learning, Natural Language Processing (NLP), and Graph Analytics**, it is possible to automatically discover relationships, detect patterns, and generate insights that assist investigators in understanding criminal networks more effectively.

### Description

The objective is to develop an AI-powered system that can analyze large volumes of criminal and intelligence-related data to uncover hidden networks and relationships among **individuals, organizations, locations, and events**.

The system should:

- Collect and process data from multiple sources
- Extract important entities such as people, locations, vehicles, phone numbers, and organizations
- Build relationship maps showing how different entities are connected
- Identify key individuals who play influential roles within criminal networks
- Detect suspicious patterns and unusual activities
- Assist investigators with visual and analytical insights

### Expected Solution

> Develop an AI-powered system that automatically analyzes structured and unstructured crime-related data to uncover criminal networks, identify key influencers, detect suspicious patterns, and provide actionable intelligence for investigators.

---

## 🧠 CIPHER's Approach

The central idea behind CIPHER is simple:

> Investigative information becomes more useful when relationships between records can be analyzed together rather than examined independently.

A CDR record may not mean much by itself. A transaction may not mean much by itself. A vehicle sighting may not mean much by itself. An intelligence report may contain only a partial reference.

But when these records are connected:

```
Person
  │
  ├── calls ──────────► Person
  │
  ├── owns ───────────► Vehicle
  │
  ├── transfers ──────► Person
  │
  ├── seen at ────────► Location
  │
  └── mentioned in ───► Intelligence Report
```

...the combined network can reveal relationships and patterns that are difficult to identify through isolated records.

---

## 🏗️ Architecture

```
                    CIPHER
                      │
        ┌─────────────┴─────────────┐
        │                           │
   DATA LAYER                  INTELLIGENCE
        │                           │
        ↓                           ↓
  9 CSV sources                 NLP / NER
        │                           │
        └─────────────┬─────────────┘
                      ↓
              KNOWLEDGE GRAPH
                      │
        ┌─────────────┼──────────────┐
        ↓             ↓              ↓
   Network        Anomaly         Pattern
   Analysis       Detection       Detection
        │             │              │
        └─────────────┼──────────────┘
                      ↓
             INVESTIGATION
               PRIORITY
                 SCORE
                      │
              ┌───────┴───────┐
              ↓               ↓
           Evidence        Timeline
              │               │
              └───────┬───────┘
                      ↓
              FASTAPI BACKEND
                      │
                      ↓
              REACT DASHBOARD
```

---

## 1. Data Ingestion

CIPHER currently consumes multiple sources of investigative information: **persons, call detail records, financial transactions, vehicles, vehicle sightings, incidents, intelligence reports, locations, and organizations.**

A separate `ground_truth.csv` is maintained for evaluation and is **not** provided to the detection pipeline.

| Dataset | Records |
|---|---:|
| Persons | 150 |
| CDR | 1,658 |
| Transactions | 706 |
| Vehicles | 100 |
| Sightings | 303 |
| Incidents | 102 |
| Intelligence Reports | 50 |
| Locations | 20 |
| Organizations | 10 |

This allows the system to work across several different types of investigative evidence rather than relying on a single dataset.

---

## 2. Synthetic Crime Simulation

### Why synthetic data?

Real criminal intelligence contains highly sensitive information and cannot be freely used for development, experimentation, or public demonstrations.

CIPHER therefore uses a **synthetically generated investigative environment**. The objective is not to create random fake records — the dataset is designed to simulate the structure and behavior of a realistic investigation while maintaining complete control over the underlying ground truth.

This allows the team to:

- Develop without exposing real personal information
- Reproduce the same scenarios during testing
- Deliberately introduce known network structures
- Test detection algorithms against known outcomes
- Measure precision, recall, and F1-score
- Demonstrate the system safely

### How the synthetic data is generated

**Step 1 — Generate entities**
A synthetic population is created containing persons, vehicles, locations, organizations, and incidents. Each entity receives a unique identifier (e.g. `P001`, `P002`, ... `P150`).

**Step 2 — Create normal relationships**
Baseline relationships are generated: `Person → Person`, `Person → Vehicle`, `Person → Location`, `Person → Incident`, `Person → Organization`.

**Step 3 — Generate activity**
Activity records are generated around these entities: calls, transactions, vehicle sightings, incidents, and intelligence reports — producing a connected synthetic investigation environment.

**Step 4 — Inject investigative scenarios**
Specific patterns are deliberately introduced, including:

- Multiple synthetic criminal networks
- Bridge individuals
- Communication spikes
- Circular transaction flows
- Transaction layering
- Aliases
- Unstructured intelligence references
- Cross-source relationships

These planted scenarios provide known ground truth against which CIPHER can be evaluated.

---

## 3. Simulated Criminal Networks

The synthetic dataset contains **five deliberately constructed network structures**, each with different relationships and activity patterns. For example:

```
          Network A
       P01 ─── P02
       │ \     / │
       │  P03   │
       │   │    │
       P04 ─── P05
```

The purpose is to simulate groups of individuals with stronger internal connectivity. These networks are combined with additional entities and relationships so that the system must **discover** their structure rather than simply being told which people belong to which group.

---

## 4. Knowledge Graph

CIPHER uses a **NetworkX `MultiDiGraph`** as its central relationship model.

**Entity types:** `Person`, `Vehicle`, `Location`, `Incident`, `Report`

**Relationship types:** `OWNS`, `CALLED`, `TRANSFERRED`, `SEEN_AT`, `MENTIONED_IN`

The graph currently contains approximately:

| Metric | Value |
|---|---:|
| Nodes | 372 |
| Edges | 2,971 |

The use of a multi-directed graph allows different relationship types to exist between the same entities:

```
P001 ──CALLED──────► P007
P001 ──TRANSFERRED► P007
```

These represent two distinct investigative relationships.

---

## 5. Intelligence Reports & NLP

Not all investigative information is structured. CIPHER incorporates intelligence reports as part of the graph. Reports can contain references to people, aliases, locations, events, and other entities.

The NLP layer identifies these references and attempts to connect them to entities already present in the structured datasets:

```
"Arjun, also known as AJ, was seen near..."
                         │
                         ▼
                  Entity Resolution
                         │
                         ▼
                       P001
```

Reports become graph entities themselves:

```
Person ─────MENTIONED_IN─────► Report
Location ─────────────────────► Report
```

Associated evidence retains: **Report ID, date, source, extracted entity, match type, confidence, report text** — creating a bridge between unstructured intelligence and structured network data.

---

## 6. Entity Resolution

Different sources may refer to the same person using different identifiers, names, or aliases. CIPHER builds a resolver from the structured entity data.

For example, `P001`, `Arjun Mehta`, `Arjun`, and `AJ` can all be resolved to a single canonical entity.

The system records `entity_id`, `match_type`, and `confidence` for every match — preventing the same individual from being treated as several unrelated entities.

---

## 7. Network Intelligence

Once the knowledge graph has been constructed, CIPHER analyzes its structure using three core metrics:

| Metric | Description |
|---|---|
| **Degree Centrality** | How connected an entity is within the network — a highly connected entity may function as a hub |
| **Betweenness Centrality** | How frequently an entity lies on paths between other entities — useful for identifying intermediaries and bridge individuals |
| **PageRank** | Structural importance based on an entity's connections and the importance of connected entities |

These metrics combine into the **Influence Score**:

| Component | Weight |
|---|---:|
| Degree Centrality | 30% |
| Betweenness Centrality | 40% |
| PageRank | 30% |

> The influence score represents **structural importance** within the observed network, not criminality.

---

## 8. Community Detection

Criminal networks may consist of several interconnected groups rather than a single network. CIPHER identifies communities within the person-level network using **Greedy Modularity Community Detection** (Louvain community detection is under evaluation as a potential improvement).

```
          NETWORK
             │
     ┌───────┼───────┐
     ▼       ▼       ▼
 Community Community Community
     A        B        C
```

Community information can then be combined with centrality and behavioral analysis.

---

## 9. Bridge Analysis

A highly connected person is not necessarily the most strategically important person. An individual connecting two otherwise separate communities can be particularly significant to understanding the network.

```
Community A
P01 ── P02 ── P03
          │
         P50
          │
P21 ── P22 ── P23
Community B
```

CIPHER calculates a **Bridge Score** using:

| Component | Weight |
|---|---:|
| Betweenness | 70% |
| Cross-community connectivity | 30% |

This allows the system to identify potential intermediaries between network communities.

---

## 10. Communication Anomaly Detection

CIPHER analyzes Call Detail Records over time. For each person, activity is aggregated by day using **calls per day, unique contacts, and total call duration**. Statistical analysis then identifies unusually intense periods of communication.

```
Normal activity:
▂ ▃ ▂ ▃ ▂ ▂ ▃

Unusual activity:
▂ ▃ ▂ █ █ █ █ ▂
```

The strongest detected deviation contributes to the person's `communication_anomaly` score. The synthetic dataset includes a deliberately introduced communication spike so this detector can be evaluated.

---

## 11. Financial Anomaly Detection

CIPHER analyzes transaction behavior using **transaction count, total transaction amount, and unique counterparties**. The resulting activity is analyzed to identify unusually strong financial behavior, generating a normalized financial anomaly signal that contributes to the overall investigation-priority calculation.

---

## 12. Circular Transaction Detection

CIPHER contains explicit detection for circular transaction structures:

```
A ─────► B          or:    A → B → C → A
▲        │
│        ▼
└────────C
```

Transactions are examined within a defined time window and compared based on their amounts. Detected cycles are preserved as analytical evidence. The synthetic dataset deliberately contains circular transaction scenarios for evaluation.

---

## 13. Transaction Layering Detection

CIPHER also searches for multi-hop transaction chains:

```
A → B → C → D
```

Detection logic considers:

- High transaction amounts
- Rapid movement of funds
- Multiple intermediaries
- Declining transaction values
- Temporal proximity

Detected chains contribute to `layering_chain_count` and `layering_score` — meaning CIPHER is not simply identifying "unusual money," but looking for specific transaction structures.

---

## 14. Cross-Source Intelligence

The real strength of CIPHER comes from combining these signals:

```
                    PERSON
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
 Communication      Financial       Intelligence
       │               │                │
       ▼               ▼                ▼
    CDR data       Transactions      Reports
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                  Network Context
```

A person can therefore be analyzed using information from several independent sources — this is the core idea behind CIPHER's multi-source intelligence approach.

---

## 15. Investigation Priority Score

CIPHER combines the analytical signals into an **Investigation Priority Score**:

| Component | Weight |
|---|---:|
| Network Influence | 25% |
| Communication Anomaly | 20% |
| Bridge Score | 20% |
| Financial Anomaly | 15% |
| Transaction Cycles | 10% |
| Layering | 10% |
| **Total** | **100%** |

The score answers: ***"Which entities should an investigator examine first?"***

It does **not** answer: *"Is this person a criminal?"*

> This distinction is fundamental to the system. CIPHER is designed to prioritize analytical attention, not make legal or investigative conclusions.

---

## 16. Evidence Layer

A score without an explanation is not particularly useful to an investigator. CIPHER therefore preserves supporting evidence behind analytical results.

An investigator can move from:

```
P044
  ↓
High Investigation Priority
  ↓
Why?
  ↓
Network influence → Communication anomaly → Financial relationships
  ↓
Bridge connections → Intelligence reports
  ↓
Underlying evidence
```

The system retains report-level information including **Report ID, matched entity, relationship, match type, confidence, and source text** — creating an evidence trail behind every analytical result.

---

## 17. Investigation Timeline

CIPHER generates entity-centric timelines from graph events, including `CALL`, `TRANSFERRED`, `SEEN_AT`, and `MENTIONED_IN`, with contextual information such as timestamp, counterparty, amount, duration, location, and report ID.

The current dashboard export retains the **most recent 60 events per person**, allowing investigators to examine how an entity's activity developed over time rather than viewing relationships as a static graph.

---

## 18. Location Footprint

Vehicle sightings and location relationships provide another dimension of investigation:

```
Person → Vehicle → Sighting → Location → Time
```

This allows activity to be considered alongside geographic information. The dashboard export includes location-footprint information used to visualize an entity's observed movement and associated locations.

---

## 19. Investigation Dashboard

CIPHER includes a **React-based investigator interface** providing a single environment for exploring:

- Entity rankings
- Investigation-priority scores
- Network information & communities
- Suspicious patterns
- Evidence & intelligence reports
- Timelines & location footprints
- Relationships & graph data

The frontend receives processed analytical data rather than directly operating on raw CSV files.

---

## 20. Analytics → Dashboard Data Contract

The analysis pipeline generates `dashboard/public/data/analysis.json`, which includes:

`summary` · `people` · `reports` · `patterns` · `graph_edges` · `timelines` · `location_footprint`

This creates a clear separation between:

```
RAW DATA → ANALYSIS ENGINE → ANALYSIS OUTPUT → API / DASHBOARD
```

The dashboard can also fall back to the generated JSON for offline demonstrations.

---

## 21. FastAPI Backend

CIPHER exposes the analytical system through a FastAPI backend.

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/dashboard` | Full dashboard data |
| `GET /api/entities/{person_id}` | Entity info, timeline, and evidence |
| `GET /api/patterns` | Detected suspicious patterns |
| `POST /api/reanalyse` | Re-run analysis on current CSV data without rebuilding the app |

This separates the investigation engine from the presentation layer.

---

## 22. Technology Stack

| Layer | Technologies |
|---|---|
| **Data Processing** | Python, Pandas, NumPy |
| **Graph Analysis** | NetworkX |
| **Statistical / ML** | Scikit-learn, statistical anomaly detection |
| **Text Processing** | NLP, entity extraction, entity resolution |
| **Backend** | FastAPI |
| **Frontend** | React, Vite |

---

## 23. Project Structure

```
CIPHER/
│
├── data/
│   ├── persons.csv
│   ├── cdr.csv
│   ├── transactions.csv
│   ├── vehicles.csv
│   ├── sightings.csv
│   ├── incidents.csv
│   ├── intelligence_reports.csv
│   ├── locations.csv
│   ├── organizations.csv
│   └── ground_truth.csv
│
├── src/
│   ├── main.py
│   ├── data_loader.py
│   ├── graph_builder.py
│   ├── network_analysis.py
│   ├── anomaly_detection.py
│   ├── nlp_extractor.py
│   ├── dashboard_export.py
│   └── api.py
│
├── dashboard/
│   ├── public/
│   └── src/
│
├── outputs/
│
├── requirements.txt
└── README.md
```

---

## 24. Evaluation & Ground Truth

Because the dataset is synthetically generated, CIPHER has a major advantage during development: **we know what patterns we planted.**

The ground-truth dataset is kept separate from the actual detection pipeline. This allows the team to evaluate whether the system successfully discovers:

- Synthetic criminal communities
- Bridge individuals
- Communication spikes
- Circular transaction flows
- Layering chains
- Alias relationships
- Cross-source relationships

...using metrics such as **Precision, Recall, F1-score, Detection Rate, Community Quality, and Ranking Quality**.

This makes the synthetic environment more than demonstration data — it becomes a **controlled testing environment** for the investigation engine.

---

## 25. Current Results

The current pipeline produces a knowledge graph containing approximately **372 nodes** and **2,971 edges**, and generates entity-level analytical results including influence score, community, bridge score, communication anomaly, financial anomaly, transaction pattern evidence, and investigation priority.

The engine can rank entities based on the combined signals:

```
========== TOP INFLUENTIAL ENTITIES ==========
P044    Imran Sharma       0.099686
P050    Aman Bhosale       0.076809
P090    Aman More 2        0.074987
P013    Pranav Jadhav      0.051358
...
```

> These scores are analytical network measurements and should not be interpreted as criminality probabilities.

---

## 26. Roadmap

### ✅ Implemented

- Multi-source data ingestion
- Synthetic investigative dataset & controlled crime-scenario simulation
- Ground-truth dataset
- Knowledge graph construction (MultiDiGraph relationships)
- Entity resolution
- Intelligence report extraction & evidence linking
- Degree centrality, betweenness centrality, PageRank, influence scoring
- Community detection
- Bridge analysis
- Communication anomaly detection
- Financial anomaly detection
- Circular transaction detection
- Transaction layering detection
- Investigation priority scoring
- Entity timelines
- Location footprint
- FastAPI backend
- React dashboard & data export
- Offline dashboard fallback
- Live re-analysis endpoint

### 🔬 In Development

**Better Network Intelligence**
- Evaluate Louvain against Greedy Modularity
- Improved & temporal community detection
- Dynamic network evolution
- Advanced bridge detection

**Better Entity Intelligence**
- Improved alias resolution & fuzzy entity matching
- Cross-source entity reconciliation
- Expanded NLP relationship extraction
- Improved location/entity extraction

**Better Pattern Detection**
- More complex transaction motifs
- Temporal communication patterns
- Coordinated activity detection
- Cross-community behavior analysis
- Multi-source pattern correlation

**Investigator Experience**
- Interactive graph exploration
- Advanced entity search
- Investigation workspaces & case-based analysis
- Evidence filtering
- Investigation report generation & exportable analytical reports

**Advanced Analysis**
- Graph-based machine learning
- Advanced anomaly models
- Temporal graph analysis
- More sophisticated investigation-priority models
- Automated hypothesis generation

---

## 27. Why CIPHER?

Traditional investigation workflows often require analysts to move between multiple datasets and systems:

```
CDR database → Transaction records → Vehicle records → Incident records → Intelligence reports → Manual correlation
```

CIPHER brings these relationships into one analytical environment:

```
                 CIPHER
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    Network     Activity    Evidence
    Structure   Patterns    Sources
        │          │          │
        └──────────┼──────────┘
                   ▼
          Investigation Leads
```

The goal is not to replace investigators. **The goal is to make the relationships within large volumes of investigative data easier to discover, understand, and investigate.**

---

<div align="center">

### 📜 Smart India Hackathon 2026

**Problem Statement:** SIH26189
**Title:** AI-Powered Criminal Network Analysis System

---

**CIPHER**
*Criminal Intelligence & Pattern-Hunting Engine*

*Connect the records. Discover the relationships. Follow the evidence.*

</div>