# Knowledge Archaeology - Phase 4: ANALYSIS

## Übersicht

Das Analyzer-Modul implementiert Phase 4 des Knowledge Archaeology Systems: **Mustererkennung im Knowledge Graph**. Es analysiert den in Phase 3 (CARTOGRAPHY) erstellten Knowledge Graph und extrahiert wertvolle Erkenntnisse durch verschiedene Analyse-Algorithmen.

## Features

### 1. Clustering (Community Detection)

Erkennt Wissens-Cluster im Graph - Gruppen von eng verbundenen Konzepten.

**Algorithmen:**
- **Louvain**: Optimierung der Modularity durch iterative Node-Zuweisung
- **Greedy Modularity**: Zusammenführen von Communities für maximalen Modularity-Gain
- **Label Propagation**: Schnelle Community-Erkennung durch Label-Propagation

**Verwendung:**
```python
from analyzer import KnowledgeAnalyzer

analyzer = KnowledgeAnalyzer(graph)
clusters = analyzer.detect_clusters(algorithm="louvain")

for cluster in clusters:
    print(f"{cluster.label}: {len(cluster.node_ids)} Nodes")
    print(f"  Kohärenz: {cluster.coherence}")
    print(f"  Zentrum: {cluster.centroid}")
```

### 2. Anomalie-Erkennung (Outlier Detection)

Identifiziert ungewöhnliche Nodes im Knowledge Graph.

**Anomalie-Typen:**
- **ISOLATED**: Vollständig isolierte Nodes
- **OUTLIER**: Statistische Ausreißer (ungewöhnlich hoher/niedriger Degree)
- **BRIDGE**: Brücken-Nodes zwischen Communities (hohe Betweenness)
- **HUB**: Ungewöhnlich gut vernetzte Nodes
- **TEMPORAL_GAP**: Nodes mit zeitlichen Lücken in ihrer Präsenz

**Verwendung:**
```python
anomalies = analyzer.detect_anomalies(method="statistical")

for anomaly in anomalies:
    print(f"{anomaly.anomaly_type.value}: {anomaly.description}")
    print(f"  Score: {anomaly.score}")
```

### 3. Zentralitäts-Analyse (Centrality Analysis)

Berechnet verschiedene Zentralitäts-Metriken für alle Nodes.

**Metriken:**
- **Degree Centrality**: Direkte Verbindungen
- **Betweenness Centrality**: Position auf kürzesten Pfaden
- **Closeness Centrality**: Durchschnittliche Distanz zu allen anderen Nodes
- **Eigenvector Centrality**: Einfluss basierend auf Einfluss der Nachbarn
- **PageRank**: Wichtigkeit basierend auf eingehenden Verbindungen

**Verwendung:**
```python
centralities = analyzer.calculate_centralities()

for metric in centralities:
    print(f"{metric.node_id}:")
    print(f"  Degree: {metric.degree_centrality}")
    print(f"  Betweenness: {metric.betweenness_centrality}")
    print(f"  Gesamt-Score: {metric.overall_score}")
```

### 4. Temporale Analyse (Temporal Analysis)

Analysiert die Evolution von Konzepten über Zeit.

**Features:**
- Timeline der Konzept-Aktivität pro Periode
- Erkennung der Entstehungsperiode
- Identifikation der Peak-Periode
- Verwandte Konzepte

**Verwendung:**
```python
evolutions = analyzer.analyze_concept_evolution()

for evolution in evolutions:
    print(f"{evolution.concept_label}:")
    print(f"  Entstehung: {evolution.emergence_period}")
    print(f"  Peak: {evolution.peak_period}")
    for period, activity in evolution.timeline:
        print(f"    {period}: {activity}")
```

### 5. Übertragungsketten (Transmission Chains)

Erkennt Pfade der Wissensübertragung durch den Graph.

**Chain-Typen:**
- **DIRECT**: Direkte Verbindung zwischen zwei Konzepten
- **MULTI_HOP**: Übertragung über mehrere Zwischenstationen
- **CROSS_DOMAIN**: Übertragung über Domänen-Grenzen hinweg
- **TEMPORAL**: Übertragung über Zeitperioden hinweg

**Verwendung:**
```python
chains = analyzer.detect_transmission_chains(min_strength=0.3)

for chain in chains:
    print(f"{chain.transmission_type.value}:")
    print(f"  {chain.start_node} -> {chain.end_node}")
    print(f"  Pfad: {' -> '.join(chain.path)}")
    print(f"  Stärke: {chain.strength}")
    print(f"  Perioden: {chain.periods_covered}")
```

## Hauptklasse: KnowledgeAnalyzer

```python
class KnowledgeAnalyzer:
    def __init__(self, graph: KnowledgeGraph):
        """
        Initialisiere den Analyzer.
        
        Args:
            graph: Der zu analysierende Knowledge Graph
        """
    
    def analyze(self, clustering_algorithm="louvain", 
                anomaly_method="statistical") -> AnalysisReport:
        """
        Führe die komplette Analyse durch.
        
        Returns:
            AnalysisReport mit allen Ergebnissen
        """
```

## AnalysisReport

Der `AnalysisReport` enthält alle Analyse-Ergebnisse:

```python
@dataclass
class AnalysisReport:
    graph_stats: Dict[str, Any]           # Graph-Statistiken
    clusters: List[Cluster]               # Gefundene Cluster
    anomalies: List[Anomaly]              # Erkannte Anomalien
    centralities: List[CentralityMetrics] # Zentralitäts-Metriken
    concept_evolutions: List[ConceptEvolution]  # Konzept-Evolutionen
    transmission_chains: List[TransmissionChain] # Übertragungsketten
    insights: List[str]                   # Automatisch generierte Erkenntnisse
```

### Export

```python
# Als Dictionary
report_dict = report.to_dict()

# Als JSON
json_str = report.to_json(indent=2)

# In Datei speichern
report.save_to_file("analysis_report.json")
```

## Convenience-Funktionen

### Schnelle Analyse

```python
from analyzer import analyze_graph

report = analyze_graph(graph, clustering_algorithm="louvain")
```

### Laden und Analysieren

```python
from analyzer import load_and_analyze

report = load_and_analyze("knowledge_graph.json")
```

## Komplettes Beispiel

```python
from cartographer import KnowledgeGraph, Node, Edge, NodeType, EdgeType, Domain
from analyzer import KnowledgeAnalyzer

# Erstelle Knowledge Graph
graph = KnowledgeGraph()

# Füge Konzepte hinzu
concepts = [
    Node(id="alchemy", label="Alchemy", node_type=NodeType.CONCEPT,
         domains={Domain.ALCHEMY}, periods={"Ancient", "Medieval"}),
    Node(id="hermeticism", label="Hermeticism", node_type=NodeType.CONCEPT,
         domains={Domain.HERMETICISM}, periods={"Ancient", "Renaissance"}),
    Node(id="kabbalah", label="Kabbalah", node_type=NodeType.CONCEPT,
         domains={Domain.KABBALAH}, periods={"Medieval", "Renaissance"}),
]

for node in concepts:
    graph.add_node(node)

# Füge Verbindungen hinzu
graph.add_edge(Edge("alchemy", "hermeticism", EdgeType.DERIVED_FROM, 0.9))
graph.add_edge(Edge("hermeticism", "kabbalah", EdgeType.INFLUENCED, 0.7))

# Analysiere
analyzer = KnowledgeAnalyzer(graph)
report = analyzer.analyze()

# Auswertung
print(f"Cluster gefunden: {len(report.clusters)}")
print(f"Anomalien erkannt: {len(report.anomalies)}")
print(f"Übertragungsketten: {len(report.transmission_chains)}")

for insight in report.insights:
    print(f"• {insight}")
```

## Algorithmen-Details

### Louvain Clustering

1. Initialisiere jede Node als eigene Community
2. Für jede Node: Verschiebe in die Community mit maximalem Modularity-Gain
3. Wiederhole bis keine Verbesserung mehr möglich
4. Erstelle Super-Nodes aus Communities und wiederhole

**Komplexität:** O(n log n)

### Modularity

Modularity misst die Qualität einer Community-Zuweisung:

```
Q = (1/2m) * Σ[Aij - (ki*kj)/(2m)] * δ(ci, cj)
```

- Aij = Verbindung zwischen i und j
- ki, kj = Degrees der Nodes
- m = Gesamtzahl der Edges
- δ(ci, cj) = 1 wenn gleiche Community

### Betweenness Centrality

Berechnet für jeden Node, wie oft er auf kürzesten Pfaden zwischen anderen Nodes liegt:

```
BC(v) = Σ(σst(v) / σst)
```

- σst = Anzahl kürzester Pfade von s nach t
- σst(v) = Anzahl dieser Pfade, die durch v gehen

### PageRank

Iterative Berechnung der Wichtigkeit:

```
PR(v) = (1-d)/N + d * Σ(PR(u)/L(u))
```

- d = Damping-Faktor (typisch 0.85)
- L(u) = Anzahl ausgehender Links von u

## Integration mit Phase 1-3

```
Phase 1 (DISCOVERY) → URLs/Quellen
        ↓
Phase 2 (EXCAVATION) → Fragmente
        ↓
Phase 3 (CARTOGRAPHY) → KnowledgeGraph
        ↓
Phase 4 (ANALYSIS) → AnalysisReport
```

### Workflow-Integration

```python
from excavator import KnowledgeExcavator
from cartographer import KnowledgeCartographer
from analyzer import KnowledgeAnalyzer

# Phase 2: Excavation
excavator = KnowledgeExcavator()
fragments = excavator.excavate(source="https://example.com/hermeticism")

# Phase 3: Cartography
cartographer = KnowledgeCartographer()
graph = cartographer.map_fragments(fragments)

# Phase 4: Analysis
analyzer = KnowledgeAnalyzer(graph)
report = analyzer.analyze()

# Speichere Ergebnisse
graph.save_to_file("knowledge_graph.json")
report.save_to_file("analysis_report.json")
```

## Tests

Das Modul enthält umfassende Unit Tests:

```bash
cd skills/knowledge_archaeology
python -m pytest test_analyzer.py -v
```

**Test-Abdeckung:**
- Cluster-Dataclass
- Anomaly-Dataclass
- CentralityMetrics
- ConceptEvolution
- TransmissionChain
- AnalysisReport
- KnowledgeAnalyzer (alle Methoden)
- Integrationstests

## Performance

| Operation | Komplexität | 100 Nodes | 1000 Nodes |
|-----------|-------------|-----------|------------|
| Clustering (Louvain) | O(n log n) | ~10ms | ~200ms |
| Anomalie-Erkennung | O(n²) | ~20ms | ~500ms |
| Centrality (alle) | O(n³) | ~50ms | ~2s |
| Temporale Analyse | O(n²) | ~15ms | ~300ms |
| Transmission Chains | O(n³) | ~100ms | ~5s |

## Erweiterungsmöglichkeiten

### Geplante Features

1. **Semantische Analyse**: NLP-basierte Konzept-Ähnlichkeit
2. **Prädiktion**: Vorhersage zukünftiger Konzept-Verbindungen
3. **Visualisierung**: Automatische Graph-Visualisierung
4. **Vergleichsanalyse**: Vergleich mehrerer Knowledge Graphen
5. **Inkrementelle Analyse**: Effiziente Re-Analyse bei Änderungen

### Custom Algorithmen

```python
class CustomAnalyzer(KnowledgeAnalyzer):
    def detect_clusters(self, algorithm="custom"):
        if algorithm == "custom":
            # Eigene Implementierung
            return self._my_clustering()
        return super().detect_clusters(algorithm)
```

## Referenzen

- **Louvain Algorithm**: Blondel et al. (2008)
- **Label Propagation**: Raghavan et al. (2007)
- **PageRank**: Page et al. (1999)
- **Betweenness Centrality**: Brandes (2001)

## Version

- **Version**: 1.0
- **Erstellt**: 2026-03-02
- **Phase**: 4 (ANALYSIS)
- **Status**: ✅ Implementiert
