# SKILL.md - knowledge_archaeology

## Purpose
Archäologie des Wissens - Ein 4-Phasen-System zur Erforschung und Analyse von Wissensdomänen.

## Phasen

### Phase 1: DISCOVERY ✅
Websuche nach obskuren Quellen und relevanten Ressourcen.

### Phase 2: EXCAVATION ✅ 
Extraktion von Wissensfragmenten aus Quellen (`excavator.py`).
- Konzept-Erkennung
- Entitäts-Extraktion
- Zeitperioden-Klassifikation

### Phase 3: CARTOGRAPHY ✅
Aufbau des Knowledge Graphs (`cartographer.py`).
- Node- und Edge-Erstellung
- Domänen-Klassifikation
- Zeitschichten-Einordnung

### Phase 4: ANALYSIS ✅
Mustererkennung im Knowledge Graph (`analyzer.py`).
- **Clustering**: Community Detection (Louvain, Greedy, Label Propagation)
- **Anomalie-Erkennung**: Outlier Detection (statistisch, isolation, distance)
- **Zentralitäts-Analyse**: Degree, Betweenness, Closeness, Eigenvector, PageRank
- **Temporale Analyse**: Konzept-Evolution über Zeit
- **Übertragungsketten**: Erkennung von Wissensflüssen

## Files
- `excavator.py` - Phase 2: Wissensfragment-Extraktion
- `cartographer.py` - Phase 3: Knowledge Graph Aufbau
- `analyzer.py` - Phase 4: Graph-Analyse
- `test_analyzer.py` - Unit Tests für Phase 4
- `analyzer.md` - Dokumentation für Phase 4

## Usage

### Phase 2-4 Workflow:
```python
from excavator import KnowledgeExcavator
from cartographer import KnowledgeCartographer
from analyzer import KnowledgeAnalyzer

# Phase 2: Excavation
excavator = KnowledgeExcavator()
fragments = excavator.excavate(source="text", content="...")

# Phase 3: Cartography
cartographer = KnowledgeCartographer()
graph = cartographer.map_fragments(fragments)

# Phase 4: Analysis
analyzer = KnowledgeAnalyzer(graph)
report = analyzer.analyze()

# Ergebnisse
print(f"Cluster: {len(report.clusters)}")
print(f"Anomalien: {len(report.anomalies)}")
print(f"Zentrale Konzepte: {len(report.centralities)}")
```

### Direkte Analyse eines gespeicherten Graphs:
```python
from analyzer import load_and_analyze

report = load_and_analyze("knowledge_graph.json")
report.save_to_file("analysis_report.json")
```

## Dependencies
- Python 3.8+
- Standard Library: dataclasses, json, math, collections

## Created
2026-03-02

## Version
1.0

## Status
✅ **Vollständig implementiert**
- Phase 1: Konzept
- Phase 2: Implementiert + Getestet
- Phase 3: Implementiert + Getestet  
- Phase 4: Implementiert + Getestet (49 Unit Tests)
