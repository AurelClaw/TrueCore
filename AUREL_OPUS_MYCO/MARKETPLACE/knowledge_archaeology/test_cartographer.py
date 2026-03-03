"""
Tests für das Cartographer-Modul (Phase 3: CARTOGRAPHY)

Testet Knowledge Graph Aufbau, Domänen-Klassifikation,
Zeitschichten-Einordnung und Verbindungs-Stärken.
"""

import pytest
import json
from pathlib import Path

from cartographer import (
    Node, Edge, TemporalLayer, KnowledgeGraph,
    NodeType, EdgeType, Domain,
    KnowledgeCartographer
)


# ==================== Node Tests ====================

class TestNode:
    """Tests für die Node-Klasse."""
    
    def test_node_creation(self):
        """Teste grundlegende Node-Erstellung."""
        node = Node(
            id="test_node",
            label="Test Node",
            node_type=NodeType.CONCEPT,
            domains={Domain.ALCHEMY},
            periods={"Ancient"},
            confidence=0.85
        )
        
        assert node.id == "test_node"
        assert node.label == "Test Node"
        assert node.node_type == NodeType.CONCEPT
        assert Domain.ALCHEMY in node.domains
        assert "Ancient" in node.periods
        assert node.confidence == 0.85
    
    def test_node_confidence_clamping(self):
        """Teste Confidence-Clamping auf 0-1."""
        node_high = Node(id="high", label="High", node_type=NodeType.CONCEPT, confidence=1.5)
        node_low = Node(id="low", label="Low", node_type=NodeType.CONCEPT, confidence=-0.5)
        
        assert node_high.confidence == 1.0
        assert node_low.confidence == 0.0
    
    def test_node_to_dict(self):
        """Teste Node-Serialisierung zu Dictionary."""
        node = Node(
            id="concept_alchemy",
            label="Alchemy",
            node_type=NodeType.CONCEPT,
            domains={Domain.ALCHEMY},
            periods={"Medieval", "Renaissance"},
            confidence=0.9
        )
        
        data = node.to_dict()
        
        assert data["id"] == "concept_alchemy"
        assert data["label"] == "Alchemy"
        assert data["node_type"] == "concept"
        assert "alchemy" in data["domains"]
        assert "Medieval" in data["periods"]
        assert data["confidence"] == 0.9
    
    def test_node_from_dict(self):
        """Teste Node-Deserialisierung aus Dictionary."""
        data = {
            "id": "entity_test",
            "label": "Test Entity",
            "node_type": "entity",
            "properties": {"type": "person"},
            "domains": ["hermeticism"],
            "periods": ["Ancient"],
            "confidence": 0.75
        }
        
        node = Node.from_dict(data)
        
        assert node.id == "entity_test"
        assert node.label == "Test Entity"
        assert node.node_type == NodeType.ENTITY
        assert Domain.HERMETICISM in node.domains
        assert node.confidence == 0.75


# ==================== Edge Tests ====================

class TestEdge:
    """Tests für die Edge-Klasse."""
    
    def test_edge_creation(self):
        """Teste grundlegende Edge-Erstellung."""
        edge = Edge(
            source="node_a",
            target="node_b",
            edge_type=EdgeType.RELATES_TO,
            weight=0.8,
            bidirectional=True
        )
        
        assert edge.source == "node_a"
        assert edge.target == "node_b"
        assert edge.edge_type == EdgeType.RELATES_TO
        assert edge.weight == 0.8
        assert edge.bidirectional is True
    
    def test_edge_weight_clamping(self):
        """Teste Weight-Clamping auf 0-1."""
        edge_high = Edge("a", "b", EdgeType.RELATES_TO, weight=2.0)
        edge_low = Edge("a", "b", EdgeType.RELATES_TO, weight=-0.5)
        
        assert edge_high.weight == 1.0
        assert edge_low.weight == 0.0
    
    def test_edge_id_generation(self):
        """Teste Edge-ID-Generierung."""
        edge = Edge(
            source="concept_alchemy",
            target="concept_hermeticism",
            edge_type=EdgeType.RELATES_TO
        )
        
        assert edge.id == "concept_alchemy--relates_to--concept_hermeticism"
    
    def test_edge_to_dict(self):
        """Teste Edge-Serialisierung."""
        edge = Edge(
            source="a",
            target="b",
            edge_type=EdgeType.INFLUENCED,
            weight=0.9,
            properties={"strength": "strong"}
        )
        
        data = edge.to_dict()
        
        assert data["source"] == "a"
        assert data["target"] == "b"
        assert data["edge_type"] == "influenced"
        assert data["weight"] == 0.9
        assert data["properties"]["strength"] == "strong"


# ==================== KnowledgeGraph Tests ====================

class TestKnowledgeGraph:
    """Tests für die KnowledgeGraph-Klasse."""
    
    def test_empty_graph(self):
        """Teste leeren Graph."""
        graph = KnowledgeGraph()
        
        assert graph.node_count == 0
        assert graph.edge_count == 0
        assert graph.nodes == []
        assert graph.edges == []
    
    def test_add_node(self):
        """Teste Node-Hinzufügung."""
        graph = KnowledgeGraph()
        node = Node(id="test", label="Test", node_type=NodeType.CONCEPT)
        
        node_id = graph.add_node(node)
        
        assert node_id == "test"
        assert graph.node_count == 1
        assert graph.has_node("test")
        assert graph.get_node("test").label == "Test"
    
    def test_add_edge(self):
        """Teste Edge-Hinzufügung."""
        graph = KnowledgeGraph()
        
        # Erstelle Nodes
        node_a = Node(id="a", label="A", node_type=NodeType.CONCEPT)
        node_b = Node(id="b", label="B", node_type=NodeType.CONCEPT)
        graph.add_node(node_a)
        graph.add_node(node_b)
        
        # Füge Edge hinzu
        edge = Edge(source="a", target="b", edge_type=EdgeType.RELATES_TO)
        edge_id = graph.add_edge(edge)
        
        assert graph.edge_count == 1
        assert graph.get_edge(edge_id) is not None
    
    def test_add_edge_invalid_nodes(self):
        """Teste Edge mit nicht-existenten Nodes."""
        graph = KnowledgeGraph()
        edge = Edge(source="nonexistent", target="also_not", edge_type=EdgeType.RELATES_TO)
        
        with pytest.raises(ValueError):
            graph.add_edge(edge)
    
    def test_remove_node(self):
        """Teste Node-Entfernung."""
        graph = KnowledgeGraph()
        node = Node(id="test", label="Test", node_type=NodeType.CONCEPT)
        graph.add_node(node)
        
        result = graph.remove_node("test")
        
        assert result is True
        assert graph.node_count == 0
        assert not graph.has_node("test")
    
    def test_get_neighbors(self):
        """Teste Nachbar-Abfrage."""
        graph = KnowledgeGraph()
        
        # Erstelle Dreieck
        for node_id in ["a", "b", "c"]:
            graph.add_node(Node(id=node_id, label=node_id, node_type=NodeType.CONCEPT))
        
        graph.add_edge(Edge("a", "b", EdgeType.RELATES_TO))
        graph.add_edge(Edge("a", "c", EdgeType.RELATES_TO))
        
        neighbors = graph.get_neighbors("a")
        neighbor_ids = {n.id for n in neighbors}
        
        assert neighbor_ids == {"b", "c"}
    
    def test_get_nodes_by_domain(self):
        """Teste Domänen-Filterung."""
        graph = KnowledgeGraph()
        
        node1 = Node(id="n1", label="N1", node_type=NodeType.CONCEPT, domains={Domain.ALCHEMY})
        node2 = Node(id="n2", label="N2", node_type=NodeType.CONCEPT, domains={Domain.ALCHEMY})
        node3 = Node(id="n3", label="N3", node_type=NodeType.CONCEPT, domains={Domain.MAGIC})
        
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        
        alchemy_nodes = graph.get_nodes_by_domain(Domain.ALCHEMY)
        
        assert len(alchemy_nodes) == 2
        assert all(Domain.ALCHEMY in n.domains for n in alchemy_nodes)
    
    def test_get_nodes_by_type(self):
        """Teste Typ-Filterung."""
        graph = KnowledgeGraph()
        
        graph.add_node(Node(id="c1", label="C1", node_type=NodeType.CONCEPT))
        graph.add_node(Node(id="e1", label="E1", node_type=NodeType.ENTITY))
        graph.add_node(Node(id="c2", label="C2", node_type=NodeType.CONCEPT))
        
        concepts = graph.get_nodes_by_type(NodeType.CONCEPT)
        
        assert len(concepts) == 2
        assert all(n.node_type == NodeType.CONCEPT for n in concepts)
    
    def test_find_path(self):
        """Teste Pfad-Findung."""
        graph = KnowledgeGraph()
        
        # Erstelle Pfad: a -> b -> c -> d
        for node_id in ["a", "b", "c", "d"]:
            graph.add_node(Node(id=node_id, label=node_id, node_type=NodeType.CONCEPT))
        
        graph.add_edge(Edge("a", "b", EdgeType.RELATES_TO))
        graph.add_edge(Edge("b", "c", EdgeType.RELATES_TO))
        graph.add_edge(Edge("c", "d", EdgeType.RELATES_TO))
        
        path = graph.find_path("a", "d")
        
        assert path is not None
        assert len(path) == 3
    
    def test_find_path_no_connection(self):
        """Teste Pfad-Findung ohne Verbindung."""
        graph = KnowledgeGraph()
        
        graph.add_node(Node(id="a", label="A", node_type=NodeType.CONCEPT))
        graph.add_node(Node(id="b", label="B", node_type=NodeType.CONCEPT))
        
        path = graph.find_path("a", "b")
        
        assert path is None
    
    def test_temporal_layers(self):
        """Teste Zeitschichten."""
        graph = KnowledgeGraph()
        
        node = Node(
            id="ancient_node",
            label="Ancient",
            node_type=NodeType.CONCEPT,
            periods={"Ancient"}
        )
        graph.add_node(node)
        
        layer = graph.get_temporal_layer("Ancient")
        
        assert layer is not None
        assert layer.period == "Ancient"
        assert "ancient_node" in layer.node_ids
    
    def test_calculate_centrality(self):
        """Teste Zentralitäts-Berechnung."""
        graph = KnowledgeGraph()
        
        # Stern-Graph: center verbunden mit a, b, c
        graph.add_node(Node(id="center", label="Center", node_type=NodeType.CONCEPT))
        for node_id in ["a", "b", "c"]:
            graph.add_node(Node(id=node_id, label=node_id, node_type=NodeType.CONCEPT))
            graph.add_edge(Edge("center", node_id, EdgeType.RELATES_TO))
        
        centrality = graph.calculate_centrality("center")
        
        assert centrality == 1.0  # Verbunden mit allen anderen
    
    def test_calculate_connection_strength(self):
        """Teste Verbindungsstärken-Berechnung."""
        graph = KnowledgeGraph()
        
        # Erstelle zwei verbundene Nodes
        node_a = Node(id="a", label="A", node_type=NodeType.CONCEPT, domains={Domain.ALCHEMY})
        node_b = Node(id="b", label="B", node_type=NodeType.CONCEPT, domains={Domain.ALCHEMY})
        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_edge(Edge("a", "b", EdgeType.RELATES_TO, weight=1.0))
        
        strength = graph.calculate_connection_strength("a", "b")
        
        assert strength > 0.5  # Starke Verbindung
    
    def test_graph_stats(self):
        """Teste Graph-Statistiken."""
        graph = KnowledgeGraph()
        
        # Füge Nodes verschiedener Typen hinzu
        graph.add_node(Node(id="c1", label="C1", node_type=NodeType.CONCEPT, domains={Domain.ALCHEMY}))
        graph.add_node(Node(id="e1", label="E1", node_type=NodeType.ENTITY))
        graph.add_edge(Edge("c1", "e1", EdgeType.MENTIONS))
        
        stats = graph.get_graph_stats()
        
        assert stats["node_count"] == 2
        assert stats["edge_count"] == 1
        assert "concept" in stats["nodes_by_type"]
        assert "entity" in stats["nodes_by_type"]
    
    def test_serialization(self):
        """Teste Graph-Serialisierung."""
        graph = KnowledgeGraph()
        
        node = Node(id="test", label="Test", node_type=NodeType.CONCEPT, domains={Domain.ALCHEMY})
        graph.add_node(node)
        graph.add_edge(Edge("test", "test", EdgeType.RELATES_TO))  # Self-loop
        
        # Zu JSON und zurück
        json_str = graph.to_json()
        restored = KnowledgeGraph.from_json(json_str)
        
        assert restored.node_count == 1
        assert restored.get_node("test") is not None


# ==================== KnowledgeCartographer Tests ====================

class TestKnowledgeCartographer:
    """Tests für die KnowledgeCartographer-Klasse."""
    
    def test_cartographer_creation(self):
        """Teste Cartographer-Initialisierung."""
        cartographer = KnowledgeCartographer()
        
        assert cartographer.graph is not None
        assert cartographer.graph.node_count == 0
    
    def test_classify_concept_domain(self):
        """Teste Domänen-Klassifikation."""
        cartographer = KnowledgeCartographer()
        
        assert cartographer._classify_concept_domain("alchemy") == Domain.ALCHEMY
        assert cartographer._classify_concept_domain("hermeticism") == Domain.HERMETICISM
        assert cartographer._classify_concept_domain("unknown") == Domain.UNKNOWN
    
    def test_get_or_create_concept_node(self):
        """Teste Konzept-Node-Erstellung."""
        cartographer = KnowledgeCartographer()
        
        node_id = cartographer._get_or_create_concept_node("alchemy")
        
        assert node_id.startswith("concept_")
        assert cartographer.graph.has_node(node_id)
        
        # Wiederverwendung
        node_id2 = cartographer._get_or_create_concept_node("alchemy")
        assert node_id == node_id2
    
    def test_get_or_create_period_node(self):
        """Teste Period-Node-Erstellung."""
        cartographer = KnowledgeCartographer()
        
        node_id = cartographer._get_or_create_period_node("Renaissance")
        
        assert node_id == "period_renaissance"
        assert cartographer.graph.has_node(node_id)
        
        node = cartographer.graph.get_node(node_id)
        assert node.properties["start_year"] == 1500
        assert node.properties["end_year"] == 1700
    
    def test_get_or_create_source_node(self):
        """Teste Source-Node-Erstellung."""
        cartographer = KnowledgeCartographer()
        
        source = "https://example.com/article"
        node_id = cartographer._get_or_create_source_node(source)
        
        assert cartographer.graph.has_node(node_id)
        assert cartographer._source_nodes[source] == node_id
    
    def test_map_fragments_integration(self):
        """Integrationstest: Fragmente zu Graph."""
        # Erstelle Mock-Fragmente
        class MockFragment:
            def __init__(self, text, source, period, concepts, confidence):
                self.text = text
                self.source = source
                self.period = MockPeriod(period)
                self.concepts = concepts
                self.confidence = confidence
        
        class MockPeriod:
            def __init__(self, value):
                self.value = value
        
        fragments = [
            MockFragment(
                text="Alchemy and hermeticism are connected.",
                source="source1.txt",
                period="Ancient",
                concepts=["alchemy", "hermeticism"],
                confidence=0.9
            ),
            MockFragment(
                text="Mysticism in the Renaissance.",
                source="source2.txt",
                period="Renaissance",
                concepts=["mysticism"],
                confidence=0.8
            ),
        ]
        
        cartographer = KnowledgeCartographer()
        graph = cartographer.map_fragments(fragments)
        
        # Prüfe Nodes
        assert graph.node_count >= 5  # Konzepte + Quellen + Perioden
        
        # Prüfe Konzept-Nodes
        assert any(n.label == "Alchemy" for n in graph.nodes)
        assert any(n.label == "Hermeticism" for n in graph.nodes)
        
        # Prüfe Edges
        assert graph.edge_count > 0
    
    def test_domain_summary(self):
        """Teste Domänen-Zusammenfassung."""
        cartographer = KnowledgeCartographer()
        
        # Erstelle Nodes in Domäne
        for i in range(3):
            node = Node(
                id=f"alchemy_{i}",
                label=f"Alchemy {i}",
                node_type=NodeType.CONCEPT,
                domains={Domain.ALCHEMY}
            )
            cartographer.graph.add_node(node)
        
        summary = cartographer.get_domain_summary(Domain.ALCHEMY)
        
        assert summary["domain"] == "alchemy"
        assert summary["total_nodes"] == 3
        assert summary["concepts"] == 3
    
    def test_temporal_analysis(self):
        """Teste zeitliche Analyse."""
        cartographer = KnowledgeCartographer()
        
        # Erstelle Nodes in verschiedenen Perioden
        cartographer.graph.add_node(Node(
            id="ancient",
            label="Ancient",
            node_type=NodeType.CONCEPT,
            periods={"Ancient"}
        ))
        cartographer.graph.add_node(Node(
            id="modern",
            label="Modern",
            node_type=NodeType.CONCEPT,
            periods={"Modern"}
        ))
        
        analysis = cartographer.get_temporal_analysis()
        
        assert "Ancient" in analysis["periods"]
        assert "Modern" in analysis["periods"]
        assert analysis["periods"]["Ancient"]["node_count"] == 1
    
    def test_export_for_visualization(self):
        """Teste Visualisierungs-Export."""
        cartographer = KnowledgeCartographer()
        
        # Erstelle Test-Graph
        node = Node(
            id="test",
            label="Test",
            node_type=NodeType.CONCEPT,
            domains={Domain.ALCHEMY}
        )
        cartographer.graph.add_node(node)
        
        export = cartographer.export_for_visualization()
        
        assert "nodes" in export
        assert "edges" in export
        assert len(export["nodes"]) == 1
        assert export["nodes"][0]["data"]["id"] == "test"


# ==================== Integration mit Excavator ====================

class TestExcavatorIntegration:
    """Integrationstests mit dem Excavator-Modul."""
    
    def test_import_excavator_fragment(self):
        """Teste Import von echten Excavator-Fragmenten."""
        try:
            from excavator import Fragment, TimePeriod
            
            # Erstelle echte Fragmente
            fragments = [
                Fragment(
                    text="Hermetic philosophy emerged in ancient Egypt.",
                    source="test.txt",
                    period=TimePeriod.ANCIENT,
                    concepts=["hermeticism", "philosophy"],
                    confidence=0.85
                ),
                Fragment(
                    text="Alchemy was practiced in medieval times.",
                    source="test2.txt",
                    period=TimePeriod.MEDIEVAL,
                    concepts=["alchemy"],
                    confidence=0.75
                ),
            ]
            
            cartographer = KnowledgeCartographer()
            graph = cartographer.map_fragments(fragments)
            
            # Verifiziere Graph-Struktur
            assert graph.node_count >= 6  # 2 Quellen + 2 Perioden + 3 Konzepte
            
            # Prüfe Konzept-Nodes
            concept_nodes = graph.get_nodes_by_type(NodeType.CONCEPT)
            assert len(concept_nodes) >= 3
            
            # Prüfe Period-Nodes
            period_nodes = graph.get_nodes_by_type(NodeType.PERIOD)
            assert len(period_nodes) >= 2
            
        except ImportError:
            pytest.skip("Excavator-Modul nicht verfügbar")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])