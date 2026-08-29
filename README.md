CIPHER

Criminal Intelligence & Pattern-Hunting Engine


CIPHER is an investigation-support and criminal network analysis platform developed for Smart India Hackathon 2026, addressing Problem Statement SIH26189 — AI-Powered Criminal Network Analysis System.

CIPHER combines multi-source data fusion, entity resolution, knowledge graphs, network analysis, anomaly detection, transaction-pattern detection, evidence extraction, and investigator-focused visualization to uncover relationships and patterns hidden across fragmented investigative records.

⸻

🚔 Smart India Hackathon 2026

Problem Statement ID

SIH26189

Problem Statement Title

AI-Powered Criminal Network Analysis System

Official Problem Statement

Background

Modern criminal activities are increasingly organized and interconnected. Criminals often operate through networks involving associates, intermediaries, financial channels, communication links, locations, and events.

Law enforcement agencies collect large volumes of data from sources such as:

* FIRs and police reports
* Call Detail Records (CDRs)
* Financial transaction records
* Surveillance reports
* Social media intelligence
* Criminal history databases
* Intelligence agency reports

Despite having access to this information, investigators frequently face challenges in identifying hidden relationships among suspects because the data is fragmented, unstructured, and distributed across multiple systems.

Manual analysis can be slow, labor-intensive, and prone to missing critical connections.

With advances in Artificial Intelligence (AI), Machine Learning (ML), Natural Language Processing (NLP), and Graph Analytics, it is possible to automatically discover relationships, detect patterns, and generate insights that can assist investigators in understanding criminal networks more effectively.

Description

The objective is to develop an AI-powered system that can analyze large volumes of criminal and intelligence-related data to uncover hidden networks and relationships among:

* Individuals
* Organizations
* Locations
* Events

The system should:

* Collect and process data from multiple sources.
* Extract important entities such as people, locations, vehicles, phone numbers, and organizations.
* Build relationship maps showing how different entities are connected.
* Identify key individuals who play influential roles within criminal networks.
* Detect suspicious patterns and unusual activities.
* Assist investigators by providing visual and analytical insights.

Expected Solution

Develop an AI-powered system that automatically analyzes structured and unstructured crime-related data to uncover criminal networks, identify key influencers, detect suspicious patterns, and provide actionable intelligence for investigators.

⸻

🧠 CIPHER’s Approach

The central idea behind CIPHER is simple:

Investigative information becomes more useful when relationships between records can be analyzed together rather than examined independently.

A CDR record may not mean much by itself.

A transaction may not mean much by itself.

A vehicle sighting may not mean much by itself.

An intelligence report may contain only a partial reference.

But when these records are connected:

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

the combined network can reveal relationships and patterns that are difficult to identify through isolated records.

⸻

🏗️ Current Architecture

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

⸻

1. Data Ingestion

CIPHER currently consumes multiple sources of investigative information:

* Persons
* Call Detail Records
* Financial transactions
* Vehicles
* Vehicle sightings
* Incidents
* Intelligence reports
* Locations
* Organizations

A separate ground_truth.csv is maintained for evaluation and is not provided to the detection pipeline.

The current development dataset contains:

Dataset	Records
Persons	150
CDR	1,658
Transactions	706
Vehicles	100
Sightings	303
Incidents	102
Intelligence Reports	50
Locations	20
Organizations	10

This allows the system to work across several different types of investigative evidence rather than relying on a single dataset.

⸻

2. Synthetic Crime Simulation

Why synthetic data?

Real criminal intelligence contains highly sensitive information and cannot be freely used for development, experimentation, or public demonstrations.

CIPHER therefore uses a synthetically generated investigative environment.

The objective is not to create random fake records.

Instead, the dataset is designed to simulate the structure and behavior of a realistic investigation while maintaining complete control over the underlying ground truth.

This allows us to:

* Develop without exposing real personal information.
* Reproduce the same scenarios during testing.
* Deliberately introduce known network structures.
* Test detection algorithms against known outcomes.
* Measure precision, recall, and F1-score.
* Demonstrate the system safely.

⸻

How the synthetic data is generated

The dataset is constructed in stages.

Step 1 — Generate entities

A synthetic population is created containing:

Persons
Vehicles
Locations
Organizations
Incidents

Each entity receives a unique identifier.

For example:

P001
P002
P003
...
P150

⸻

Step 2 — Create normal relationships

Relationships are generated between entities to establish a baseline network.

Examples include:

Person → Person
Person → Vehicle
Person → Location
Person → Incident
Person → Organization

⸻

Step 3 — Generate activity

Activity records are then generated around these entities:

Calls
Transactions
Vehicle sightings
Incidents
Intelligence reports

The result is a connected synthetic investigation environment.

⸻

Step 4 — Inject investigative scenarios

Specific patterns are deliberately introduced into the generated data.

These include:

* Multiple synthetic criminal networks
* Bridge individuals
* Communication spikes
* Circular transaction flows
* Transaction layering
* Aliases
* Unstructured intelligence references
* Cross-source relationships

These planted scenarios provide known ground truth against which CIPHER can be evaluated.

⸻

3. Simulated Criminal Networks

The synthetic dataset contains five deliberately constructed network structures.

Each network contains different relationships and activity patterns.

For example:

          Network A
       P01 ─── P02
       │ \     / │
       │  P03   │
       │   │    │
       P04 ─── P05

The purpose is to simulate groups of individuals with stronger internal connectivity.

The networks are then combined with additional entities and relationships so that the system must discover their structure rather than simply being told which people belong to which group.

⸻

4. Knowledge Graph

CIPHER uses a NetworkX MultiDiGraph as its central relationship model.

Current entity types include:

Person
Vehicle
Location
Incident
Report

Relationships include:

OWNS
CALLED
TRANSFERRED
SEEN_AT
MENTIONED_IN

The graph currently contains approximately:

372 Nodes
2,971 Edges

The use of a multi-directed graph allows different relationship types to exist between the same entities.

For example:

P001 ──CALLED──────► P007
P001 ──TRANSFERRED► P007

These represent two distinct investigative relationships.

⸻

5. Intelligence Reports & NLP

Not all investigative information is structured.

CIPHER therefore incorporates intelligence reports as part of the graph.

Reports can contain references to:

* People
* Aliases
* Locations
* Events
* Other entities

The NLP layer identifies these references and attempts to connect them to entities already present in the structured datasets.

For example:

"Arjun, also known as AJ, was seen near..."
                         │
                         ▼
                  Entity Resolution
                         │
                         ▼
                       P001

Reports become graph entities themselves:

Person ─────MENTIONED_IN─────► Report
Location ─────────────────────► Report

The associated evidence retains information such as:

* Report ID
* Date
* Source
* Extracted entity
* Match type
* Confidence
* Report text

This creates a bridge between unstructured intelligence and structured network data.

⸻

6. Entity Resolution

Different sources may refer to the same person using different identifiers, names, or aliases.

CIPHER builds a resolver from the structured entity data.

For example:

P001
Arjun Mehta
Arjun
AJ

can be resolved to a single canonical entity.

The system records:

entity_id
match_type
confidence

This prevents the same individual from being treated as several unrelated entities.

⸻

7. Network Intelligence

Once the knowledge graph has been constructed, CIPHER analyzes its structure.

Degree Centrality

Measures how connected an entity is within the network.

A highly connected entity may function as a hub.

Betweenness Centrality

Measures how frequently an entity lies on paths between other entities.

This is particularly useful for identifying intermediaries and bridge individuals.

PageRank

Measures structural importance based on the entity’s connections and the importance of connected entities.

These metrics are combined into the current Influence Score:

Degree Centrality        30%
Betweenness Centrality   40%
PageRank                 30%

The influence score represents structural importance within the observed network, not criminality.

⸻

8. Community Detection

Criminal networks may consist of several interconnected groups rather than a single network.

CIPHER identifies communities within the person-level network.

The current implementation uses:

Greedy Modularity Community Detection

We are also evaluating Louvain community detection as a potential improvement.

The goal is to identify structures such as:

          NETWORK
             │
     ┌───────┼───────┐
     ▼       ▼       ▼
 Community Community Community
     A        B        C

Community information can then be combined with centrality and behavioral analysis.

⸻

9. Bridge Analysis

A highly connected person is not necessarily the most strategically important person.

An individual connecting two otherwise separate communities can be particularly significant to understanding the network.

For example:

Community A
P01 ── P02 ── P03
          │
         P50
          │
P21 ── P22 ── P23
Community B

CIPHER calculates a Bridge Score using:

70% Betweenness
30% Cross-community connectivity

This allows the system to identify potential intermediaries between network communities.

⸻

10. Communication Anomaly Detection

CIPHER analyzes Call Detail Records over time.

For each person, activity is aggregated by day using:

Calls per day
Unique contacts
Total call duration

Statistical analysis is then used to identify unusually intense periods of communication.

For example:

Normal activity:
▂ ▃ ▂ ▃ ▂ ▂ ▃
Unusual activity:
▂ ▃ ▂ █ █ █ █ ▂

The strongest detected deviation contributes to the person’s:

communication_anomaly

score.

The synthetic dataset includes a deliberately introduced communication spike so that this detector can be evaluated.

⸻

11. Financial Anomaly Detection

CIPHER analyzes transaction behavior using:

Transaction count
Total transaction amount
Unique counterparties

The resulting activity is analyzed to identify unusually strong financial behavior.

The system generates a normalized financial anomaly signal that can contribute to the overall investigation-priority calculation.

⸻

12. Circular Transaction Detection

CIPHER contains explicit detection for circular transaction structures.

Example:

A ─────► B
▲        │
│        ▼
└────────C

or:

A → B → C → A

Transactions are examined within a defined time window and compared based on their amounts.

Detected cycles are preserved as analytical evidence.

The synthetic dataset deliberately contains circular transaction scenarios for evaluation.

⸻

13. Transaction Layering Detection

CIPHER also searches for multi-hop transaction chains.

Example:

A → B → C → D

The detection logic considers factors such as:

* High transaction amounts
* Rapid movement of funds
* Multiple intermediaries
* Declining transaction values
* Temporal proximity

Detected chains contribute to:

layering_chain_count
layering_score

This means CIPHER is not simply identifying “unusual money.”

It is looking for specific transaction structures.

⸻

14. Cross-Source Intelligence

The real strength of CIPHER comes from combining these signals.

For example:

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

A person can therefore be analyzed using information from several independent sources.

This is the core idea behind CIPHER’s multi-source intelligence approach.

⸻

15. Investigation Priority Score

CIPHER combines the analytical signals into an Investigation Priority Score.

The current model uses:

Network Influence       25%
Communication Anomaly   20%
Financial Anomaly       15%
Bridge Score             20%
Transaction Cycles       10%
Layering                 10%
────────────────────────────
Total                   100%

The score answers:

Which entities should an investigator examine first?

It does not answer:

“Is this person a criminal?”

This distinction is fundamental to the system.

CIPHER is designed to prioritize analytical attention, not make legal or investigative conclusions.

⸻

16. Evidence Layer

A score without an explanation is not particularly useful to an investigator.

CIPHER therefore preserves supporting evidence behind analytical results.

An investigator can move from:

P044
  ↓
High Investigation Priority
  ↓
Why?
  ↓
Network influence
  ↓
Communication anomaly
  ↓
Financial relationships
  ↓
Bridge connections
  ↓
Intelligence reports
  ↓
Underlying evidence

The system retains report-level information including:

Report ID
Matched entity
Relationship
Match type
Confidence
Source text

This creates an evidence trail behind the analytical result.

⸻

17. Investigation Timeline

CIPHER generates entity-centric timelines from graph events.

Events can include:

CALL
TRANSFERRED
SEEN_AT
MENTIONED_IN

with contextual information such as:

Timestamp
Counterparty
Amount
Duration
Location
Report ID

The current dashboard export retains the most recent 60 events per person.

This allows investigators to examine how an entity’s activity developed over time rather than viewing relationships as a static graph.

⸻

18. Location Footprint

Vehicle sightings and location relationships provide another dimension of investigation.

CIPHER connects:

Person
   ↓
Vehicle
   ↓
Sighting
   ↓
Location
   ↓
Time

This allows activity to be considered alongside geographic information.

The dashboard export includes location-footprint information that can be used to visualize an entity’s observed movement and associated locations.

⸻

19. Investigation Dashboard

CIPHER includes a React-based investigator interface.

The dashboard provides a single environment for exploring:

* Entity rankings
* Investigation-priority scores
* Network information
* Communities
* Suspicious patterns
* Evidence
* Intelligence reports
* Timelines
* Location footprints
* Relationships
* Graph data

The frontend receives processed analytical data rather than directly operating on raw CSV files.

⸻

20. Analytics → Dashboard Data Contract

The analysis pipeline generates:

dashboard/public/data/analysis.json

The generated data includes:

summary
people
reports
patterns
graph_edges
timelines
location_footprint

This creates a clear separation between:

RAW DATA
    ↓
ANALYSIS ENGINE
    ↓
ANALYSIS OUTPUT
    ↓
API / DASHBOARD

The dashboard can also fall back to the generated JSON for offline demonstrations.

⸻

21. FastAPI Backend

CIPHER exposes the analytical system through a FastAPI backend.

Current endpoints include:

GET  /api/health
GET  /api/dashboard
GET  /api/entities/{person_id}
GET  /api/patterns
POST /api/reanalyse

The entity endpoint can provide:

Entity information
Timeline
Evidence

The /api/reanalyse endpoint allows the current CSV data to be processed again without rebuilding the application.

This separates the investigation engine from the presentation layer.

⸻

22. Current Technology Stack

Data Processing

Python
Pandas
NumPy

Graph Analysis

NetworkX

Statistical / ML Components

Scikit-learn
Statistical anomaly detection

Text Processing

NLP
Entity extraction
Entity resolution

Backend

FastAPI

Frontend

React
Vite

⸻

23. Current Project Structure

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

⸻

24. Evaluation & Ground Truth

Because the dataset is synthetically generated, CIPHER has a major advantage during development:

we know what patterns we planted.

The ground-truth dataset is kept separate from the actual detection pipeline.

This allows us to evaluate whether the system successfully discovers:

* Synthetic criminal communities
* Bridge individuals
* Communication spikes
* Circular transaction flows
* Layering chains
* Alias relationships
* Cross-source relationships

using metrics such as:

Precision
Recall
F1-score
Detection Rate
Community Quality
Ranking Quality

This makes the synthetic environment more than demonstration data.

It becomes a controlled testing environment for the investigation engine.

⸻

25. Current Results

The current pipeline produces a knowledge graph containing approximately:

372 Nodes
2,971 Edges

and generates entity-level analytical results including:

Influence Score
Community
Bridge Score
Communication Anomaly
Financial Anomaly
Transaction Pattern Evidence
Investigation Priority

The engine can rank entities based on the combined signals.

Example output:

========== TOP INFLUENTIAL ENTITIES ==========
P044    Imran Sharma       0.099686
P050    Aman Bhosale       0.076809
P090    Aman More 2        0.074987
P013    Pranav Jadhav     0.051358
...

These scores are analytical network measurements and should not be interpreted as criminality probabilities.

⸻

26. Roadmap

CIPHER is being developed in stages.

✅ Implemented

* Multi-source data ingestion
* Synthetic investigative dataset
* Controlled crime-scenario simulation
* Ground-truth dataset
* Knowledge graph construction
* MultiDiGraph relationships
* Entity resolution
* Intelligence report extraction
* Evidence linking
* Degree centrality
* Betweenness centrality
* PageRank
* Influence scoring
* Community detection
* Bridge analysis
* Communication anomaly detection
* Financial anomaly detection
* Circular transaction detection
* Transaction layering detection
* Investigation priority scoring
* Entity timelines
* Location footprint
* FastAPI backend
* React dashboard
* Dashboard data export
* Offline dashboard fallback
* Live re-analysis endpoint

🔬 In Development

Better Network Intelligence

* Evaluate Louvain against Greedy Modularity
* Improved community detection
* Temporal community analysis
* Dynamic network evolution
* Advanced bridge detection

Better Entity Intelligence

* Improved alias resolution
* Fuzzy entity matching
* Cross-source entity reconciliation
* Expanded NLP relationship extraction
* Improved location/entity extraction

Better Pattern Detection

* More complex transaction motifs
* Temporal communication patterns
* Coordinated activity detection
* Cross-community behavior analysis
* Multi-source pattern correlation

Investigator Experience

* Interactive graph exploration
* Advanced entity search
* Investigation workspaces
* Case-based analysis
* Evidence filtering
* Investigation report generation
* Exportable analytical reports

Advanced Analysis

* Graph-based machine learning
* Advanced anomaly models
* Temporal graph analysis
* More sophisticated investigation-priority models
* Automated hypothesis generation

⸻

27. Why CIPHER?

Traditional investigation workflows can require analysts to move between multiple datasets and systems:

CDR database
     ↓
Transaction records
     ↓
Vehicle records
     ↓
Incident records
     ↓
Intelligence reports
     ↓
Manual correlation

CIPHER brings these relationships into one analytical environment:

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

The goal is not to replace investigators.

The goal is to make the relationships within large volumes of investigative data easier to discover, understand, and investigate.

⸻

📜 Project

Smart India Hackathon 2026

Problem Statement: SIH26189
Title: AI-Powered Criminal Network Analysis System

CIPHER

Criminal Intelligence & Pattern-Hunting Engine

Connect the records. Discover the relationships. Follow the evidence.