"""
Knowledge Archaeology - Analyzer Module

Phase 4: ANALYSIS - Mustererkennung im Knowledge Graph

Dieses Modul analysiert den Knowledge Graph aus Phase 3 und erkennt:
- Cluster (Community Detection)
- Anomalien (Outlier Detection)
- Zentrale Konzepte (Centrality Analysis)
- Konzept-Evolution über Zeit (Temporal Analysis)
- Übertragungsketten (Transmission Chains)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Set, Tuple, Any, Callable
from collections import defaultdict
import json
import math
from pathlib import Path

# Importiere Phase 3
from cartographer import (
    KnowledgeGraph, Node, Edge, NodeType, EdgeType, Domain, TemporalLayer
)


@dataclass
class Cluster:
    """
    Ein Wissens-Cluster (Community) im Knowledge Graph.
    
    Attributes:
        id: Eindeutige Cluster-ID
        label: Beschreibender Name
        node_ids: IDs der Nodes im Cluster
        domain: Primäre Domäne des Clusters
        coherence: Kohärenz-Score (0-1)
        centroid: Zentraler Node des Clusters
    """
    id: str
    label: str
    node_ids: Set[str] = field(default_factory=set)
    domain: Optional[Domain] = None
    coherence: float = 0.0
    centroid: Optional[str] = None
    
    def __post_init__(self):
        """Validiere Kohärenz."""
        self.coherence = max(0.0, min(1.0, self.coherence))
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere Cluster zu Dictionary."""
        return {
            "id": self.id,
            "label": self.label,
            "node_ids": list(self.node_ids),
            "domain": self.domain.value if self.domain else None,
            "coherence": self.coherence,
            "centroid": self.centroid,
        }


@dataclass
class Anomaly:
    """
    Eine erkannte Anomalie im Knowledge Graph.
    
    Attributes:
        node_id: ID des anomalen Nodes
        anomaly_type: Typ der Anomalie
        score: Anomalie-Score (0-1, höher = anomaler)
        description: Beschreibung der Anomalie
        expected_connections: Erwartete Anzahl Verbindungen
        actual_connections: Tatsächliche Anzahl Verbindungen
    """
    class Type(Enum):
        ISOLATED = "isolated"           # Isolierter Node
        OUTLIER = "outlier"             # Statistischer Ausreißer
        BRIDGE = "bridge"               # Brücken-Node zwischen Clustern
        HUB = "hub"                     # Ungewöhnlich gut vernetzt
        TEMPORAL_GAP = "temporal_gap"   # Zeitliche Lücke
    
    node_id: str
    anomaly_type: Type
    score: float = 0.0
    description: str = ""
    expected_connections: int = 0
    actual_connections: int = 0
    
    def __post_init__(self):
        """Validiere Score."""
        self.score = max(0.0, min(1.0, self.score))
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere Anomalie zu Dictionary."""
        return {
            "node_id": self.node_id,
            "anomaly_type": self.anomaly_type.value,
            "score": self.score,
            "description": self.description,
            "expected_connections": self.expected_connections,
            "actual_connections": self.actual_connections,
        }


@dataclass
class CentralityMetrics:
    """
    Zentralitäts-Metriken für einen Node.
    
    Attributes:
        node_id: ID des Nodes
        degree_centrality: Degree Centrality (0-1)
        betweenness_centrality: Betweenness Centrality (0-1)
        closeness_centrality: Closeness Centrality (0-1)
        eigenvector_centrality: Eigenvector Centrality (0-1)
        pagerank: PageRank-Score (0-1)
    """
    node_id: str
    degree_centrality: float = 0.0
    betweenness_centrality: float = 0.0
    closeness_centrality: float = 0.0
    eigenvector_centrality: float = 0.0
    pagerank: float = 0.0
    
    @property
    def overall_score(self) -> float:
        """Berechne Gesamt-Zentralität als gewichteten Durchschnitt."""
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        values = [
            self.degree_centrality,
            self.betweenness_centrality,
            self.closeness_centrality,
            self.eigenvector_centrality,
            self.pagerank,
        ]
        return sum(w * v for w, v in zip(weights, values))
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere Metriken zu Dictionary."""
        return {
            "node_id": self.node_id,
            "degree_centrality": round(self.degree_centrality, 4),
            "betweenness_centrality": round(self.betweenness_centrality, 4),
            "closeness_centrality": round(self.closeness_centrality, 4),
            "eigenvector_centrality": round(self.eigenvector_centrality, 4),
            "pagerank": round(self.pagerank, 4),
            "overall_score": round(self.overall_score, 4),
        }


@dataclass
class ConceptEvolution:
    """
    Evolution eines Konzepts über Zeit.
    
    Attributes:
        concept_id: ID des Konzept-Nodes
        concept_label: Name des Konzepts
        timeline: Liste von (Periode, Aktivitäts-Score) Tupeln
        emergence_period: Periode des ersten Auftretens
        peak_period: Periode der höchsten Aktivität
        related_concepts: Konzepte, die mit der Evolution verbunden sind
    """
    concept_id: str
    concept_label: str
    timeline: List[Tuple[str, float]] = field(default_factory=list)
    emergence_period: Optional[str] = None
    peak_period: Optional[str] = None
    related_concepts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere Evolution zu Dictionary."""
        return {
            "concept_id": self.concept_id,
            "concept_label": self.concept_label,
            "timeline": self.timeline,
            "emergence_period": self.emergence_period,
            "peak_period": self.peak_period,
            "related_concepts": self.related_concepts,
        }


@dataclass
class TransmissionChain:
    """
    Eine Übertragungskette von Wissen.
    
    Attributes:
        id: Eindeutige ID der Kette
        start_node: Startpunkt der Übertragung
        end_node: Endpunkt der Übertragung
        path: Liste der Node-IDs im Pfad
        path_edges: Liste der Edge-IDs im Pfad
        strength: Stärke der Übertragung (0-1)
        periods_covered: Zeitperioden, die die Kette überspannt
        transmission_type: Art der Übertragung
    """
    class Type(Enum):
        DIRECT = "direct"           # Direkte Übertragung
        MULTI_HOP = "multi_hop"     # Über mehrere Zwischenstationen
        CROSS_DOMAIN = "cross_domain"  # Über Domänen-Grenzen
        TEMPORAL = "temporal"       # Über Zeitperioden hinweg
    
    id: str
    start_node: str
    end_node: str
    path: List[str] = field(default_factory=list)
    path_edges: List[str] = field(default_factory=list)
    strength: float = 0.0
    periods_covered: Set[str] = field(default_factory=set)
    transmission_type: Type = Type.DIRECT
    
    def __post_init__(self):
        """Validiere Stärke."""
        self.strength = max(0.0, min(1.0, self.strength))
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere Kette zu Dictionary."""
        return {
            "id": self.id,
            "start_node": self.start_node,
            "end_node": self.end_node,
            "path": self.path,
            "path_edges": self.path_edges,
            "strength": self.strength,
            "periods_covered": list(self.periods_covered),
            "transmission_type": self.transmission_type.value,
        }


@dataclass
class AnalysisReport:
    """
    Vollständiger Analyse-Report für einen Knowledge Graph.
    
    Attributes:
        graph_stats: Statistiken über den Graph
        clusters: Gefundene Wissens-Cluster
        anomalies: Erkannte Anomalien
        centralities: Zentralitäts-Metriken für alle Nodes
        concept_evolutions: Evolution der Konzepte
        transmission_chains: Erkannte Übertragungsketten
        insights: Automatisch generierte Erkenntnisse
    """
    graph_stats: Dict[str, Any] = field(default_factory=dict)
    clusters: List[Cluster] = field(default_factory=list)
    anomalies: List[Anomaly] = field(default_factory=list)
    centralities: List[CentralityMetrics] = field(default_factory=list)
    concept_evolutions: List[ConceptEvolution] = field(default_factory=list)
    transmission_chains: List[TransmissionChain] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere Report zu Dictionary."""
        return {
            "graph_stats": self.graph_stats,
            "clusters": [c.to_dict() for c in self.clusters],
            "anomalies": [a.to_dict() for a in self.anomalies],
            "centralities": [c.to_dict() for c in self.centralities],
            "concept_evolutions": [e.to_dict() for e in self.concept_evolutions],
            "transmission_chains": [t.to_dict() for t in self.transmission_chains],
            "insights": self.insights,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Serialisiere Report zu JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save_to_file(self, filepath: str) -> None:
        """Speichere Report in JSON-Datei."""
        Path(filepath).write_text(self.to_json(), encoding="utf-8")


class KnowledgeAnalyzer:
    """
    Hauptklasse für die Analyse-Phase des Knowledge Archaeology Systems.
    
    Analysiert den Knowledge Graph und erkennt Muster, Cluster,
    Anomalien und Übertragungsketten.
    """
    
    def __init__(self, graph: KnowledgeGraph):
        """
        Initialisiere den Analyzer.
        
        Args:
            graph: Der zu analysierende Knowledge Graph
        """
        self.graph = graph
        self._node_neighbors: Dict[str, Set[str]] = {}
        self._node_degrees: Dict[str, int] = {}
        self._shortest_paths: Dict[Tuple[str, str], List[str]] = {}
        self._build_indices()
    
    def _build_indices(self) -> None:
        """Baue interne Indizes für effiziente Analyse."""
        for node in self.graph.nodes:
            neighbors = set()
            for edge in self.graph.edges:
                if edge.source == node.id:
                    neighbors.add(edge.target)
                if edge.target == node.id:
                    if edge.bidirectional:
                        neighbors.add(edge.source)
                    # Auch nicht-bidirektionale Edges sollten den target-Node 
                    # als verbunden mit source betrachten
                    neighbors.add(edge.source)
            self._node_neighbors[node.id] = neighbors
            self._node_degrees[node.id] = len(neighbors)
    
    # ==================== Clustering (Community Detection) ====================
    
    def detect_clusters(self, algorithm: str = "louvain") -> List[Cluster]:
        """
        Erkenne Wissens-Cluster im Graph.
        
        Args:
            algorithm: Clustering-Algorithmus ("louvain", "greedy", "label_prop")
            
        Returns:
            Liste der gefundenen Cluster
        """
        if algorithm == "louvain":
            return self._louvain_clustering()
        elif algorithm == "greedy":
            return self._greedy_modularity_clustering()
        elif algorithm == "label_prop":
            return self._label_propagation_clustering()
        else:
            raise ValueError(f"Unknown clustering algorithm: {algorithm}")
    
    def _louvain_clustering(self) -> List[Cluster]:
        """
        Louvain-Algorithmus für Community Detection.
        
        Vereinfachte Implementierung des Louvain-Algorithmus.
        Optimiert Modularity durch iterative Node-Zuweisung.
        
        Returns:
            Liste der gefundenen Cluster
        """
        # Initialisiere: Jeder Node ist seine eigene Community
        node_to_community: Dict[str, int] = {node.id: i for i, node in enumerate(self.graph.nodes)}
        communities: Dict[int, Set[str]] = {i: {node.id} for i, node in enumerate(self.graph.nodes)}
        
        # Berechne initiale Modularity
        current_modularity = self._calculate_modularity(node_to_community)
        improved = True
        iterations = 0
        max_iterations = 10
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for node in self.graph.nodes:
                current_community = node_to_community[node.id]
                
                # Finde beste Community für diesen Node
                best_community = current_community
                best_gain = 0.0
                
                # Betrachte Communities der Nachbarn
                neighbor_communities: Dict[int, int] = defaultdict(int)
                for neighbor_id in self._node_neighbors.get(node.id, set()):
                    neighbor_communities[node_to_community[neighbor_id]] += 1
                
                for community_id, connections in neighbor_communities.items():
                    if community_id == current_community:
                        continue
                    
                    # Berechne Modularity-Gain
                    gain = self._calculate_modularity_gain(node.id, current_community, community_id, node_to_community)
                    
                    if gain > best_gain:
                        best_gain = gain
                        best_community = community_id
                
                # Verschiebe Node, wenn Verbesserung
                if best_community != current_community:
                    communities[current_community].discard(node.id)
                    communities[best_community].add(node.id)
                    node_to_community[node.id] = best_community
                    improved = True
            
            new_modularity = self._calculate_modularity(node_to_community)
            if new_modularity > current_modularity:
                current_modularity = new_modularity
            else:
                break
        
        # Erstelle Cluster-Objekte
        clusters = []
        for community_id, node_ids in communities.items():
            if len(node_ids) < 2:  # Ignoriere Singletons
                continue
            
            cluster = self._create_cluster_from_nodes(f"cluster_{community_id}", node_ids)
            clusters.append(cluster)
        
        return clusters
    
    def _greedy_modularity_clustering(self) -> List[Cluster]:
        """
        Greedy Modularity Maximization für Community Detection.
        
        Startet mit einzelnen Nodes und fügt Communities zusammen,
        die den größten Modularity-Gain ergeben.
        
        Returns:
            Liste der gefundenen Cluster
        """
        # Initialisiere: Jeder Node ist seine eigene Community
        node_to_community: Dict[str, int] = {node.id: i for i, node in enumerate(self.graph.nodes)}
        communities: Dict[int, Set[str]] = {i: {node.id} for i, node in enumerate(self.graph.nodes)}
        
        # Berechne initiale Modularity
        current_modularity = self._calculate_modularity(node_to_community)
        
        # Iteriere, bis keine Verbesserung mehr möglich
        improved = True
        iterations = 0
        max_iterations = 20
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            # Finde bestes Community-Paar zum Zusammenführen
            best_pair: Optional[Tuple[int, int]] = None
            best_gain = 0.0
            
            community_ids = list(communities.keys())
            for i, comm1 in enumerate(community_ids):
                for comm2 in community_ids[i+1:]:
                    gain = self._calculate_merge_gain(comm1, comm2, communities, node_to_community)
                    if gain > best_gain:
                        best_gain = gain
                        best_pair = (comm1, comm2)
            
            # Führe Communities zusammen, wenn Verbesserung
            if best_pair and best_gain > 0:
                comm1, comm2 = best_pair
                # Verschiebe alle Nodes von comm2 nach comm1
                for node_id in communities[comm2]:
                    node_to_community[node_id] = comm1
                    communities[comm1].add(node_id)
                del communities[comm2]
                current_modularity += best_gain
                improved = True
        
        # Erstelle Cluster-Objekte
        clusters = []
        for i, (community_id, node_ids) in enumerate(communities.items()):
            if len(node_ids) < 2:
                continue
            
            cluster = self._create_cluster_from_nodes(f"cluster_{i}", node_ids)
            clusters.append(cluster)
        
        return clusters
    
    def _label_propagation_clustering(self) -> List[Cluster]:
        """
        Label Propagation Algorithmus für Community Detection.
        
        Jeder Node übernimmt das häufigste Label seiner Nachbarn.
        Konvergiert schnell zu Communities.
        
        Returns:
            Liste der gefundenen Cluster
        """
        # Initialisiere: Jeder Node hat eindeutiges Label
        labels: Dict[str, int] = {node.id: i for i, node in enumerate(self.graph.nodes)}
        
        # Iteriere bis Konvergenz
        converged = False
        iterations = 0
        max_iterations = 100
        
        node_ids = list(labels.keys())
        
        while not converged and iterations < max_iterations:
            converged = True
            iterations += 1
            
            # Zufällige Reihenfolge für Stabilität
            import random
            random.shuffle(node_ids)
            
            for node_id in node_ids:
                # Zähle Labels der Nachbarn
                neighbor_labels: Dict[int, int] = defaultdict(int)
                for neighbor_id in self._node_neighbors.get(node_id, set()):
                    neighbor_labels[labels[neighbor_id]] += 1
                
                if not neighbor_labels:
                    continue
                
                # Finde häufigstes Label
                best_label = max(neighbor_labels.items(), key=lambda x: x[1])[0]
                
                if labels[node_id] != best_label:
                    labels[node_id] = best_label
                    converged = False
        
        # Gruppiere Nodes nach Label
        communities: Dict[int, Set[str]] = defaultdict(set)
        for node_id, label in labels.items():
            communities[label].add(node_id)
        
        # Erstelle Cluster-Objekte
        clusters = []
        for i, (label, node_ids) in enumerate(communities.items()):
            if len(node_ids) < 2:
                continue
            
            cluster = self._create_cluster_from_nodes(f"cluster_{i}", node_ids)
            clusters.append(cluster)
        
        return clusters
    
    def _calculate_modularity(self, node_to_community: Dict[str, int]) -> float:
        """
        Berechne Modularity-Score für eine Community-Zuweisung.
        
        Args:
            node_to_community: Mapping von Node-ID zu Community-ID
            
        Returns:
            Modularity-Score
        """
        m = self.graph.edge_count
        if m == 0:
            return 0.0
        
        modularity = 0.0
        node_ids = list(node_to_community.keys())
        
        for i, node1_id in enumerate(node_ids):
            for node2_id in node_ids[i+1:]:
                if node_to_community[node1_id] == node_to_community[node2_id]:
                    # Gleiche Community
                    A_ij = 1.0 if node2_id in self._node_neighbors.get(node1_id, set()) else 0.0
                    k_i = self._node_degrees.get(node1_id, 0)
                    k_j = self._node_degrees.get(node2_id, 0)
                    modularity += A_ij - (k_i * k_j) / (2 * m)
        
        return modularity / (2 * m)
    
    def _calculate_modularity_gain(self, node_id: str, from_community: int, 
                                    to_community: int, node_to_community: Dict[str, int]) -> float:
        """
        Berechne Modularity-Gain für Verschiebung eines Nodes.
        
        Args:
            node_id: ID des zu verschiebenden Nodes
            from_community: Aktuelle Community
            to_community: Ziel-Community
            node_to_community: Aktuelles Community-Mapping
            
        Returns:
            Modularity-Gain
        """
        m = self.graph.edge_count
        if m == 0:
            return 0.0
        
        # Zähle Verbindungen zu jeder Community
        k_i_to = sum(1 for n in self._node_neighbors.get(node_id, set()) 
                     if node_to_community.get(n) == to_community)
        k_i_from = sum(1 for n in self._node_neighbors.get(node_id, set()) 
                       if node_to_community.get(n) == from_community)
        
        # Berechne Summe der Degrees in jeder Community
        sum_to = sum(self._node_degrees.get(n, 0) for n, c in node_to_community.items() 
                     if c == to_community)
        sum_from = sum(self._node_degrees.get(n, 0) for n, c in node_to_community.items() 
                       if c == from_community)
        
        k_i = self._node_degrees.get(node_id, 0)
        
        # Modularity-Gain Formel
        gain = (k_i_to - k_i_from) / (2 * m) - (k_i / (2 * m * 2 * m)) * (sum_to - sum_from + k_i)
        
        return gain
    
    def _calculate_merge_gain(self, comm1: int, comm2: int, 
                               communities: Dict[int, Set[str]],
                               node_to_community: Dict[str, int]) -> float:
        """
        Berechne Modularity-Gain für Zusammenführen zweier Communities.
        
        Args:
            comm1: Erste Community
            comm2: Zweite Community
            communities: Community-Mapping
            node_to_community: Node-zu-Community Mapping
            
        Returns:
            Modularity-Gain
        """
        m = self.graph.edge_count
        if m == 0:
            return 0.0
        
        # Zähle Verbindungen zwischen den Communities
        edges_between = 0
        for node1 in communities[comm1]:
            for node2 in communities[comm2]:
                if node2 in self._node_neighbors.get(node1, set()):
                    edges_between += 1
        
        # Berechne Summe der Degrees
        sum_comm1 = sum(self._node_degrees.get(n, 0) for n in communities[comm1])
        sum_comm2 = sum(self._node_degrees.get(n, 0) for n in communities[comm2])
        
        # Modularity-Gain für Merge
        gain = edges_between / m - (sum_comm1 * sum_comm2) / (2 * m * 2 * m)
        
        return gain
    
    def _create_cluster_from_nodes(self, cluster_id: str, node_ids: Set[str]) -> Cluster:
        """
        Erstelle ein Cluster-Objekt aus einer Menge von Nodes.
        
        Args:
            cluster_id: ID des Clusters
            node_ids: IDs der Nodes im Cluster
            
        Returns:
            Cluster-Objekt
        """
        # Finde häufigste Domäne
        domain_counts: Dict[Domain, int] = defaultdict(int)
        for node_id in node_ids:
            node = self.graph.get_node(node_id)
            if node:
                for domain in node.domains:
                    domain_counts[domain] += 1
        
        primary_domain = max(domain_counts.items(), key=lambda x: x[1])[0] if domain_counts else None
        
        # Berechne Kohärenz (interne Verbindungen / mögliche Verbindungen)
        internal_edges = 0
        for node_id in node_ids:
            for neighbor_id in self._node_neighbors.get(node_id, set()):
                if neighbor_id in node_ids:
                    internal_edges += 1
        
        possible_edges = len(node_ids) * (len(node_ids) - 1)
        coherence = internal_edges / possible_edges if possible_edges > 0 else 0.0
        
        # Finde zentralen Node (höchste Degree im Cluster)
        centroid = None
        max_degree = -1
        for node_id in node_ids:
            degree = sum(1 for n in self._node_neighbors.get(node_id, set()) if n in node_ids)
            if degree > max_degree:
                max_degree = degree
                centroid = node_id
        
        # Erstelle Label aus häufigsten Konzepten
        node_labels = []
        for node_id in node_ids:
            node = self.graph.get_node(node_id)
            if node:
                node_labels.append(node.label)
        
        label = f"Cluster {cluster_id.split('_')[-1]}"
        if primary_domain:
            label = f"{primary_domain.value.title()} Cluster"
        
        return Cluster(
            id=cluster_id,
            label=label,
            node_ids=node_ids,
            domain=primary_domain,
            coherence=round(coherence, 3),
            centroid=centroid,
        )
    
    # ==================== Anomaly Detection ====================
    
    def detect_anomalies(self, method: str = "statistical") -> List[Anomaly]:
        """
        Erkenne Anomalien im Knowledge Graph.
        
        Args:
            method: Anomalie-Erkennungsmethode ("statistical", "isolation", "distance")
            
        Returns:
            Liste der erkannten Anomalien
        """
        anomalies = []
        
        if method == "statistical":
            anomalies.extend(self._statistical_outlier_detection())
        elif method == "isolation":
            anomalies.extend(self._isolation_forest_detection())
        elif method == "distance":
            anomalies.extend(self._distance_based_detection())
        
        # Zusätzliche Heuristiken
        anomalies.extend(self._detect_isolated_nodes())
        anomalies.extend(self._detect_bridge_nodes())
        anomalies.extend(self._detect_temporal_gaps())
        
        # Entferne Duplikate und sortiere nach Score
        seen = set()
        unique_anomalies = []
        for anomaly in anomalies:
            key = (anomaly.node_id, anomaly.anomaly_type)
            if key not in seen:
                seen.add(key)
                unique_anomalies.append(anomaly)
        
        unique_anomalies.sort(key=lambda x: x.score, reverse=True)
        return unique_anomalies
    
    def _statistical_outlier_detection(self) -> List[Anomaly]:
        """
        Statistische Outlier-Erkennung basierend auf Node-Degrees.
        
        Verwendet Z-Score, um Nodes mit ungewöhnlich hohem oder niedrigem Degree zu finden.
        
        Returns:
            Liste der Outlier-Anomalien
        """
        anomalies = []
        
        if not self._node_degrees:
            return anomalies
        
        # Berechne Statistiken
        degrees = list(self._node_degrees.values())
        mean_degree = sum(degrees) / len(degrees)
        variance = sum((d - mean_degree) ** 2 for d in degrees) / len(degrees)
        std_degree = math.sqrt(variance)
        
        if std_degree == 0:
            return anomalies
        
        # Finde Outlier (|Z-Score| > 2)
        for node_id, degree in self._node_degrees.items():
            z_score = (degree - mean_degree) / std_degree
            
            if abs(z_score) > 2:
                if z_score > 0:
                    # Ungewöhnlich gut vernetzt
                    anomaly = Anomaly(
                        node_id=node_id,
                        anomaly_type=Anomaly.Type.HUB,
                        score=min(abs(z_score) / 3, 1.0),
                        description=f"Unusually high connectivity (degree={degree}, z={z_score:.2f})",
                        expected_connections=int(mean_degree),
                        actual_connections=degree,
                    )
                else:
                    # Ungewöhnlich schlecht vernetzt
                    anomaly = Anomaly(
                        node_id=node_id,
                        anomaly_type=Anomaly.Type.OUTLIER,
                        score=min(abs(z_score) / 3, 1.0),
                        description=f"Unusually low connectivity (degree={degree}, z={z_score:.2f})",
                        expected_connections=int(mean_degree),
                        actual_connections=degree,
                    )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _isolation_forest_detection(self) -> List[Anomaly]:
        """
        Isolation Forest ähnliche Anomalie-Erkennung.
        
        Vereinfachte Implementierung: Isoliere Nodes durch zufällige Partitionierung.
        
        Returns:
            Liste der Anomalien
        """
        anomalies = []
        
        # Feature-Vektoren für jeden Node: [degree, clustering_coefficient, domain_count]
        features: Dict[str, List[float]] = {}
        for node in self.graph.nodes:
            degree = self._node_degrees.get(node.id, 0)
            clustering = self._calculate_local_clustering(node.id)
            domain_count = len(node.domains)
            features[node.id] = [float(degree), clustering, float(domain_count)]
        
        # Isolation durch rekursive Partitionierung (simuliert)
        isolation_scores: Dict[str, float] = {}
        
        for node_id, feature_vector in features.items():
            # Simuliere Isolation: Wie schnell wird der Node isoliert?
            # Vereinfacht: Nutze Abstand zum Median
            median_degree = sorted(self._node_degrees.values())[len(self._node_degrees) // 2]
            degree_deviation = abs(feature_vector[0] - median_degree)
            
            # Normalisiere zu Score (höher = anomaler)
            max_deviation = max(abs(d - median_degree) for d in self._node_degrees.values())
            if max_deviation > 0:
                isolation_scores[node_id] = degree_deviation / max_deviation
            else:
                isolation_scores[node_id] = 0.0
        
        # Erstelle Anomalien für Top-Outlier
        threshold = 0.7
        for node_id, score in isolation_scores.items():
            if score > threshold:
                anomaly = Anomaly(
                    node_id=node_id,
                    anomaly_type=Anomaly.Type.OUTLIER,
                    score=score,
                    description=f"Isolation forest anomaly (isolation_score={score:.2f})",
                    expected_connections=0,
                    actual_connections=self._node_degrees.get(node_id, 0),
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _distance_based_detection(self) -> List[Anomaly]:
        """
        Distanz-basierte Anomalie-Erkennung.
        
        Findet Nodes, die weit von ihren Nachbarn entfernt sind.
        
        Returns:
            Liste der Anomalien
        """
        anomalies = []
        
        for node in self.graph.nodes:
            # Berechne durchschnittliche Distanz zu allen anderen Nodes
            distances = []
            for other_node in self.graph.nodes:
                if node.id != other_node.id:
                    dist = self._calculate_graph_distance(node.id, other_node.id)
                    if dist is not None:
                        distances.append(dist)
            
            if not distances:
                continue
            
            avg_distance = sum(distances) / len(distances)
            max_possible = max(distances) if distances else 1
            
            # Hohe durchschnittliche Distanz = isoliert
            if avg_distance > max_possible * 0.8:
                anomaly = Anomaly(
                    node_id=node.id,
                    anomaly_type=Anomaly.Type.ISOLATED,
                    score=avg_distance / max_possible if max_possible > 0 else 0.0,
                    description=f"Structurally isolated (avg_distance={avg_distance:.1f})",
                    expected_connections=0,
                    actual_connections=self._node_degrees.get(node.id, 0),
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_isolated_nodes(self) -> List[Anomaly]:
        """
        Erkenne vollständig isolierte Nodes.
        
        Returns:
            Liste der Isolations-Anomalien
        """
        anomalies = []
        
        for node in self.graph.nodes:
            degree = self._node_degrees.get(node.id, 0)
            if degree == 0:
                anomaly = Anomaly(
                    node_id=node.id,
                    anomaly_type=Anomaly.Type.ISOLATED,
                    score=1.0,
                    description="Completely isolated node (no connections)",
                    expected_connections=1,
                    actual_connections=0,
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_bridge_nodes(self) -> List[Anomaly]:
        """
        Erkenne Brücken-Nodes zwischen Communities.
        
        Brücken-Nodes verbinden verschiedene Cluster und haben hohe Betweenness.
        
        Returns:
            Liste der Brücken-Anomalien
        """
        anomalies = []
        
        # Berechne Betweenness Centrality für alle Nodes
        betweenness = self._calculate_betweenness_centrality()
        
        # Finde Nodes mit hoher Betweenness
        if betweenness:
            max_betweenness = max(betweenness.values())
            threshold = max_betweenness * 0.7
            
            for node_id, score in betweenness.items():
                if score >= threshold:
                    anomaly = Anomaly(
                        node_id=node_id,
                        anomaly_type=Anomaly.Type.BRIDGE,
                        score=score / max_betweenness if max_betweenness > 0 else 0.0,
                        description=f"Bridge node between communities (betweenness={score:.3f})",
                        expected_connections=0,
                        actual_connections=self._node_degrees.get(node_id, 0),
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_temporal_gaps(self) -> List[Anomaly]:
        """
        Erkenne zeitliche Lücken in der Wissensübertragung.
        
        Returns:
            Liste der Temporal-Gap-Anomalien
        """
        anomalies = []
        
        # Hole alle Perioden
        periods = [layer.period for layer in self.graph.temporal_layers]
        if len(periods) < 2:
            return anomalies
        
        # Definiere Perioden-Reihenfolge
        period_order = ["Ancient", "Medieval", "Renaissance", "Modern"]
        
        # Finde Nodes, die in nicht-aufeinanderfolgenden Perioden vorkommen
        for node in self.graph.nodes:
            node_periods = sorted([p for p in node.periods if p in period_order], 
                                   key=lambda x: period_order.index(x))
            
            if len(node_periods) >= 2:
                # Prüfe auf Lücken
                for i in range(len(node_periods) - 1):
                    idx1 = period_order.index(node_periods[i])
                    idx2 = period_order.index(node_periods[i + 1])
                    
                    if idx2 - idx1 > 1:
                        # Lücke gefunden
                        gap_periods = period_order[idx1 + 1:idx2]
                        anomaly = Anomaly(
                            node_id=node.id,
                            anomaly_type=Anomaly.Type.TEMPORAL_GAP,
                            score=0.5 + 0.1 * (idx2 - idx1),
                            description=f"Temporal gap: appears in {node_periods[i]} and {node_periods[i+1]} but not in {', '.join(gap_periods)}",
                            expected_connections=0,
                            actual_connections=len(node_periods),
                        )
                        anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_local_clustering(self, node_id: str) -> float:
        """
        Berechne lokale Clustering-Koeffizient für einen Node.
        
        Args:
            node_id: ID des Nodes
            
        Returns:
            Clustering-Koeffizient (0-1)
        """
        neighbors = self._node_neighbors.get(node_id, set())
        k = len(neighbors)
        
        if k < 2:
            return 0.0
        
        # Zähle Verbindungen zwischen Nachbarn
        edges_between_neighbors = 0
        for n1 in neighbors:
            for n2 in neighbors:
                if n1 < n2 and n2 in self._node_neighbors.get(n1, set()):
                    edges_between_neighbors += 1
        
        # Clustering-Koeffizient
        possible_edges = k * (k - 1) / 2
        return edges_between_neighbors / possible_edges if possible_edges > 0 else 0.0
    
    def _calculate_graph_distance(self, start_id: str, end_id: str) -> Optional[int]:
        """
        Berechne kürzeste Pfad-Distanz zwischen zwei Nodes.
        
        Args:
            start_id: Start-Node ID
            end_id: Ziel-Node ID
            
        Returns:
            Distanz oder None wenn nicht erreichbar
        """
        if start_id == end_id:
            return 0
        
        # BFS
        visited = {start_id}
        queue = [(start_id, 0)]
        
        while queue:
            current_id, distance = queue.pop(0)
            
            for neighbor_id in self._node_neighbors.get(current_id, set()):
                if neighbor_id == end_id:
                    return distance + 1
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, distance + 1))
        
        return None
    
    # ==================== Centrality Analysis ====================
    
    def calculate_centralities(self) -> List[CentralityMetrics]:
        """
        Berechne alle Zentralitäts-Metriken für alle Nodes.
        
        Returns:
            Liste der Zentralitäts-Metriken
        """
        metrics = []
        
        # Degree Centrality
        degree_centrality = self._calculate_degree_centrality_all()
        
        # Betweenness Centrality
        betweenness_centrality = self._calculate_betweenness_centrality()
        
        # Closeness Centrality
        closeness_centrality = self._calculate_closeness_centrality_all()
        
        # Eigenvector Centrality
        eigenvector_centrality = self._calculate_eigenvector_centrality()
        
        # PageRank
        pagerank = self._calculate_pagerank()
        
        # Kombiniere zu Metriken
        for node in self.graph.nodes:
            metric = CentralityMetrics(
                node_id=node.id,
                degree_centrality=degree_centrality.get(node.id, 0.0),
                betweenness_centrality=betweenness_centrality.get(node.id, 0.0),
                closeness_centrality=closeness_centrality.get(node.id, 0.0),
                eigenvector_centrality=eigenvector_centrality.get(node.id, 0.0),
                pagerank=pagerank.get(node.id, 0.0),
            )
            metrics.append(metric)
        
        return metrics
    
    def _calculate_degree_centrality_all(self) -> Dict[str, float]:
        """
        Berechne Degree Centrality für alle Nodes.
        
        Returns:
            Dictionary mit Node-ID -> Centrality
        """
        n = self.graph.node_count
        if n <= 1:
            return {node.id: 0.0 for node in self.graph.nodes}
        
        return {
            node_id: degree / (n - 1)
            for node_id, degree in self._node_degrees.items()
        }
    
    def _calculate_betweenness_centrality(self) -> Dict[str, float]:
        """
        Berechne Betweenness Centrality für alle Nodes.
        
        Betweenness misst, wie oft ein Node auf kürzesten Pfaden liegt.
        
        Returns:
            Dictionary mit Node-ID -> Betweenness
        """
        betweenness: Dict[str, float] = {node.id: 0.0 for node in self.graph.nodes}
        
        n = self.graph.node_count
        if n <= 2:
            return betweenness
        
        # Für jeden Node als Source
        for source in self.graph.nodes:
            # BFS für kürzeste Pfade
            distances: Dict[str, int] = {node.id: -1 for node in self.graph.nodes}
            num_paths: Dict[str, int] = {node.id: 0 for node in self.graph.nodes}
            parents: Dict[str, List[str]] = {node.id: [] for node in self.graph.nodes}
            
            distances[source.id] = 0
            num_paths[source.id] = 1
            
            queue = [source.id]
            visited_order = []
            
            while queue:
                current = queue.pop(0)
                visited_order.append(current)
                
                for neighbor in self._node_neighbors.get(current, set()):
                    if distances[neighbor] == -1:
                        distances[neighbor] = distances[current] + 1
                        queue.append(neighbor)
                    
                    if distances[neighbor] == distances[current] + 1:
                        num_paths[neighbor] += num_paths[current]
                        parents[neighbor].append(current)
            
            # Akkumuliere Betweenness (Rückwärts)
            dependency: Dict[str, float] = {node.id: 0.0 for node in self.graph.nodes}
            
            for node_id in reversed(visited_order):
                if node_id != source.id:
                    for parent in parents[node_id]:
                        if num_paths[node_id] > 0:
                            dependency[parent] += (num_paths[parent] / num_paths[node_id]) * (1 + dependency[node_id])
                    
                    if node_id != source.id:
                        betweenness[node_id] += dependency[node_id]
        
        # Normalisiere (für ungerichtete Graphen)
        for node_id in betweenness:
            betweenness[node_id] /= 2.0
        
        # Normalisiere zu [0, 1]
        max_betweenness = max(betweenness.values()) if betweenness else 1.0
        if max_betweenness > 0:
            for node_id in betweenness:
                betweenness[node_id] /= max_betweenness
        
        return betweenness
    
    def _calculate_closeness_centrality_all(self) -> Dict[str, float]:
        """
        Berechne Closeness Centrality für alle Nodes.
        
        Closeness misst, wie nah ein Node zu allen anderen Nodes ist.
        
        Returns:
            Dictionary mit Node-ID -> Closeness
        """
        closeness: Dict[str, float] = {}
        
        n = self.graph.node_count
        if n <= 1:
            return {node.id: 0.0 for node in self.graph.nodes}
        
        for node in self.graph.nodes:
            # Berechne Distanzen zu allen anderen Nodes
            distances = []
            for other in self.graph.nodes:
                if node.id != other.id:
                    dist = self._calculate_graph_distance(node.id, other.id)
                    if dist is not None:
                        distances.append(dist)
            
            if distances:
                avg_distance = sum(distances) / len(distances)
                closeness[node.id] = len(distances) / sum(distances) if sum(distances) > 0 else 0.0
            else:
                closeness[node.id] = 0.0
        
        return closeness
    
    def _calculate_eigenvector_centrality(self, max_iterations: int = 100, 
                                           tolerance: float = 1e-6) -> Dict[str, float]:
        """
        Berechne Eigenvector Centrality für alle Nodes.
        
        Eigenvector Centrality misst Einfluss basierend auf Einfluss der Nachbarn.
        
        Args:
            max_iterations: Maximale Iterationen
            tolerance: Konvergenz-Toleranz
            
        Returns:
            Dictionary mit Node-ID -> Eigenvector Centrality
        """
        # Initialisiere
        centrality: Dict[str, float] = {node.id: 1.0 for node in self.graph.nodes}
        
        for _ in range(max_iterations):
            new_centrality: Dict[str, float] = {}
            
            for node in self.graph.nodes:
                # Summe der Zentralitäten der Nachbarn
                score = sum(centrality.get(neighbor, 0.0) 
                           for neighbor in self._node_neighbors.get(node.id, set()))
                new_centrality[node.id] = score
            
            # Normalisiere
            max_score = max(new_centrality.values()) if new_centrality else 1.0
            if max_score > 0:
                new_centrality = {k: v / max_score for k, v in new_centrality.items()}
            
            # Prüfe Konvergenz
            diff = sum(abs(new_centrality.get(node.id, 0.0) - centrality.get(node.id, 0.0)) 
                      for node in self.graph.nodes)
            
            centrality = new_centrality
            
            if diff < tolerance:
                break
        
        return centrality
    
    def _calculate_pagerank(self, damping: float = 0.85, max_iterations: int = 100,
                            tolerance: float = 1e-6) -> Dict[str, float]:
        """
        Berechne PageRank für alle Nodes.
        
        PageRank misst Wichtigkeit basierend auf eingehenden Verbindungen.
        
        Args:
            damping: Damping-Faktor
            max_iterations: Maximale Iterationen
            tolerance: Konvergenz-Toleranz
            
        Returns:
            Dictionary mit Node-ID -> PageRank
        """
        n = self.graph.node_count
        if n == 0:
            return {}
        
        # Initialisiere
        pagerank: Dict[str, float] = {node.id: 1.0 / n for node in self.graph.nodes}
        
        # Berechne ausgehende Degrees
        out_degrees: Dict[str, int] = {}
        for node in self.graph.nodes:
            out_degrees[node.id] = len(self._node_neighbors.get(node.id, set()))
        
        for _ in range(max_iterations):
            new_pagerank: Dict[str, float] = {}
            
            for node in self.graph.nodes:
                # Summe der PageRanks der eingehenden Links
                rank = (1 - damping) / n
                
                for neighbor_id in self._node_neighbors.get(node.id, set()):
                    if out_degrees.get(neighbor_id, 0) > 0:
                        rank += damping * pagerank.get(neighbor_id, 0.0) / out_degrees[neighbor_id]
                
                new_pagerank[node.id] = rank
            
            # Prüfe Konvergenz
            diff = sum(abs(new_pagerank.get(node.id, 0.0) - pagerank.get(node.id, 0.0)) 
                      for node in self.graph.nodes)
            
            pagerank = new_pagerank
            
            if diff < tolerance:
                break
        
        # Normalisiere
        max_rank = max(pagerank.values()) if pagerank else 1.0
        if max_rank > 0:
            pagerank = {k: v / max_rank for k, v in pagerank.items()}
        
        return pagerank
    
    # ==================== Temporal Analysis ====================
    
    def analyze_concept_evolution(self) -> List[ConceptEvolution]:
        """
        Analysiere die Evolution von Konzepten über Zeit.
        
        Returns:
            Liste der Konzept-Evolutionen
        """
        evolutions = []
        
        # Hole alle Konzept-Nodes
        concept_nodes = [n for n in self.graph.nodes if n.node_type == NodeType.CONCEPT]
        
        # Definiere Perioden-Reihenfolge
        period_order = ["Ancient", "Medieval", "Renaissance", "Modern"]
        
        for concept in concept_nodes:
            # Sammle Aktivitäts-Daten für jede Periode
            timeline = []
            
            for period in period_order:
                # Zähle Verbindungen in dieser Periode
                activity = self._calculate_concept_activity_in_period(concept.id, period)
                timeline.append((period, activity))
            
            # Finde erste und höchste Aktivität
            emergence = None
            peak = None
            max_activity = -1
            
            for period, activity in timeline:
                if activity > 0 and emergence is None:
                    emergence = period
                if activity > max_activity:
                    max_activity = activity
                    peak = period
            
            # Finde verwandte Konzepte
            related = self._find_related_concepts(concept.id)
            
            evolution = ConceptEvolution(
                concept_id=concept.id,
                concept_label=concept.label,
                timeline=timeline,
                emergence_period=emergence,
                peak_period=peak,
                related_concepts=related,
            )
            evolutions.append(evolution)
        
        return evolutions
    
    def _calculate_concept_activity_in_period(self, concept_id: str, period: str) -> float:
        """
        Berechne Aktivitäts-Score eines Konzepts in einer Periode.
        
        Args:
            concept_id: ID des Konzepts
            period: Zeitperiode
            
        Returns:
            Aktivitäts-Score
        """
        node = self.graph.get_node(concept_id)
        if not node or period not in node.periods:
            return 0.0
        
        # Basis-Score für Vorkommen in Periode
        score = 1.0
        
        # Zusätzlich: Verbindungen zu anderen Nodes in derselben Periode
        for neighbor_id in self._node_neighbors.get(concept_id, set()):
            neighbor = self.graph.get_node(neighbor_id)
            if neighbor and period in neighbor.periods:
                score += 0.5
        
        return score
    
    def _find_related_concepts(self, concept_id: str) -> List[str]:
        """
        Finde verwandte Konzepte basierend auf gemeinsamen Nachbarn.
        
        Args:
            concept_id: ID des Konzepts
            
        Returns:
            Liste der IDs verwandter Konzepte
        """
        node = self.graph.get_node(concept_id)
        if not node:
            return []
        
        related = []
        node_neighbors = self._node_neighbors.get(concept_id, set())
        
        for other in self.graph.nodes:
            if other.id == concept_id or other.node_type != NodeType.CONCEPT:
                continue
            
            # Gemeinsame Nachbarn
            other_neighbors = self._node_neighbors.get(other.id, set())
            common = node_neighbors & other_neighbors
            
            if len(common) >= 2:  # Mindestens 2 gemeinsame Nachbarn
                related.append(other.id)
        
        return related[:5]  # Max 5 verwandte Konzepte
    
    def detect_transmission_chains(self, min_strength: float = 0.3) -> List[TransmissionChain]:
        """
        Erkenne Übertragungsketten von Wissen.
        
        Args:
            min_strength: Minimale Stärke für eine Kette
            
        Returns:
            Liste der Übertragungsketten
        """
        chains = []
        
        # Finde alle Paare von Konzept-Nodes
        concept_nodes = [n for n in self.graph.nodes if n.node_type == NodeType.CONCEPT]
        
        for i, start_node in enumerate(concept_nodes):
            for end_node in concept_nodes[i+1:]:
                # Finde Pfad zwischen den Nodes
                path = self._find_transmission_path(start_node.id, end_node.id)
                
                if path and len(path) >= 2:
                    strength = self._calculate_chain_strength(path)
                    
                    if strength >= min_strength:
                        chain = self._create_transmission_chain(start_node.id, end_node.id, path, strength)
                        chains.append(chain)
        
        # Sortiere nach Stärke
        chains.sort(key=lambda x: x.strength, reverse=True)
        
        return chains[:50]  # Max 50 Ketten
    
    def _find_transmission_path(self, start_id: str, end_id: str, max_length: int = 5) -> Optional[List[str]]:
        """
        Finde einen Übertragungspfad zwischen zwei Nodes.
        
        Args:
            start_id: Start-Node ID
            end_id: Ziel-Node ID
            max_length: Maximale Pfadlänge
            
        Returns:
            Liste der Node-IDs im Pfad oder None
        """
        if start_id == end_id:
            return [start_id]
        
        # BFS mit Pfad-Tracking
        queue = [(start_id, [start_id])]
        visited = {start_id}
        
        while queue:
            current_id, path = queue.pop(0)
            
            if len(path) >= max_length:
                continue
            
            for neighbor_id in self._node_neighbors.get(current_id, set()):
                if neighbor_id == end_id:
                    return path + [neighbor_id]
                
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return None
    
    def _calculate_chain_strength(self, path: List[str]) -> float:
        """
        Berechne die Stärke einer Übertragungskette.
        
        Args:
            path: Liste der Node-IDs im Pfad
            
        Returns:
            Stärke (0-1)
        """
        if len(path) < 2:
            return 0.0
        
        # Durchschnittliche Edge-Gewichtung entlang des Pfads
        total_weight = 0.0
        edge_count = 0
        
        for i in range(len(path) - 1):
            # Finde Edge zwischen path[i] und path[i+1]
            for edge in self.graph.edges:
                if (edge.source == path[i] and edge.target == path[i+1]) or \
                   (edge.bidirectional and edge.source == path[i+1] and edge.target == path[i]):
                    total_weight += edge.weight
                    edge_count += 1
                    break
        
        avg_weight = total_weight / edge_count if edge_count > 0 else 0.0
        
        # Längen-Strafe: Längere Pfade sind schwächer
        length_penalty = 1.0 / (len(path) - 1)
        
        return avg_weight * length_penalty
    
    def _create_transmission_chain(self, start_id: str, end_id: str, 
                                    path: List[str], strength: float) -> TransmissionChain:
        """
        Erstelle ein TransmissionChain-Objekt.
        
        Args:
            start_id: Start-Node ID
            end_id: Ziel-Node ID
            path: Liste der Node-IDs
            strength: Stärke der Kette
            
        Returns:
            TransmissionChain-Objekt
        """
        # Sammle Edge-IDs im Pfad
        path_edges = []
        for i in range(len(path) - 1):
            for edge in self.graph.edges:
                if (edge.source == path[i] and edge.target == path[i+1]) or \
                   (edge.bidirectional and edge.source == path[i+1] and edge.target == path[i]):
                    path_edges.append(edge.id)
                    break
        
        # Sammle Perioden
        periods = set()
        for node_id in path:
            node = self.graph.get_node(node_id)
            if node:
                periods.update(node.periods)
        
        # Bestimme Typ
        if len(path) == 2:
            chain_type = TransmissionChain.Type.DIRECT
        elif len(periods) > 1:
            chain_type = TransmissionChain.Type.TEMPORAL
        else:
            # Prüfe auf Cross-Domain
            domains = set()
            for node_id in path:
                node = self.graph.get_node(node_id)
                if node:
                    domains.update(node.domains)
            
            if len(domains) > 1:
                chain_type = TransmissionChain.Type.CROSS_DOMAIN
            else:
                chain_type = TransmissionChain.Type.MULTI_HOP
        
        return TransmissionChain(
            id=f"chain_{start_id}_{end_id}",
            start_node=start_id,
            end_node=end_id,
            path=path,
            path_edges=path_edges,
            strength=strength,
            periods_covered=periods,
            transmission_type=chain_type,
        )
    
    # ==================== Main Analysis ====================
    
    def analyze(self, clustering_algorithm: str = "louvain",
                anomaly_method: str = "statistical") -> AnalysisReport:
        """
        Führe die komplette Analyse des Knowledge Graphs durch.
        
        Args:
            clustering_algorithm: Algorithmus für Clustering
            anomaly_method: Methode für Anomalie-Erkennung
            
        Returns:
            Vollständiger AnalysisReport
        """
        report = AnalysisReport()
        
        # Graph-Statistiken
        report.graph_stats = self.graph.get_graph_stats()
        
        # Clustering
        report.clusters = self.detect_clusters(algorithm=clustering_algorithm)
        
        # Anomalie-Erkennung
        report.anomalies = self.detect_anomalies(method=anomaly_method)
        
        # Zentralitäts-Analyse
        report.centralities = self.calculate_centralities()
        
        # Temporale Analyse
        report.concept_evolutions = self.analyze_concept_evolution()
        
        # Übertragungsketten
        report.transmission_chains = self.detect_transmission_chains()
        
        # Generiere Insights
        report.insights = self._generate_insights(report)
        
        return report
    
    def _generate_insights(self, report: AnalysisReport) -> List[str]:
        """
        Generiere automatische Erkenntnisse aus dem Report.
        
        Args:
            report: Der AnalysisReport
            
        Returns:
            Liste von Insight-Strings
        """
        insights = []
        
        # Insight 1: Zentrale Konzepte
        if report.centralities:
            top_central = sorted(report.centralities, key=lambda x: x.overall_score, reverse=True)[:3]
            if top_central:
                node_labels = []
                for cent in top_central:
                    node = self.graph.get_node(cent.node_id)
                    if node:
                        node_labels.append(node.label)
                insights.append(f"Zentrale Konzepte: {', '.join(node_labels)}")
        
        # Insight 2: Cluster-Struktur
        if report.clusters:
            insights.append(f"Wissenslandkarte zeigt {len(report.clusters)} distincte Cluster")
            
            # Domänen-Verteilung
            domain_counts: Dict[str, int] = {}
            for cluster in report.clusters:
                if cluster.domain:
                    domain_counts[cluster.domain.value] = domain_counts.get(cluster.domain.value, 0) + 1
            
            if domain_counts:
                top_domain = max(domain_counts.items(), key=lambda x: x[1])
                insights.append(f"Dominante Domäne: {top_domain[0]} ({top_domain[1]} Cluster)")
        
        # Insight 3: Anomalien
        if report.anomalies:
            critical = [a for a in report.anomalies if a.score > 0.8]
            if critical:
                insights.append(f"{len(critical)} kritische Anomalien erkannt - Überprüfung empfohlen")
        
        # Insight 4: Übertragungsketten
        if report.transmission_chains:
            temporal_chains = [c for c in report.transmission_chains 
                              if c.transmission_type == TransmissionChain.Type.TEMPORAL]
            if temporal_chains:
                insights.append(f"{len(temporal_chains)} zeitliche Wissensübertragungen identifiziert")
        
        # Insight 5: Evolution
        if report.concept_evolutions:
            evolving = [e for e in report.concept_evolutions if len(e.timeline) > 1]
            if evolving:
                insights.append(f"{len(evolving)} Konzepte zeigen evolutionäre Entwicklung")
        
        return insights


# ==================== Convenience Functions ====================

def analyze_graph(graph: KnowledgeGraph, 
                  clustering_algorithm: str = "louvain",
                  anomaly_method: str = "statistical") -> AnalysisReport:
    """
    Analysiere einen Knowledge Graph (Convenience-Funktion).
    
    Args:
        graph: Der zu analysierende Knowledge Graph
        clustering_algorithm: Algorithmus für Clustering
        anomaly_method: Methode für Anomalie-Erkennung
        
    Returns:
        Vollständiger AnalysisReport
    """
    analyzer = KnowledgeAnalyzer(graph)
    return analyzer.analyze(clustering_algorithm, anomaly_method)


def load_and_analyze(filepath: str,
                     clustering_algorithm: str = "louvain",
                     anomaly_method: str = "statistical") -> AnalysisReport:
    """
    Lade einen Knowledge Graph aus Datei und analysiere ihn.
    
    Args:
        filepath: Pfad zur Graph-JSON-Datei
        clustering_algorithm: Algorithmus für Clustering
        anomaly_method: Methode für Anomalie-Erkennung
        
    Returns:
        Vollständiger AnalysisReport
    """
    graph = KnowledgeGraph.load_from_file(filepath)
    return analyze_graph(graph, clustering_algorithm, anomaly_method)


if __name__ == "__main__":
    # Demo: Erstelle und analysiere einen Beispiel-Graph
    print("Knowledge Archaeology - Analyzer Demo")
    print("=" * 50)
    
    # Erstelle einen einfachen Test-Graph
    graph = KnowledgeGraph()
    
    # Füge Konzept-Nodes hinzu
    concepts = [
        ("concept_alchemy", "Alchemy", {Domain.ALCHEMY}, {"Ancient", "Medieval", "Renaissance"}),
        ("concept_hermeticism", "Hermeticism", {Domain.HERMETICISM}, {"Ancient", "Renaissance"}),
        ("concept_kabbalah", "Kabbalah", {Domain.KABBALAH}, {"Medieval", "Renaissance"}),
        ("concept_gnosis", "Gnosis", {Domain.GNOSIS}, {"Ancient", "Medieval"}),
        ("concept_astrology", "Astrology", {Domain.ASTROLOGY}, {"Ancient", "Medieval", "Renaissance"}),
    ]
    
    for node_id, label, domains, periods in concepts:
        node = Node(
            id=node_id,
            label=label,
            node_type=NodeType.CONCEPT,
            domains=domains,
            periods=periods,
        )
        graph.add_node(node)
    
    # Füge Verbindungen hinzu
    edges = [
        ("concept_alchemy", "concept_hermeticism", EdgeType.DERIVED_FROM, 0.8),
        ("concept_alchemy", "concept_astrology", EdgeType.RELATES_TO, 0.6),
        ("concept_hermeticism", "concept_gnosis", EdgeType.INFLUENCED, 0.7),
        ("concept_kabbalah", "concept_hermeticism", EdgeType.RELATES_TO, 0.5),
        ("concept_gnosis", "concept_kabbalah", EdgeType.SIMILAR_TO, 0.4),
    ]
    
    for source, target, edge_type, weight in edges:
        edge = Edge(source=source, target=target, edge_type=edge_type, weight=weight)
        graph.add_edge(edge)
    
    # Analysiere
    analyzer = KnowledgeAnalyzer(graph)
    report = analyzer.analyze()
    
    # Zeige Ergebnisse
    print(f"\nGraph-Statistiken:")
    print(f"  Nodes: {report.graph_stats.get('node_count', 0)}")
    print(f"  Edges: {report.graph_stats.get('edge_count', 0)}")
    
    print(f"\nCluster ({len(report.clusters)}):")
    for cluster in report.clusters:
        print(f"  - {cluster.label}: {len(cluster.node_ids)} Nodes (Kohärenz: {cluster.coherence})")
    
    print(f"\nAnomalien ({len(report.anomalies)}):")
    for anomaly in report.anomalies[:5]:
        print(f"  - {anomaly.anomaly_type.value}: {anomaly.description}")
    
    print(f"\nZentrale Konzepte:")
    top_central = sorted(report.centralities, key=lambda x: x.overall_score, reverse=True)[:3]
    for cent in top_central:
        node = graph.get_node(cent.node_id)
        if node:
            print(f"  - {node.label}: {cent.overall_score:.3f}")
    
    print(f"\nInsights:")
    for insight in report.insights:
        print(f"  • {insight}")
    
    print("\n" + "=" * 50)
    print("Analyse abgeschlossen!")
