"""
Knowledge Archaeology - Cartographer Module

Phase 3: CARTOGRAPHY - Kartographie des Wissens

Dieses Modul baut einen Knowledge Graph aus den extrahierten Wissensfragmenten.
Es erstellt Nodes (Konzepte, Entitäten) und Edges (Beziehungen) mit Gewichtungen.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Set, Tuple, Any
import json
import re
from collections import defaultdict
from pathlib import Path


class NodeType(Enum):
    """Typen von Nodes im Knowledge Graph."""
    CONCEPT = "concept"           # Abstraktes Konzept (z.B. "Alchemy")
    ENTITY = "entity"             # Konkrete Entität (Person, Ort, Werk)
    DOMAIN = "domain"             # Wissensdomäne
    PERIOD = "period"             # Zeitperiode
    SOURCE = "source"             # Quelle/Referenz


class EdgeType(Enum):
    """Typen von Edges (Beziehungen) im Knowledge Graph."""
    RELATES_TO = "relates_to"           # Allgemeine Beziehung
    INFLUENCED = "influenced"           # Einfluss auf
    DERIVED_FROM = "derived_from"       # Abgeleitet von
    PART_OF = "part_of"                 # Teil von
    MENTIONS = "mentions"               # Erwähnt
    BELONGS_TO = "belongs_to"           # Gehört zu
    TEMPORAL_LINK = "temporal_link"     # Zeitliche Verbindung
    SIMILAR_TO = "similar_to"           # Ähnlich zu


class Domain(Enum):
    """Wissensdomänen für die Klassifikation."""
    HERMETICISM = "hermeticism"
    ALCHEMY = "alchemy"
    KABBALAH = "kabbalah"
    GNOSIS = "gnosis"
    MYSTICISM = "mysticism"
    PHILOSOPHY = "philosophy"
    ASTROLOGY = "astrology"
    MAGIC = "magic"
    RELIGION = "religion"
    SYMBOLISM = "symbolism"
    HISTORY = "history"
    SCIENCE = "science"
    UNKNOWN = "unknown"


@dataclass
class Node:
    """
    Ein Node im Knowledge Graph.
    
    Attributes:
        id: Eindeutige Identifikation
        label: Anzeigename
        node_type: Typ des Nodes
        properties: Zusätzliche Eigenschaften
        domains: Zugeordnete Domänen
        periods: Zugeordnete Zeitperioden
        confidence: Zuverlässigkeit (0-1)
    """
    id: str
    label: str
    node_type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    domains: Set[Domain] = field(default_factory=set)
    periods: Set[str] = field(default_factory=set)
    confidence: float = 1.0
    
    def __post_init__(self):
        """Validiere und normalisiere Werte."""
        self.confidence = max(0.0, min(1.0, self.confidence))
        self.domains = set(self.domains) if self.domains else set()
        self.periods = set(self.periods) if self.periods else set()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere Node zu Dictionary."""
        return {
            "id": self.id,
            "label": self.label,
            "node_type": self.node_type.value,
            "properties": self.properties,
            "domains": [d.value for d in self.domains],
            "periods": list(self.periods),
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        """Erstelle Node aus Dictionary."""
        return cls(
            id=data["id"],
            label=data["label"],
            node_type=NodeType(data["node_type"]),
            properties=data.get("properties", {}),
            domains={Domain(d) for d in data.get("domains", [])},
            periods=set(data.get("periods", [])),
            confidence=data.get("confidence", 1.0),
        )


@dataclass
class Edge:
    """
    Eine Edge (Beziehung) im Knowledge Graph.
    
    Attributes:
        source: ID des Quell-Nodes
        target: ID des Ziel-Nodes
        edge_type: Typ der Beziehung
        weight: Stärke der Verbindung (0-1)
        properties: Zusätzliche Eigenschaften
        bidirectional: Ob die Beziehung bidirektional ist
    """
    source: str
    target: str
    edge_type: EdgeType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    bidirectional: bool = False
    
    def __post_init__(self):
        """Validiere Gewichtung."""
        self.weight = max(0.0, min(1.0, self.weight))
    
    @property
    def id(self) -> str:
        """Generiere eindeutige Edge-ID."""
        return f"{self.source}--{self.edge_type.value}--{self.target}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere Edge zu Dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type.value,
            "weight": self.weight,
            "properties": self.properties,
            "bidirectional": self.bidirectional,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        """Erstelle Edge aus Dictionary."""
        return cls(
            source=data["source"],
            target=data["target"],
            edge_type=EdgeType(data["edge_type"]),
            weight=data.get("weight", 1.0),
            properties=data.get("properties", {}),
            bidirectional=data.get("bidirectional", False),
        )


@dataclass
class TemporalLayer:
    """
    Eine Zeitschicht im Knowledge Graph.
    
    Attributes:
        period: Name der Zeitperiode
        start_year: Startjahr (optional)
        end_year: Endjahr (optional)
        node_ids: IDs der Nodes in dieser Schicht
        description: Beschreibung der Schicht
    """
    period: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    node_ids: Set[str] = field(default_factory=set)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere zu Dictionary."""
        return {
            "period": self.period,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "node_ids": list(self.node_ids),
            "description": self.description,
        }


class KnowledgeGraph:
    """
    Der Knowledge Graph für das Knowledge Archaeology System.
    
    Speichert Nodes, Edges und Zeitschichten. Bietet Methoden für
    Graph-Operationen, Serialisierung und Analyse.
    """
    
    # Mapping von Konzepten zu Domänen
    CONCEPT_DOMAIN_MAP: Dict[str, Domain] = {
        "hermeticism": Domain.HERMETICISM,
        "alchemy": Domain.ALCHEMY,
        "kabbalah": Domain.KABBALAH,
        "gnosis": Domain.GNOSIS,
        "mysticism": Domain.MYSTICISM,
        "philosophy": Domain.PHILOSOPHY,
        "astrology": Domain.ASTROLOGY,
        "magic": Domain.MAGIC,
        "religion": Domain.RELIGION,
        "symbolism": Domain.SYMBOLISM,
    }
    
    # Zeitperioden mit Jahreszahlen
    PERIOD_TIMELINE: Dict[str, Tuple[Optional[int], Optional[int]]] = {
        "Ancient": (None, 500),
        "Medieval": (500, 1500),
        "Renaissance": (1500, 1700),
        "Modern": (1700, None),
        "Unknown": (None, None),
    }
    
    def __init__(self):
        """Initialisiere einen leeren Knowledge Graph."""
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[str, Edge] = {}
        self._temporal_layers: Dict[str, TemporalLayer] = {}
        self._node_edges: Dict[str, Set[str]] = defaultdict(set)
        self._domain_index: Dict[Domain, Set[str]] = defaultdict(set)
    
    # ==================== Node Management ====================
    
    def add_node(self, node: Node) -> str:
        """
        Füge einen Node zum Graph hinzu.
        
        Args:
            node: Der hinzuzufügende Node
            
        Returns:
            ID des hinzugefügten Nodes
        """
        self._nodes[node.id] = node
        
        # Indexiere nach Domänen
        for domain in node.domains:
            self._domain_index[domain].add(node.id)
        
        # Füge zu Zeitschichten hinzu
        for period in node.periods:
            self._add_to_temporal_layer(node.id, period)
        
        return node.id
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Hole einen Node anhand seiner ID."""
        return self._nodes.get(node_id)
    
    def has_node(self, node_id: str) -> bool:
        """Prüfe ob ein Node existiert."""
        return node_id in self._nodes
    
    def remove_node(self, node_id: str) -> bool:
        """
        Entferne einen Node und alle seine Edges.
        
        Args:
            node_id: ID des zu entfernenden Nodes
            
        Returns:
            True wenn entfernt, False wenn nicht gefunden
        """
        if node_id not in self._nodes:
            return False
        
        # Entferne alle verbundenen Edges
        edge_ids = list(self._node_edges[node_id])
        for edge_id in edge_ids:
            self.remove_edge_by_id(edge_id)
        
        # Entferne aus Domänen-Index
        node = self._nodes[node_id]
        for domain in node.domains:
            self._domain_index[domain].discard(node.id)
        
        # Entferne aus Zeitschichten
        for period in node.periods:
            if period in self._temporal_layers:
                self._temporal_layers[period].node_ids.discard(node_id)
        
        del self._nodes[node_id]
        return True
    
    @property
    def nodes(self) -> List[Node]:
        """Alle Nodes im Graph."""
        return list(self._nodes.values())
    
    @property
    def node_count(self) -> int:
        """Anzahl der Nodes."""
        return len(self._nodes)
    
    # ==================== Edge Management ====================
    
    def add_edge(self, edge: Edge) -> str:
        """
        Füge eine Edge zum Graph hinzu.
        
        Args:
            edge: Die hinzuzufügende Edge
            
        Returns:
            ID der hinzugefügten Edge
        """
        # Validiere Node-Existenz
        if edge.source not in self._nodes or edge.target not in self._nodes:
            raise ValueError(f"Source or target node does not exist: {edge.source} -> {edge.target}")
        
        self._edges[edge.id] = edge
        self._node_edges[edge.source].add(edge.id)
        self._node_edges[edge.target].add(edge.id)
        
        return edge.id
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Hole eine Edge anhand ihrer ID."""
        return self._edges.get(edge_id)
    
    def get_edges_between(self, source_id: str, target_id: str) -> List[Edge]:
        """Hole alle Edges zwischen zwei Nodes."""
        result = []
        for edge_id in self._node_edges.get(source_id, set()):
            edge = self._edges.get(edge_id)
            if edge and edge.target == target_id:
                result.append(edge)
        return result
    
    def remove_edge_by_id(self, edge_id: str) -> bool:
        """
        Entferne eine Edge anhand ihrer ID.
        
        Args:
            edge_id: ID der zu entfernenden Edge
            
        Returns:
            True wenn entfernt, False wenn nicht gefunden
        """
        if edge_id not in self._edges:
            return False
        
        edge = self._edges[edge_id]
        self._node_edges[edge.source].discard(edge_id)
        self._node_edges[edge.target].discard(edge_id)
        del self._edges[edge_id]
        return True
    
    @property
    def edges(self) -> List[Edge]:
        """Alle Edges im Graph."""
        return list(self._edges.values())
    
    @property
    def edge_count(self) -> int:
        """Anzahl der Edges."""
        return len(self._edges)
    
    # ==================== Graph Queries ====================
    
    def get_neighbors(self, node_id: str) -> List[Node]:
        """
        Hole alle Nachbar-Nodes.
        
        Args:
            node_id: ID des Ausgangs-Nodes
            
        Returns:
            Liste der Nachbar-Nodes
        """
        if node_id not in self._nodes:
            return []
        
        neighbor_ids = set()
        for edge_id in self._node_edges.get(node_id, set()):
            edge = self._edges.get(edge_id)
            if edge:
                if edge.source == node_id:
                    neighbor_ids.add(edge.target)
                elif edge.bidirectional or edge.target == node_id:
                    neighbor_ids.add(edge.source)
        
        return [self._nodes[nid] for nid in neighbor_ids if nid in self._nodes]
    
    def get_connected_nodes(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[Tuple[Node, Edge]]:
        """
        Hole alle verbundenen Nodes mit ihren Edges.
        
        Args:
            node_id: ID des Ausgangs-Nodes
            edge_type: Optionaler Filter nach Edge-Typ
            
        Returns:
            Liste von (Node, Edge) Tupeln
        """
        if node_id not in self._nodes:
            return []
        
        result = []
        for edge_id in self._node_edges.get(node_id, set()):
            edge = self._edges.get(edge_id)
            if not edge:
                continue
            
            if edge_type and edge.edge_type != edge_type:
                continue
            
            # Bestimme den anderen Node
            other_id = edge.target if edge.source == node_id else edge.source
            if other_id in self._nodes:
                result.append((self._nodes[other_id], edge))
        
        return result
    
    def get_nodes_by_domain(self, domain: Domain) -> List[Node]:
        """Hole alle Nodes einer Domäne."""
        node_ids = self._domain_index.get(domain, set())
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """Hole alle Nodes eines Typs."""
        return [n for n in self._nodes.values() if n.node_type == node_type]
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 5) -> Optional[List[Edge]]:
        """
        Finde einen Pfad zwischen zwei Nodes (BFS).
        
        Args:
            start_id: Start-Node ID
            end_id: Ziel-Node ID
            max_depth: Maximale Suchtiefe
            
        Returns:
            Liste der Edges im Pfad oder None
        """
        if start_id not in self._nodes or end_id not in self._nodes:
            return None
        
        if start_id == end_id:
            return []
        
        visited = {start_id}
        queue = [(start_id, [])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if len(path) >= max_depth:
                continue
            
            for edge_id in self._node_edges.get(current_id, set()):
                edge = self._edges.get(edge_id)
                if not edge:
                    continue
                
                next_id = edge.target if edge.source == current_id else edge.source
                
                if next_id == end_id:
                    return path + [edge]
                
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [edge]))
        
        return None
    
    # ==================== Temporal Layers ====================
    
    def _add_to_temporal_layer(self, node_id: str, period: str) -> None:
        """Füge einen Node zu einer Zeitschicht hinzu."""
        if period not in self._temporal_layers:
            # Erstelle neue Schicht
            years = self.PERIOD_TIMELINE.get(period, (None, None))
            self._temporal_layers[period] = TemporalLayer(
                period=period,
                start_year=years[0],
                end_year=years[1],
            )
        
        self._temporal_layers[period].node_ids.add(node_id)
    
    def get_temporal_layer(self, period: str) -> Optional[TemporalLayer]:
        """Hole eine Zeitschicht."""
        return self._temporal_layers.get(period)
    
    @property
    def temporal_layers(self) -> List[TemporalLayer]:
        """Alle Zeitschichten."""
        return list(self._temporal_layers.values())
    
    def get_nodes_in_period(self, period: str) -> List[Node]:
        """Hole alle Nodes in einer Zeitperiode."""
        layer = self._temporal_layers.get(period)
        if not layer:
            return []
        return [self._nodes[nid] for nid in layer.node_ids if nid in self._nodes]
    
    # ==================== Analysis ====================
    
    def calculate_centrality(self, node_id: str) -> float:
        """
        Berechne die Zentralität eines Nodes (Degree Centrality).
        
        Args:
            node_id: ID des Nodes
            
        Returns:
            Zentralitäts-Score (0-1)
        """
        if node_id not in self._nodes or self.node_count <= 1:
            return 0.0
        
        degree = len(self._node_edges.get(node_id, set()))
        max_degree = self.node_count - 1
        
        return degree / max_degree if max_degree > 0 else 0.0
    
    def calculate_connection_strength(self, source_id: str, target_id: str) -> float:
        """
        Berechne die Verbindungsstärke zwischen zwei Nodes.
        
        Berücksichtigt:
        - Direkte Edges
        - Gewichtungen
        - Gemeinsame Nachbarn
        
        Args:
            source_id: ID des Quell-Nodes
            target_id: ID des Ziel-Nodes
            
        Returns:
            Verbindungsstärke (0-1)
        """
        if source_id not in self._nodes or target_id not in self._nodes:
            return 0.0
        
        if source_id == target_id:
            return 1.0
        
        strength = 0.0
        
        # Direkte Verbindungen
        direct_edges = self.get_edges_between(source_id, target_id)
        direct_edges.extend(self.get_edges_between(target_id, source_id))
        
        for edge in direct_edges:
            strength += edge.weight * 0.5  # Direkte Verbindung = 50% max
        
        # Gemeinsame Nachbarn (Jaccard-ähnlich)
        source_neighbors = set(n.id for n in self.get_neighbors(source_id))
        target_neighbors = set(n.id for n in self.get_neighbors(target_id))
        
        if source_neighbors and target_neighbors:
            common = source_neighbors & target_neighbors
            union = source_neighbors | target_neighbors
            if union:
                jaccard = len(common) / len(union)
                strength += jaccard * 0.3  # Gemeinsame Nachbarn = 30% max
        
        # Gleiche Domänen
        source_node = self._nodes[source_id]
        target_node = self._nodes[target_id]
        
        if source_node.domains and target_node.domains:
            common_domains = source_node.domains & target_node.domains
            union_domains = source_node.domains | target_node.domains
            if union_domains:
                domain_sim = len(common_domains) / len(union_domains)
                strength += domain_sim * 0.2  # Domänen-Ähnlichkeit = 20% max
        
        return min(strength, 1.0)
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Erstelle Statistiken über den Graph.
        
        Returns:
            Dictionary mit Statistiken
        """
        stats = {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes_by_type": {},
            "nodes_by_domain": {},
            "nodes_by_period": {},
            "avg_degree": 0.0,
            "density": 0.0,
        }
        
        # Nodes nach Typ
        for node_type in NodeType:
            count = len(self.get_nodes_by_type(node_type))
            if count > 0:
                stats["nodes_by_type"][node_type.value] = count
        
        # Nodes nach Domäne
        for domain in Domain:
            count = len(self.get_nodes_by_domain(domain))
            if count > 0:
                stats["nodes_by_domain"][domain.value] = count
        
        # Nodes nach Periode
        for period, layer in self._temporal_layers.items():
            stats["nodes_by_period"][period] = len(layer.node_ids)
        
        # Durchschnittlicher Grad
        if self.node_count > 0:
            total_degree = sum(len(self._node_edges.get(n.id, set())) for n in self._nodes.values())
            stats["avg_degree"] = round(total_degree / self.node_count, 2)
        
        # Dichte
        if self.node_count > 1:
            max_edges = self.node_count * (self.node_count - 1)
            stats["density"] = round(self.edge_count / max_edges, 4)
        
        return stats
    
    # ==================== Serialization ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialisiere den Graph zu einem Dictionary.
        
        Returns:
            Dictionary-Repräsentation des Graphs
        """
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges.values()],
            "temporal_layers": [l.to_dict() for l in self._temporal_layers.values()],
            "stats": self.get_graph_stats(),
        }
    
    def to_json(self, indent: int = 2) -> str:
        """
        Serialisiere den Graph zu JSON.
        
        Args:
            indent: Einrückung für lesbares JSON
            
        Returns:
            JSON-String
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeGraph":
        """
        Erstelle Graph aus Dictionary.
        
        Args:
            data: Dictionary mit Graph-Daten
            
        Returns:
            KnowledgeGraph-Instanz
        """
        graph = cls()
        
        # Lade Nodes
        for node_data in data.get("nodes", []):
            node = Node.from_dict(node_data)
            graph.add_node(node)
        
        # Lade Edges
        for edge_data in data.get("edges", []):
            edge = Edge.from_dict(edge_data)
            try:
                graph.add_edge(edge)
            except ValueError:
                # Ignoriere Edges zu nicht-existenten Nodes
                pass
        
        return graph
    
    @classmethod
    def from_json(cls, json_str: str) -> "KnowledgeGraph":
        """
        Erstelle Graph aus JSON-String.
        
        Args:
            json_str: JSON-String mit Graph-Daten
            
        Returns:
            KnowledgeGraph-Instanz
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, filepath: str) -> None:
        """
        Speichere den Graph in eine JSON-Datei.
        
        Args:
            filepath: Pfad zur Zieldatei
        """
        path = Path(filepath)
        path.write_text(self.to_json(), encoding="utf-8")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "KnowledgeGraph":
        """
        Lade einen Graph aus einer JSON-Datei.
        
        Args:
            filepath: Pfad zur Datei
            
        Returns:
            KnowledgeGraph-Instanz
        """
        path = Path(filepath)
        return cls.from_json(path.read_text(encoding="utf-8"))


# Import für Type-Checking (vermeidet zirkuläre Importe)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from excavator import Fragment, KnowledgeExcavator


class KnowledgeCartographer:
    """
    Hauptklasse für die Kartographie-Phase des Knowledge Archaeology Systems.
    
    Baut einen Knowledge Graph aus Wissensfragmenten (Phase 2 Output) auf.
    Führt Domänen-Klassifikation, Zeitschichten-Einordnung und
    Verbindungs-Stärken-Berechnung durch.
    """
    
    # Entitäts-Typen für die Erkennung
    ENTITY_TYPES = ["person", "place", "work"]
    
    def __init__(self, graph: Optional[KnowledgeGraph] = None):
        """
        Initialisiere den Cartographer.
        
        Args:
            graph: Optionaler bestehender Knowledge Graph
        """
        self.graph = graph if graph else KnowledgeGraph()
        self._concept_nodes: Dict[str, str] = {}  # concept_name -> node_id
        self._entity_nodes: Dict[str, str] = {}   # entity_name -> node_id
        self._period_nodes: Dict[str, str] = {}   # period_name -> node_id
        self._source_nodes: Dict[str, str] = {}   # source_name -> node_id
    
    def map_fragments(self, fragments: List["Fragment"]) -> KnowledgeGraph:
        """
        Hauptmethode: Baue den Knowledge Graph aus Fragmenten.
        
        Args:
            fragments: Liste der Wissensfragmente aus Phase 2
            
        Returns:
            Der aufgebaute Knowledge Graph
        """
        # Phase 1: Erstelle alle Nodes
        for fragment in fragments:
            self._process_fragment_nodes(fragment)
        
        # Phase 2: Erstelle Edges zwischen Nodes
        for fragment in fragments:
            self._process_fragment_edges(fragment)
        
        # Phase 3: Berechne Verbindungsstärken
        self._calculate_all_connection_strengths()
        
        return self.graph
    
    def _process_fragment_nodes(self, fragment: "Fragment") -> None:
        """
        Erstelle Nodes aus einem Fragment.
        
        Args:
            fragment: Das zu verarbeitende Fragment
        """
        # 1. Erstelle/Update Konzept-Nodes
        for concept in fragment.concepts:
            self._get_or_create_concept_node(concept)
        
        # 2. Erstelle Quellen-Node
        source_node_id = self._get_or_create_source_node(fragment.source)
        
        # 3. Erstelle Period-Node falls bekannt
        period_name = fragment.period.value if hasattr(fragment.period, 'value') else str(fragment.period)
        if period_name != "Unknown":
            self._get_or_create_period_node(period_name)
    
    def _process_fragment_edges(self, fragment: "Fragment") -> None:
        """
        Erstelle Edges aus einem Fragment.
        
        Args:
            fragment: Das zu verarbeitende Fragment
        """
        # Hole Quellen-Node
        source_node_id = self._source_nodes.get(fragment.source)
        if not source_node_id:
            return
        
        period_name = fragment.period.value if hasattr(fragment.period, 'value') else str(fragment.period)
        
        # Verbinde Quelle mit Konzepten
        for concept in fragment.concepts:
            concept_node_id = self._concept_nodes.get(concept)
            if concept_node_id:
                # Edge: Quelle -> Konzept (MENTIONS)
                edge = Edge(
                    source=source_node_id,
                    target=concept_node_id,
                    edge_type=EdgeType.MENTIONS,
                    weight=fragment.confidence,
                    properties={"context": fragment.text[:200]}
                )
                try:
                    self.graph.add_edge(edge)
                except ValueError:
                    pass
                
                # Edge: Konzept -> Periode (TEMPORAL_LINK)
                if period_name != "Unknown":
                    period_node_id = self._period_nodes.get(period_name)
                    if period_node_id:
                        edge = Edge(
                            source=concept_node_id,
                            target=period_node_id,
                            edge_type=EdgeType.TEMPORAL_LINK,
                            weight=fragment.confidence * 0.8,
                        )
                        try:
                            self.graph.add_edge(edge)
                        except ValueError:
                            pass
        
        # Verbinde Konzepte untereinander (RELATES_TO)
        concepts = list(fragment.concepts)
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                node1_id = self._concept_nodes.get(concept1)
                node2_id = self._concept_nodes.get(concept2)
                if node1_id and node2_id:
                    edge = Edge(
                        source=node1_id,
                        target=node2_id,
                        edge_type=EdgeType.RELATES_TO,
                        weight=fragment.confidence * 0.6,
                        bidirectional=True,
                    )
                    try:
                        self.graph.add_edge(edge)
                    except ValueError:
                        pass
    
    def _get_or_create_concept_node(self, concept: str) -> str:
        """
        Hole oder erstelle einen Konzept-Node.
        
        Args:
            concept: Name des Konzepts
            
        Returns:
            ID des Nodes
        """
        if concept in self._concept_nodes:
            return self._concept_nodes[concept]
        
        # Bestimme Domäne
        domain = self._classify_concept_domain(concept)
        
        # Erstelle Node
        node_id = f"concept_{concept.lower().replace(' ', '_')}"
        node = Node(
            id=node_id,
            label=concept.capitalize(),
            node_type=NodeType.CONCEPT,
            domains={domain},
            properties={"category": "concept"}
        )
        
        self.graph.add_node(node)
        self._concept_nodes[concept] = node_id
        return node_id
    
    def _get_or_create_entity_node(self, entity_type: str, entity_name: str, 
                                   domains: Optional[Set[Domain]] = None) -> str:
        """
        Hole oder erstelle einen Entitäts-Node.
        
        Args:
            entity_type: Typ der Entität (person, place, work)
            entity_name: Name der Entität
            domains: Optionale Domänen-Zuordnung
            
        Returns:
            ID des Nodes
        """
        key = f"{entity_type}:{entity_name}"
        if key in self._entity_nodes:
            return self._entity_nodes[key]
        
        node_id = f"entity_{entity_type}_{entity_name.lower().replace(' ', '_')}"
        node = Node(
            id=node_id,
            label=entity_name,
            node_type=NodeType.ENTITY,
            domains=domains or {Domain.UNKNOWN},
            properties={"entity_type": entity_type}
        )
        
        self.graph.add_node(node)
        self._entity_nodes[key] = node_id
        return node_id
    
    def _get_or_create_period_node(self, period: str) -> str:
        """
        Hole oder erstelle einen Period-Node.
        
        Args:
            period: Name der Zeitperiode
            
        Returns:
            ID des Nodes
        """
        if period in self._period_nodes:
            return self._period_nodes[period]
        
        node_id = f"period_{period.lower()}"
        
        # Hole Jahreszahlen
        years = KnowledgeGraph.PERIOD_TIMELINE.get(period, (None, None))
        
        node = Node(
            id=node_id,
            label=period,
            node_type=NodeType.PERIOD,
            periods={period},
            properties={
                "start_year": years[0],
                "end_year": years[1]
            }
        )
        
        self.graph.add_node(node)
        self._period_nodes[period] = node_id
        return node_id
    
    def _get_or_create_source_node(self, source: str) -> str:
        """
        Hole oder erstelle einen Source-Node.
        
        Args:
            source: Name/URL der Quelle
            
        Returns:
            ID des Nodes
        """
        if source in self._source_nodes:
            return self._source_nodes[source]
        
        # Erstelle kurze ID aus Source
        source_id = f"source_{hash(source) % 10000000:07d}"
        
        node = Node(
            id=source_id,
            label=source[:50] if len(source) > 50 else source,
            node_type=NodeType.SOURCE,
            properties={"full_source": source}
        )
        
        self.graph.add_node(node)
        self._source_nodes[source] = source_id
        return source_id
    
    def _classify_concept_domain(self, concept: str) -> Domain:
        """
        Klassifiziere ein Konzept in eine Domäne.
        
        Args:
            concept: Name des Konzepts
            
        Returns:
            Die zugeordnete Domäne
        """
        concept_lower = concept.lower()
        return KnowledgeGraph.CONCEPT_DOMAIN_MAP.get(concept_lower, Domain.UNKNOWN)
    
    def add_entities_from_fragment(self, fragment: "Fragment", 
                                    entities: Dict[str, List[str]]) -> None:
        """
        Füge Entitäten aus einem Fragment zum Graph hinzu.
        
        Args:
            fragment: Das Quell-Fragment
            entities: Dictionary mit Entitäten (person, place, work)
        """
        # Bestimme Domänen aus Fragment
        fragment_domains = {self._classify_concept_domain(c) for c in fragment.concepts}
        fragment_domains.discard(Domain.UNKNOWN)
        
        if not fragment_domains:
            fragment_domains = {Domain.UNKNOWN}
        
        # Erstelle Entitäts-Nodes
        for entity_type, entity_list in entities.items():
            for entity_name in entity_list:
                entity_node_id = self._get_or_create_entity_node(
                    entity_type, entity_name, fragment_domains
                )
                
                # Verbinde Entität mit Konzepten
                for concept in fragment.concepts:
                    concept_node_id = self._concept_nodes.get(concept)
                    if concept_node_id:
                        edge = Edge(
                            source=entity_node_id,
                            target=concept_node_id,
                            edge_type=EdgeType.BELONGS_TO,
                            weight=0.7,
                        )
                        try:
                            self.graph.add_edge(edge)
                        except ValueError:
                            pass
    
    def _calculate_all_connection_strengths(self) -> None:
        """
        Berechne Verbindungsstärken für alle Node-Paare.
        Diese Methode kann für Analysen erweitert werden.
        """
        # Die Verbindungsstärken werden on-demand berechnet
        # durch calculate_connection_strength()
        pass
    
    def get_domain_summary(self, domain: Domain) -> Dict[str, Any]:
        """
        Erstelle eine Zusammenfassung für eine Domäne.
        
        Args:
            domain: Die zu analysierende Domäne
            
        Returns:
            Dictionary mit Domänen-Informationen
        """
        nodes = self.graph.get_nodes_by_domain(domain)
        
        # Gruppiere nach Typ
        concepts = [n for n in nodes if n.node_type == NodeType.CONCEPT]
        entities = [n for n in nodes if n.node_type == NodeType.ENTITY]
        
        # Finde zentrale Nodes (hohe Zentralität)
        central_nodes = []
        for node in nodes:
            centrality = self.graph.calculate_centrality(node.id)
            if centrality > 0.3:
                central_nodes.append({
                    "id": node.id,
                    "label": node.label,
                    "centrality": round(centrality, 3)
                })
        
        central_nodes.sort(key=lambda x: x["centrality"], reverse=True)
        
        return {
            "domain": domain.value,
            "total_nodes": len(nodes),
            "concepts": len(concepts),
            "entities": len(entities),
            "central_nodes": central_nodes[:5],
        }
    
    def get_temporal_analysis(self) -> Dict[str, Any]:
        """
        Analysiere die zeitliche Verteilung des Wissens.
        
        Returns:
            Dictionary mit zeitlichen Analysen
        """
        analysis = {
            "periods": {},
            "cross_period_connections": 0,
            "temporal_flow": []
        }
        
        for layer in self.graph.temporal_layers:
            nodes_in_period = self.graph.get_nodes_in_period(layer.period)
            
            # Zähle Konzepte und Entitäten
            concepts = len([n for n in nodes_in_period if n.node_type == NodeType.CONCEPT])
            entities = len([n for n in nodes_in_period if n.node_type == NodeType.ENTITY])
            
            analysis["periods"][layer.period] = {
                "node_count": len(nodes_in_period),
                "concepts": concepts,
                "entities": entities,
                "time_range": (layer.start_year, layer.end_year)
            }
        
        # Finde zeitliche Verbindungen (TEMPORAL_LINK Edges)
        temporal_edges = [e for e in self.graph.edges 
                         if e.edge_type == EdgeType.TEMPORAL_LINK]
        analysis["cross_period_connections"] = len(temporal_edges)
        
        return analysis
    
    def export_for_visualization(self) -> Dict[str, Any]:
        """
        Exportiere den Graph in ein Visualisierungs-Format.
        
        Returns:
            Dictionary im Cytoscape.js kompatiblen Format
        """
        elements = {
            "nodes": [],
            "edges": []
        }
        
        # Farben für Domänen
        domain_colors = {
            Domain.HERMETICISM: "#9C27B0",
            Domain.ALCHEMY: "#FF9800",
            Domain.KABBALAH: "#3F51B5",
            Domain.GNOSIS: "#E91E63",
            Domain.MYSTICISM: "#00BCD4",
            Domain.PHILOSOPHY: "#795548",
            Domain.ASTROLOGY: "#673AB7",
            Domain.MAGIC: "#F44336",
            Domain.RELIGION: "#4CAF50",
            Domain.SYMBOLISM: "#FFC107",
            Domain.UNKNOWN: "#9E9E9E",
        }
        
        # Exportiere Nodes
        for node in self.graph.nodes:
            # Bestimme Farbe nach primärer Domäne
            color = "#9E9E9E"
            if node.domains:
                primary_domain = list(node.domains)[0]
                color = domain_colors.get(primary_domain, "#9E9E9E")
            
            elements["nodes"].append({
                "data": {
                    "id": node.id,
                    "label": node.label,
                    "type": node.node_type.value,
                    "color": color,
                    "domains": [d.value for d in node.domains],
                }
            })
        
        # Exportiere Edges
        for edge in self.graph.edges:
            elements["edges"].append({
                "data": {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.edge_type.value,
                    "weight": edge.weight,
                }
            })
        
        return elements