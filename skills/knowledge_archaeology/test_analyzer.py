"""
Knowledge Archaeology - Analyzer Tests

Unit Tests für das analyzer.py Modul (Phase 4).
"""

import unittest
import sys
import os
from pathlib import Path

# Füge Parent-Verzeichnis zum Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

from analyzer import (
    Cluster, Anomaly, CentralityMetrics, ConceptEvolution, TransmissionChain,
    AnalysisReport, KnowledgeAnalyzer,
    analyze_graph
)
from cartographer import (
    KnowledgeGraph, Node, Edge, NodeType, EdgeType, Domain
)


class TestCluster(unittest.TestCase):
    """Tests für die Cluster-Dataclass."""
    
    def test_cluster_creation(self):
        """Teste Erstellung eines Clusters."""
        cluster = Cluster(
            id="cluster_1",
            label="Test Cluster",
            node_ids={"node1", "node2", "node3"},
            domain=Domain.ALCHEMY,
            coherence=0.75,
            centroid="node1"
        )
        
        self.assertEqual(cluster.id, "cluster_1")
        self.assertEqual(cluster.label, "Test Cluster")
        self.assertEqual(len(cluster.node_ids), 3)
        self.assertEqual(cluster.domain, Domain.ALCHEMY)
        self.assertEqual(cluster.coherence, 0.75)
        self.assertEqual(cluster.centroid, "node1")
    
    def test_cluster_coherence_validation(self):
        """Teste Kohärenz-Validierung."""
        cluster_high = Cluster(id="c1", label="Test", coherence=1.5)
        self.assertEqual(cluster_high.coherence, 1.0)
        
        cluster_low = Cluster(id="c2", label="Test", coherence=-0.5)
        self.assertEqual(cluster_low.coherence, 0.0)
    
    def test_cluster_to_dict(self):
        """Teste Konvertierung zu Dictionary."""
        cluster = Cluster(
            id="cluster_1",
            label="Test",
            node_ids={"n1", "n2"},
            domain=Domain.HERMETICISM,
            coherence=0.8
        )
        
        d = cluster.to_dict()
        self.assertEqual(d["id"], "cluster_1")
        self.assertEqual(d["label"], "Test")
        self.assertEqual(set(d["node_ids"]), {"n1", "n2"})
        self.assertEqual(d["domain"], "hermeticism")
        self.assertEqual(d["coherence"], 0.8)


class TestAnomaly(unittest.TestCase):
    """Tests für die Anomaly-Dataclass."""
    
    def test_anomaly_creation(self):
        """Teste Erstellung einer Anomalie."""
        anomaly = Anomaly(
            node_id="node1",
            anomaly_type=Anomaly.Type.OUTLIER,
            score=0.85,
            description="Test anomaly",
            expected_connections=5,
            actual_connections=1
        )
        
        self.assertEqual(anomaly.node_id, "node1")
        self.assertEqual(anomaly.anomaly_type, Anomaly.Type.OUTLIER)
        self.assertEqual(anomaly.score, 0.85)
        self.assertEqual(anomaly.description, "Test anomaly")
    
    def test_anomaly_score_validation(self):
        """Teste Score-Validierung."""
        anomaly_high = Anomaly(node_id="n1", anomaly_type=Anomaly.Type.HUB, score=1.5)
        self.assertEqual(anomaly_high.score, 1.0)
        
        anomaly_low = Anomaly(node_id="n2", anomaly_type=Anomaly.Type.ISOLATED, score=-0.5)
        self.assertEqual(anomaly_low.score, 0.0)
    
    def test_anomaly_types(self):
        """Teste alle Anomalie-Typen."""
        types = [
            Anomaly.Type.ISOLATED,
            Anomaly.Type.OUTLIER,
            Anomaly.Type.BRIDGE,
            Anomaly.Type.HUB,
            Anomaly.Type.TEMPORAL_GAP,
        ]
        
        for anomaly_type in types:
            anomaly = Anomaly(node_id="n1", anomaly_type=anomaly_type)
            self.assertEqual(anomaly.anomaly_type, anomaly_type)


class TestCentralityMetrics(unittest.TestCase):
    """Tests für die CentralityMetrics-Dataclass."""
    
    def test_metrics_creation(self):
        """Teste Erstellung von Metriken."""
        metrics = CentralityMetrics(
            node_id="node1",
            degree_centrality=0.5,
            betweenness_centrality=0.3,
            closeness_centrality=0.4,
            eigenvector_centrality=0.2,
            pagerank=0.1
        )
        
        self.assertEqual(metrics.node_id, "node1")
        self.assertEqual(metrics.degree_centrality, 0.5)
        self.assertEqual(metrics.betweenness_centrality, 0.3)
    
    def test_overall_score_calculation(self):
        """Teste Berechnung des Gesamt-Scores."""
        metrics = CentralityMetrics(
            node_id="node1",
            degree_centrality=1.0,
            betweenness_centrality=0.0,
            closeness_centrality=0.0,
            eigenvector_centrality=0.0,
            pagerank=0.0
        )
        
        # Gewichtung: 0.3, 0.25, 0.2, 0.15, 0.1
        expected = 1.0 * 0.3  # Nur degree_centrality trägt bei
        self.assertAlmostEqual(metrics.overall_score, expected, places=4)
    
    def test_overall_score_all_metrics(self):
        """Teste Gesamt-Score mit allen Metriken."""
        metrics = CentralityMetrics(
            node_id="node1",
            degree_centrality=1.0,
            betweenness_centrality=1.0,
            closeness_centrality=1.0,
            eigenvector_centrality=1.0,
            pagerank=1.0
        )
        
        self.assertAlmostEqual(metrics.overall_score, 1.0, places=4)
    
    def test_to_dict(self):
        """Teste Konvertierung zu Dictionary."""
        metrics = CentralityMetrics(
            node_id="node1",
            degree_centrality=0.5,
            betweenness_centrality=0.3
        )
        
        d = metrics.to_dict()
        self.assertEqual(d["node_id"], "node1")
        self.assertEqual(d["degree_centrality"], 0.5)
        self.assertEqual(d["betweenness_centrality"], 0.3)
        self.assertIn("overall_score", d)


class TestConceptEvolution(unittest.TestCase):
    """Tests für die ConceptEvolution-Dataclass."""
    
    def test_evolution_creation(self):
        """Teste Erstellung einer Evolution."""
        evolution = ConceptEvolution(
            concept_id="concept1",
            concept_label="Alchemy",
            timeline=[("Ancient", 1.0), ("Medieval", 2.0), ("Renaissance", 1.5)],
            emergence_period="Ancient",
            peak_period="Medieval",
            related_concepts=["concept2", "concept3"]
        )
        
        self.assertEqual(evolution.concept_id, "concept1")
        self.assertEqual(evolution.concept_label, "Alchemy")
        self.assertEqual(len(evolution.timeline), 3)
        self.assertEqual(evolution.emergence_period, "Ancient")
        self.assertEqual(evolution.peak_period, "Medieval")


class TestTransmissionChain(unittest.TestCase):
    """Tests für die TransmissionChain-Dataclass."""
    
    def test_chain_creation(self):
        """Teste Erstellung einer Kette."""
        chain = TransmissionChain(
            id="chain_1",
            start_node="node1",
            end_node="node5",
            path=["node1", "node2", "node3", "node4", "node5"],
            strength=0.75,
            periods_covered={"Ancient", "Medieval"},
            transmission_type=TransmissionChain.Type.MULTI_HOP
        )
        
        self.assertEqual(chain.id, "chain_1")
        self.assertEqual(chain.start_node, "node1")
        self.assertEqual(chain.end_node, "node5")
        self.assertEqual(len(chain.path), 5)
        self.assertEqual(chain.strength, 0.75)
    
    def test_chain_strength_validation(self):
        """Teste Stärke-Validierung."""
        chain_high = TransmissionChain(
            id="c1", start_node="n1", end_node="n2", strength=1.5
        )
        self.assertEqual(chain_high.strength, 1.0)
        
        chain_low = TransmissionChain(
            id="c2", start_node="n1", end_node="n2", strength=-0.5
        )
        self.assertEqual(chain_low.strength, 0.0)
    
    def test_chain_types(self):
        """Teste alle Chain-Typen."""
        types = [
            TransmissionChain.Type.DIRECT,
            TransmissionChain.Type.MULTI_HOP,
            TransmissionChain.Type.CROSS_DOMAIN,
            TransmissionChain.Type.TEMPORAL,
        ]
        
        for chain_type in types:
            chain = TransmissionChain(
                id="c1", start_node="n1", end_node="n2", transmission_type=chain_type
            )
            self.assertEqual(chain.transmission_type, chain_type)


class TestAnalysisReport(unittest.TestCase):
    """Tests für die AnalysisReport-Dataclass."""
    
    def test_report_creation(self):
        """Teste Erstellung eines Reports."""
        report = AnalysisReport(
            graph_stats={"node_count": 10, "edge_count": 15},
            clusters=[Cluster(id="c1", label="Cluster 1")],
            anomalies=[Anomaly(node_id="n1", anomaly_type=Anomaly.Type.OUTLIER)],
            insights=["Insight 1", "Insight 2"]
        )
        
        self.assertEqual(report.graph_stats["node_count"], 10)
        self.assertEqual(len(report.clusters), 1)
        self.assertEqual(len(report.anomalies), 1)
        self.assertEqual(len(report.insights), 2)
    
    def test_report_to_dict(self):
        """Teste Konvertierung zu Dictionary."""
        report = AnalysisReport(
            graph_stats={"count": 5},
            clusters=[Cluster(id="c1", label="Test")],
            insights=["Test insight"]
        )
        
        d = report.to_dict()
        self.assertEqual(d["graph_stats"]["count"], 5)
        self.assertEqual(len(d["clusters"]), 1)
        self.assertEqual(len(d["insights"]), 1)


class TestKnowledgeAnalyzer(unittest.TestCase):
    """Tests für die KnowledgeAnalyzer-Klasse."""
    
    def setUp(self):
        """Erstelle Test-Graph für jeden Test."""
        self.graph = KnowledgeGraph()
        
        # Füge Nodes hinzu
        nodes = [
            Node(id="n1", label="Alchemy", node_type=NodeType.CONCEPT, 
                 domains={Domain.ALCHEMY}, periods={"Ancient", "Medieval"}),
            Node(id="n2", label="Hermeticism", node_type=NodeType.CONCEPT,
                 domains={Domain.HERMETICISM}, periods={"Ancient", "Renaissance"}),
            Node(id="n3", label="Kabbalah", node_type=NodeType.CONCEPT,
                 domains={Domain.KABBALAH}, periods={"Medieval"}),
            Node(id="n4", label="Astrology", node_type=NodeType.CONCEPT,
                 domains={Domain.ASTROLOGY}, periods={"Ancient", "Medieval", "Renaissance"}),
            Node(id="n5", label="Gnosis", node_type=NodeType.CONCEPT,
                 domains={Domain.GNOSIS}, periods={"Ancient"}),
        ]
        
        for node in nodes:
            self.graph.add_node(node)
        
        # Füge Edges hinzu (sternförmig um n1)
        edges = [
            Edge("n1", "n2", EdgeType.RELATES_TO, 0.8),
            Edge("n1", "n3", EdgeType.RELATES_TO, 0.7),
            Edge("n1", "n4", EdgeType.RELATES_TO, 0.6),
            Edge("n1", "n5", EdgeType.RELATES_TO, 0.5),
            Edge("n2", "n4", EdgeType.SIMILAR_TO, 0.4, bidirectional=True),
        ]
        
        for edge in edges:
            self.graph.add_edge(edge)
        
        self.analyzer = KnowledgeAnalyzer(self.graph)
    
    def test_analyzer_initialization(self):
        """Teste Initialisierung des Analyzers."""
        self.assertEqual(self.analyzer.graph, self.graph)
        self.assertEqual(len(self.analyzer._node_neighbors), 5)
    
    def test_build_indices(self):
        """Teste Index-Aufbau."""
        # n1 hat 4 Nachbarn (n2, n3, n4, n5)
        self.assertEqual(len(self.analyzer._node_neighbors["n1"]), 4)
        # n2 hat 2 Nachbarn (n1, n4) - jetzt korrekt behandelt
        self.assertEqual(len(self.analyzer._node_neighbors["n2"]), 2)
    
    # ==================== Clustering Tests ====================
    
    def test_detect_clusters_louvain(self):
        """Teste Louvain-Clustering."""
        clusters = self.analyzer.detect_clusters(algorithm="louvain")
        self.assertIsInstance(clusters, list)
        # Bei diesem kleinen Graph sollten alle Nodes in einem Cluster sein
        self.assertGreaterEqual(len(clusters), 1)
    
    def test_detect_clusters_greedy(self):
        """Teste Greedy-Clustering."""
        clusters = self.analyzer.detect_clusters(algorithm="greedy")
        self.assertIsInstance(clusters, list)
        self.assertGreaterEqual(len(clusters), 1)
    
    def test_detect_clusters_label_prop(self):
        """Teste Label Propagation Clustering."""
        clusters = self.analyzer.detect_clusters(algorithm="label_prop")
        self.assertIsInstance(clusters, list)
        self.assertGreaterEqual(len(clusters), 1)
    
    def test_cluster_invalid_algorithm(self):
        """Teste ungültigen Clustering-Algorithmus."""
        with self.assertRaises(ValueError):
            self.analyzer.detect_clusters(algorithm="invalid")
    
    def test_create_cluster_from_nodes(self):
        """Teste Erstellung eines Clusters aus Nodes."""
        node_ids = {"n1", "n2", "n3"}
        cluster = self.analyzer._create_cluster_from_nodes("test_cluster", node_ids)
        
        self.assertEqual(cluster.id, "test_cluster")
        self.assertEqual(cluster.node_ids, node_ids)
        self.assertIsNotNone(cluster.coherence)
        self.assertIsNotNone(cluster.centroid)
    
    # ==================== Anomaly Detection Tests ====================
    
    def test_detect_anomalies_statistical(self):
        """Teste statistische Anomalie-Erkennung."""
        anomalies = self.analyzer.detect_anomalies(method="statistical")
        self.assertIsInstance(anomalies, list)
        # n1 ist HUB (hoher Degree), n5 ist möglicherweise OUTLIER (niedriger Degree)
    
    def test_detect_anomalies_isolation(self):
        """Teste Isolation Forest Anomalie-Erkennung."""
        anomalies = self.analyzer.detect_anomalies(method="isolation")
        self.assertIsInstance(anomalies, list)
    
    def test_detect_anomalies_distance(self):
        """Teste distanz-basierte Anomalie-Erkennung."""
        anomalies = self.analyzer.detect_anomalies(method="distance")
        self.assertIsInstance(anomalies, list)
    
    def test_detect_isolated_nodes(self):
        """Teste Erkennung isolierter Nodes."""
        # Füge isolierten Node hinzu
        isolated = Node(id="isolated", label="Isolated", node_type=NodeType.CONCEPT)
        self.graph.add_node(isolated)
        self.analyzer._build_indices()
        
        anomalies = self.analyzer._detect_isolated_nodes()
        isolated_anomalies = [a for a in anomalies if a.anomaly_type == Anomaly.Type.ISOLATED]
        self.assertGreaterEqual(len(isolated_anomalies), 1)
    
    def test_detect_bridge_nodes(self):
        """Teste Erkennung von Brücken-Nodes."""
        anomalies = self.analyzer._detect_bridge_nodes()
        self.assertIsInstance(anomalies, list)
    
    def test_detect_temporal_gaps(self):
        """Teste Erkennung zeitlicher Lücken."""
        anomalies = self.analyzer._detect_temporal_gaps()
        self.assertIsInstance(anomalies, list)
    
    def test_calculate_local_clustering(self):
        """Teste Berechnung des lokalen Clustering-Koeffizienten."""
        # n2 ist mit n1 und n4 verbunden, aber n1 und n4 sind nicht verbunden
        clustering = self.analyzer._calculate_local_clustering("n2")
        self.assertGreaterEqual(clustering, 0.0)
        self.assertLessEqual(clustering, 1.0)
    
    def test_calculate_graph_distance(self):
        """Teste Berechnung der Graph-Distanz."""
        # Distanz von n2 zu n3 über n1 (n2 -> n1 -> n3)
        dist = self.analyzer._calculate_graph_distance("n2", "n3")
        self.assertEqual(dist, 2)
        
        # Distanz zu sich selbst
        dist_self = self.analyzer._calculate_graph_distance("n1", "n1")
        self.assertEqual(dist_self, 0)
    
    # ==================== Centrality Tests ====================
    
    def test_calculate_centralities(self):
        """Teste Berechnung aller Zentralitäten."""
        centralities = self.analyzer.calculate_centralities()
        self.assertEqual(len(centralities), 5)
        
        for metric in centralities:
            self.assertIsInstance(metric, CentralityMetrics)
            self.assertGreaterEqual(metric.degree_centrality, 0.0)
            self.assertLessEqual(metric.degree_centrality, 1.0)
    
    def test_degree_centrality(self):
        """Teste Degree Centrality Berechnung."""
        centrality = self.analyzer._calculate_degree_centrality_all()
        
        # n1 hat den höchsten Degree (4)
        self.assertEqual(centrality["n1"], 1.0)
        
        # n2 hat Degree 2 (n1 und n4)
        expected = 2 / 4  # 2 Verbindungen von 4 möglichen
        self.assertAlmostEqual(centrality["n2"], expected, places=4)
    
    def test_betweenness_centrality(self):
        """Teste Betweenness Centrality Berechnung."""
        betweenness = self.analyzer._calculate_betweenness_centrality()
        
        # n1 sollte hohe Betweenness haben (liegt auf vielen Pfaden)
        # In einem sternförmigen Graph ist n1 der zentrale Knoten
        self.assertGreaterEqual(betweenness["n1"], 0.0)
        
        # Alle Werte sollten zwischen 0 und 1 sein
        for score in betweenness.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_closeness_centrality(self):
        """Teste Closeness Centrality Berechnung."""
        closeness = self.analyzer._calculate_closeness_centrality_all()
        
        # Alle Werte sollten zwischen 0 und 1 sein
        for score in closeness.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_eigenvector_centrality(self):
        """Teste Eigenvector Centrality Berechnung."""
        eigenvector = self.analyzer._calculate_eigenvector_centrality()
        
        # Alle Werte sollten zwischen 0 und 1 sein
        for score in eigenvector.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
        
        # n1 sollte hohen Wert haben
        self.assertGreater(eigenvector["n1"], eigenvector.get("n5", 0))
    
    def test_pagerank(self):
        """Teste PageRank Berechnung."""
        pagerank = self.analyzer._calculate_pagerank()
        
        # Alle Werte sollten zwischen 0 und 1 sein
        for score in pagerank.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
        
        # n1 sollte hohen PageRank haben (viele eingehende Links)
        self.assertGreater(pagerank["n1"], 0.0)
    
    # ==================== Temporal Analysis Tests ====================
    
    def test_analyze_concept_evolution(self):
        """Teste Konzept-Evolutions-Analyse."""
        evolutions = self.analyzer.analyze_concept_evolution()
        
        # Sollte eine Evolution für jedes Konzept haben
        self.assertEqual(len(evolutions), 5)
        
        for evolution in evolutions:
            self.assertIsInstance(evolution, ConceptEvolution)
            self.assertIsNotNone(evolution.concept_id)
            self.assertIsNotNone(evolution.concept_label)
    
    def test_calculate_concept_activity(self):
        """Teste Aktivitäts-Berechnung."""
        activity = self.analyzer._calculate_concept_activity_in_period("n1", "Ancient")
        self.assertGreater(activity, 0.0)  # n1 hat Ancient in periods
        
        activity_none = self.analyzer._calculate_concept_activity_in_period("n1", "Modern")
        self.assertEqual(activity_none, 0.0)  # n1 hat kein Modern
    
    def test_find_related_concepts(self):
        """Teste Finden verwandter Konzepte."""
        related = self.analyzer._find_related_concepts("n1")
        # n1 ist mit allen anderen verbunden, aber _find_related_concepts 
        # sucht nach gemeinsamen Nachbarn (nicht direkte Verbindungen)
        # Da n1 der zentrale Knoten ist, haben alle anderen n1 als gemeinsamen Nachbarn
        self.assertIsInstance(related, list)
    
    # ==================== Transmission Chain Tests ====================
    
    def test_detect_transmission_chains(self):
        """Teste Erkennung von Übertragungsketten."""
        chains = self.analyzer.detect_transmission_chains(min_strength=0.1)
        self.assertIsInstance(chains, list)
        
        for chain in chains:
            self.assertIsInstance(chain, TransmissionChain)
            self.assertGreaterEqual(chain.strength, 0.1)
    
    def test_find_transmission_path(self):
        """Teste Finden von Übertragungspfaden."""
        path = self.analyzer._find_transmission_path("n2", "n3")
        self.assertIsNotNone(path)
        self.assertEqual(path[0], "n2")
        self.assertEqual(path[-1], "n3")
        # Pfad sollte n2 -> n1 -> n3 sein (Länge 3)
        self.assertEqual(len(path), 3)
    
    def test_calculate_chain_strength(self):
        """Teste Berechnung der Ketten-Stärke."""
        path = ["n2", "n1", "n3"]
        strength = self.analyzer._calculate_chain_strength(path)
        self.assertGreaterEqual(strength, 0.0)
        self.assertLessEqual(strength, 1.0)
    
    def test_create_transmission_chain(self):
        """Teste Erstellung einer TransmissionChain."""
        path = ["n1", "n2", "n4"]
        chain = self.analyzer._create_transmission_chain("n1", "n4", path, 0.7)
        
        self.assertEqual(chain.start_node, "n1")
        self.assertEqual(chain.end_node, "n4")
        self.assertEqual(chain.path, path)
        self.assertEqual(chain.strength, 0.7)
    
    # ==================== Main Analysis Tests ====================
    
    def test_analyze(self):
        """Teste komplette Analyse."""
        report = self.analyzer.analyze()
        
        self.assertIsInstance(report, AnalysisReport)
        self.assertIn("node_count", report.graph_stats)
        self.assertIn("edge_count", report.graph_stats)
        self.assertIsInstance(report.clusters, list)
        self.assertIsInstance(report.anomalies, list)
        self.assertIsInstance(report.centralities, list)
        self.assertIsInstance(report.concept_evolutions, list)
        self.assertIsInstance(report.transmission_chains, list)
        self.assertIsInstance(report.insights, list)
    
    def test_generate_insights(self):
        """Teste Insight-Generierung."""
        report = self.analyzer.analyze()
        insights = self.analyzer._generate_insights(report)
        
        self.assertIsInstance(insights, list)
        # Sollte mindestens einige Insights haben
        self.assertGreater(len(insights), 0)


class TestConvenienceFunctions(unittest.TestCase):
    """Tests für Convenience-Funktionen."""
    
    def test_analyze_graph(self):
        """Teste analyze_graph Funktion."""
        graph = KnowledgeGraph()
        
        # Füge einige Nodes und Edges hinzu
        n1 = Node(id="n1", label="Test1", node_type=NodeType.CONCEPT)
        n2 = Node(id="n2", label="Test2", node_type=NodeType.CONCEPT)
        graph.add_node(n1)
        graph.add_node(n2)
        graph.add_edge(Edge("n1", "n2", EdgeType.RELATES_TO))
        
        report = analyze_graph(graph)
        
        self.assertIsInstance(report, AnalysisReport)
        self.assertEqual(report.graph_stats["node_count"], 2)


class TestIntegration(unittest.TestCase):
    """Integrationstests für das gesamte Analyse-System."""
    
    def test_full_workflow(self):
        """Teste kompletten Analyse-Workflow."""
        # Erstelle komplexeren Test-Graph
        graph = KnowledgeGraph()
        
        # Füge Nodes aus verschiedenen Domänen und Perioden hinzu
        nodes_data = [
            ("alchemy", "Alchemy", Domain.ALCHEMY, {"Ancient", "Medieval", "Renaissance"}),
            ("hermeticism", "Hermeticism", Domain.HERMETICISM, {"Ancient", "Renaissance"}),
            ("kabbalah", "Kabbalah", Domain.KABBALAH, {"Medieval", "Renaissance"}),
            ("gnosis", "Gnosis", Domain.GNOSIS, {"Ancient", "Medieval"}),
            ("astrology", "Astrology", Domain.ASTROLOGY, {"Ancient", "Medieval", "Renaissance"}),
            ("mysticism", "Mysticism", Domain.MYSTICISM, {"Medieval", "Renaissance"}),
            ("philosophy", "Philosophy", Domain.PHILOSOPHY, {"Ancient", "Modern"}),
            ("magic", "Magic", Domain.MAGIC, {"Ancient", "Medieval"}),
        ]
        
        for node_id, label, domain, periods in nodes_data:
            node = Node(
                id=f"concept_{node_id}",
                label=label,
                node_type=NodeType.CONCEPT,
                domains={domain},
                periods=periods
            )
            graph.add_node(node)
        
        # Füge Verbindungen hinzu (komplexeres Netzwerk)
        edges_data = [
            ("concept_alchemy", "concept_hermeticism", 0.9),
            ("concept_alchemy", "concept_astrology", 0.8),
            ("concept_alchemy", "concept_magic", 0.7),
            ("concept_hermeticism", "concept_gnosis", 0.8),
            ("concept_hermeticism", "concept_philosophy", 0.6),
            ("concept_kabbalah", "concept_mysticism", 0.9),
            ("concept_kabbalah", "concept_hermeticism", 0.7),
            ("concept_gnosis", "concept_mysticism", 0.8),
            ("concept_astrology", "concept_magic", 0.6),
            ("concept_astrology", "concept_hermeticism", 0.7),
            ("concept_mysticism", "concept_philosophy", 0.5),
        ]
        
        for source, target, weight in edges_data:
            graph.add_edge(Edge(source, target, EdgeType.RELATES_TO, weight))
        
        # Führe Analyse durch
        analyzer = KnowledgeAnalyzer(graph)
        report = analyzer.analyze()
        
        # Überprüfe Ergebnisse
        self.assertEqual(report.graph_stats["node_count"], 8)
        self.assertEqual(report.graph_stats["edge_count"], 11)
        
        # Sollte Cluster finden
        self.assertGreaterEqual(len(report.clusters), 1)
        
        # Sollte Zentralitäten berechnen
        self.assertEqual(len(report.centralities), 8)
        
        # Sollte Konzept-Evolutionen haben
        self.assertEqual(len(report.concept_evolutions), 8)
        
        # Sollte Insights generieren
        self.assertGreater(len(report.insights), 0)
        
        # Überprüfe JSON-Export
        json_str = report.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn("graph_stats", json_str)
        self.assertIn("clusters", json_str)
    
    def test_modularity_calculation(self):
        """Teste Modularity-Berechnung."""
        graph = KnowledgeGraph()
        
        # Erstelle zwei getrennte Communities
        for i in range(4):
            node = Node(id=f"a{i}", label=f"A{i}", node_type=NodeType.CONCEPT)
            graph.add_node(node)
        
        for i in range(4):
            node = Node(id=f"b{i}", label=f"B{i}", node_type=NodeType.CONCEPT)
            graph.add_node(node)
        
        # Verbinde innerhalb der Communities
        for i in range(4):
            for j in range(i+1, 4):
                graph.add_edge(Edge(f"a{i}", f"a{j}", EdgeType.RELATES_TO))
                graph.add_edge(Edge(f"b{i}", f"b{j}", EdgeType.RELATES_TO))
        
        # Eine Verbindung zwischen Communities
        graph.add_edge(Edge("a0", "b0", EdgeType.RELATES_TO))
        
        analyzer = KnowledgeAnalyzer(graph)
        
        # Teste Modularity mit getrennten Communities
        node_to_community = {f"a{i}": 0 for i in range(4)}
        node_to_community.update({f"b{i}": 1 for i in range(4)})
        
        modularity = analyzer._calculate_modularity(node_to_community)
        # Sollte positive Modularity haben
        self.assertGreater(modularity, 0.0)


if __name__ == "__main__":
    # Führe alle Tests aus
    unittest.main(verbosity=2)
