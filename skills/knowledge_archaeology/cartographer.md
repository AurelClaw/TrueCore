# Knowledge Cartography System - Dokumentation

## Überblick

Das Cartography-Modul ist Phase 3 des Knowledge Archaeology Systems. Es transformiert die aus Phase 2 (Excavation) extrahierten Wissensfragmente in einen strukturierten Knowledge Graph mit Nodes (Konzepte, Entitäten) und Edges (Beziehungen).

## Architektur

### Kernkomponenten

```
┌─────────────────────────────────────────────────────────────┐
│                    KnowledgeCartographer                     │
│                         (Hauptklasse)                        │
├─────────────────────────────────────────────────────────────┤
│  Input: List[Fragment] (aus Phase 2)                        │
│  Output: KnowledgeGraph                                      │
├─────────────────────────────────────────────────────────────┤
│  1. Node-Erstellung     → Konzepte, Quellen, Perioden       │
│  2. Edge-Erstellung     → Beziehungen zwischen Nodes        │
│  3. Domänen-Klassifikation → Automatische Kategorisierung   │
│  4. Zeitschichten       → Temporale Einordnung              │
│  5. Stärken-Berechnung  → Verbindungsgewichtungen           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      KnowledgeGraph                          │
├─────────────────────────────────────────────────────────────┤
│  - Nodes: Dict[str, Node]                                    │
│  - Edges: Dict[str, Edge]                                    │
│  - Temporal Layers: Zeitschichten-Index                     │
│  - Domain Index: Domänen-Index                              │
└─────────────────────────────────────────────────────────────┘
```

## Klassen

### Node

Repräsentiert einen Knoten im Knowledge Graph.

```python
@dataclass
class Node:
    id: str                    # Eindeutige ID
    label: str                 # Anzeigename
    node_type: NodeType        # Typ (CONCEPT, ENTITY, etc.)
    properties: Dict           # Zusätzliche Eigenschaften
    domains: Set[Domain]       # Zugeordnete Domänen
    periods: Set[str]          # Zeitperioden
    confidence: float          # Zuverlässigkeit (0-1)
```

**Node-Typen:**
- `CONCEPT` - Abstrakte Konzepte (z.B. "Alchemy", "Hermeticism")
- `ENTITY` - Konkrete Entitäten (Personen, Orte, Werke)
- `DOMAIN` - Wissensdomänen
- `PERIOD` - Zeitperioden
- `SOURCE` - Quellen/Referenzen

### Edge

Repräsentiert eine Beziehung zwischen Nodes.

```python
@dataclass
class Edge:
    source: str                # Quell-Node ID
    target: str                # Ziel-Node ID
    edge_type: EdgeType        # Beziehungstyp
    weight: float              # Stärke (0-1)
    properties: Dict           # Zusätzliche Eigenschaften
    bidirectional: bool        # Bidirektional?
```

**Edge-Typen:**
- `RELATES_TO` - Allgemeine Beziehung
- `INFLUENCED` - Einfluss auf
- `DERIVED_FROM` - Abgeleitet von
- `PART_OF` - Teil von
- `MENTIONS` - Erwähnt (Quelle → Konzept)
- `BELONGS_TO` - Gehört zu
- `TEMPORAL_LINK` - Zeitliche Verbindung
- `SIMILAR_TO` - Ähnlich zu

### Domain

Wissensdomänen für die Klassifikation:

- `HERMETICISM` - Hermetik
- `ALCHEMY` - Alchemie
- `KABBALAH` - Kabbala
- `GNOSIS` - Gnosis
- `MYSTICISM` - Mystik
- `PHILOSOPHY` - Philosophie
- `ASTROLOGY` - Astrologie
- `MAGIC` - Magie
- `RELIGION` - Religion
- `SYMBOLISM` - Symbolismus
- `HISTORY` - Geschichte
- `SCIENCE` - Wissenschaft
- `UNKNOWN` - Unbekannt

### KnowledgeGraph

Die zentrale Datenstruktur für den Wissensgraphen.

#### Methoden

**Node Management:**
```python
graph.add_node(node: Node) -> str
graph.get_node(node_id: str) -> Optional[Node]
graph.has_node(node_id: str) -> bool
graph.remove_node(node_id: str) -> bool
```

**Edge Management:**
```python
graph.add_edge(edge: Edge) -> str
graph.get_edge(edge_id: str) -> Optional[Edge]
graph.get_edges_between(source_id, target_id) -> List[Edge]
graph.remove_edge_by_id(edge_id: str) -> bool
```

**Graph Queries:**
```python
graph.get_neighbors(node_id: str) -> List[Node]
graph.get_connected_nodes(node_id, edge_type) -> List[Tuple[Node, Edge]]
graph.get_nodes_by_domain(domain: Domain) -> List[Node]
graph.get_nodes_by_type(node_type: NodeType) -> List[Node]
graph.find_path(start_id, end_id, max_depth=5) -> Optional[List[Edge]]
```

**Analyse:**
```python
graph.calculate_centrality(node_id: str) -> float
graph.calculate_connection_strength(source_id, target_id) -> float
graph.get_graph_stats() -> Dict[str, Any]
```

**Serialisierung:**
```python
graph.to_dict() -> Dict[str, Any]
graph.to_json(indent=2) -> str
graph.save_to_file(filepath: str)
KnowledgeGraph.from_dict(data: Dict) -> KnowledgeGraph
KnowledgeGraph.from_json(json_str: str) -> KnowledgeGraph
KnowledgeGraph.load_from_file(filepath: str) -> KnowledgeGraph
```

### KnowledgeCartographer

Hauptklasse für die Kartographie-Phase.

#### Verwendung

```python
from cartographer import KnowledgeCartographer
from excavator import KnowledgeExcavator

# Phase 2: Fragmente extrahieren
excavator = KnowledgeExcavator()
fragments = excavator.excavate("source.txt", text)

# Phase 3: Knowledge Graph aufbauen
cartographer = KnowledgeCartographer()
graph = cartographer.map_fragments(fragments)

# Ergebnisse analysieren
print(f"Nodes: {graph.node_count}")
print(f"Edges: {graph.edge_count}")
print(f"Stats: {graph.get_graph_stats()}")
```

#### Methoden

**Hauptmethode:**
```python
cartographer.map_fragments(fragments: List[Fragment]) -> KnowledgeGraph
```

**Domänen-Analyse:**
```python
cartographer.get_domain_summary(domain: Domain) -> Dict[str, Any]
```

**Zeitliche Analyse:**
```python
cartographer.get_temporal_analysis() -> Dict[str, Any]
```

**Visualisierung:**
```python
cartographer.export_for_visualization() -> Dict[str, Any]
```

## Verwendung

### Grundlegende Verwendung

```python
from cartographer import KnowledgeCartographer, KnowledgeGraph
from excavator import KnowledgeExcavator

# Text extrahieren und kartographieren
text = """
Hermetic philosophy emerged in ancient Egypt. 
The Corpus Hermeticum contains the wisdom of Hermes Trismegistus.
During the Renaissance, Marsilio Ficino translated these texts.
Alchemy and hermeticism share deep connections.
"""

# Phase 2: Excavation
excavator = KnowledgeExcavator()
fragments = excavator.excavate("hermetic_text.txt", text)

# Phase 3: Cartography
cartographer = KnowledgeCartographer()
graph = cartographer.map_fragments(fragments)

# Graph speichern
graph.save_to_file("knowledge_graph.json")
```

### Domänen-Analyse

```python
# Analysiere Alchemie-Domäne
summary = cartographer.get_domain_summary(Domain.ALCHEMY)
print(f"Total nodes: {summary['total_nodes']}")
print(f"Central concepts: {summary['central_nodes']}")
```

### Zeitliche Analyse

```python
# Analysiere zeitliche Verteilung
temporal = cartographer.get_temporal_analysis()
for period, info in temporal['periods'].items():
    print(f"{period}: {info['node_count']} nodes")
```

### Graph-Navigation

```python
# Finde Verbindungen zwischen Konzepten
path = graph.find_path("concept_alchemy", "concept_hermeticism")
if path:
    for edge in path:
        print(f"{edge.source} --{edge.edge_type.value}--> {edge.target}")

# Nachbarn finden
neighbors = graph.get_neighbors("concept_alchemy")
for neighbor in neighbors:
    print(f"Connected to: {neighbor.label}")
```

### Verbindungsstärken

```python
# Berechne Stärke zwischen zwei Nodes
strength = graph.calculate_connection_strength("node_a", "node_b")
print(f"Connection strength: {strength:.2f}")

# Zentralität berechnen
centrality = graph.calculate_centrality("important_node")
print(f"Centrality: {centrality:.2f}")
```

## Algorithmen

### Domänen-Klassifikation

Konzepte werden automatisch Domänen zugeordnet:

```python
CONCEPT_DOMAIN_MAP = {
    "hermeticism": Domain.HERMETICISM,
    "alchemy": Domain.ALCHEMY,
    "kabbalah": Domain.KABBALAH,
    # ...
}
```

### Zeitschichten-Einordnung

Zeitperioden mit definierten Jahreszahlen:

```python
PERIOD_TIMELINE = {
    "Ancient": (None, 500),
    "Medieval": (500, 1500),
    "Renaissance": (1500, 1700),
    "Modern": (1700, None),
}
```

### Verbindungsstärken-Berechnung

Die Verbindungsstärke zwischen zwei Nodes berechnet sich aus:

1. **Direkte Verbindungen** (50% Gewichtung)
   - Summe der Edge-Gewichte
   
2. **Gemeinsame Nachbarn** (30% Gewichtung)
   - Jaccard-Ähnlichkeit der Nachbarschaften
   
3. **Domänen-Überlappung** (20% Gewichtung)
   - Gemeinsame Domänen / Alle Domänen

```
strength = (direct_edges * 0.5) + (jaccard * 0.3) + (domain_sim * 0.2)
```

### Zentralitäts-Berechnung

Degree Centrality:

```python
centrality = degree / (total_nodes - 1)
```

## Integration

Das Cartography-Modul ist Teil des Knowledge Archaeology Systems:

```
Phase 1: DISCOVERY (Quellen finden)
    ↓
Phase 2: EXCAVATION (Fragmente extrahieren)
    ↓
Phase 3: CARTOGRAPHY (dieses Modul) ← Du bist hier
    ↓
Phase 4: ANALYSIS (Muster erkennen)
    ↓
Phase 5: SYNTHESIS (Wissen synthetisieren)
    ↓
Phase 6: PUBLICATION (Ergebnisse teilen)
```

## Tests

```bash
# Alle Tests ausführen
python3 -m pytest test_cartographer.py -v

# Spezifische Test-Kategorie
python3 -m pytest test_cartographer.py::TestKnowledgeGraph -v
python3 -m pytest test_cartographer.py::TestKnowledgeCartographer -v
```

Tests umfassen:
1. Node-Erstellung und Serialisierung
2. Edge-Erstellung und Gewichtung
3. Graph-Operationen (Add/Remove)
4. Nachbar-Abfragen
5. Pfad-Findung (BFS)
6. Domänen-Filterung
7. Zeitschichten-Management
8. Zentralitäts-Berechnung
9. Verbindungsstärken
10. Integration mit Excavator

## Dateien

- `cartographer.py` - Hauptmodul (KnowledgeGraph + KnowledgeCartographer)
- `test_cartographer.py` - Unit Tests
- `cartographer.md` - Diese Dokumentation

## Erweiterung

### Neue Domäne hinzufügen

```python
# In Domain Enum
class Domain(Enum):
    # ... bestehende Domänen
    NEW_DOMAIN = "new_domain"

# In CONCEPT_DOMAIN_MAP
KnowledgeGraph.CONCEPT_DOMAIN_MAP["new_concept"] = Domain.NEW_DOMAIN
```

### Neuer Edge-Typ

```python
class EdgeType(Enum):
    # ... bestehende Typen
    CUSTOM_RELATION = "custom_relation"
```

### Neue Zeitperiode

```python
KnowledgeGraph.PERIOD_TIMELINE["NewPeriod"] = (1800, 1900)
```

## Visualisierung

Der Export für Visualisierung liefert ein Cytoscape.js-kompatibles Format:

```python
export = cartographer.export_for_visualization()

# Format:
{
    "nodes": [
        {"data": {"id": "...", "label": "...", "type": "...", "color": "..."}}
    ],
    "edges": [
        {"data": {"id": "...", "source": "...", "target": "...", "weight": ...}}
    ]
}
```

Farben werden automatisch nach Domäne zugewiesen:
- Alchemy: Orange (#FF9800)
- Hermeticism: Lila (#9C27B0)
- Mysticism: Cyan (#00BCD4)
- ...

## Performance

- Node-Lookup: O(1) durch Dictionary
- Edge-Lookup: O(1) durch Dictionary
- Nachbar-Abfrage: O(E) wobei E = Edges pro Node
- Pfad-Findung: O(V + E) mit BFS
- Speicher: ~200 Bytes pro Node, ~150 Bytes pro Edge

## Beispiel-Output

```json
{
  "nodes": [
    {
      "id": "concept_alchemy",
      "label": "Alchemy",
      "node_type": "concept",
      "domains": ["alchemy"],
      "periods": ["Medieval", "Renaissance"],
      "confidence": 1.0
    },
    {
      "id": "period_medieval",
      "label": "Medieval",
      "node_type": "period",
      "periods": ["Medieval"],
      "properties": {"start_year": 500, "end_year": 1500}
    }
  ],
  "edges": [
    {
      "source": "concept_alchemy",
      "target": "period_medieval",
      "edge_type": "temporal_link",
      "weight": 0.8
    }
  ],
  "stats": {
    "node_count": 2,
    "edge_count": 1,
    "avg_degree": 1.0
  }
}
```