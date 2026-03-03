"""
Knowledge Archaeology - Excavation Module

Phase 2: Excavation - Ausgrabung von Wissensfragmenten

Dieses Modul extrahiert strukturierte Wissensfragmente aus verschiedenen Quellen
(URLs, Texte) und klassifiziert sie nach Zeitperioden und Konzepten.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Set
import re
from urllib.parse import urlparse


class TimePeriod(Enum):
    """Zeitperioden für die Klassifizierung von Wissensfragmenten."""
    ANCIENT = "Ancient"           # Antike (vor 500 CE)
    MEDIEVAL = "Medieval"         # Mittelalter (500-1500 CE)
    RENAISSANCE = "Renaissance"   # Renaissance (1500-1700 CE)
    MODERN = "Modern"             # Moderne (ab 1700 CE)
    UNKNOWN = "Unknown"           # Unbekannt


@dataclass
class Fragment:
    """
    Ein extrahiertes Wissensfragment.
    
    Attributes:
        text: Der extrahierte Inhalt
        source: Herkunft (URL, Dateiname, etc.)
        period: Zeitperiode des Fragments
        concepts: Liste der erkannten Konzepte
        confidence: Zuverlässigkeit der Extraktion (0-1)
    """
    text: str
    source: str
    period: TimePeriod = TimePeriod.UNKNOWN
    concepts: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def __post_init__(self):
        """Validiere die confidence-Werte."""
        self.confidence = max(0.0, min(1.0, self.confidence))


class KnowledgeExcavator:
    """
    Hauptklasse für die Ausgrabung von Wissensfragmenten.
    
    Extrahiert strukturierte Informationen aus Textquellen und
    klassifiziert sie nach Zeitperioden und Konzepten.
    """
    
    # Konzept-Keywords für die Erkennung
    CONCEPT_PATTERNS: Dict[str, List[str]] = {
        "hermeticism": ["hermetic", "hermes", "hermetism", "hermetic philosophy"],
        "alchemy": ["alchemy", "alchemical", "philosopher's stone", "elixir", "transmutation"],
        "kabbalah": ["kabbalah", "kabbalistic", "tree of life", "sephiroth", "ein sof"],
        "gnosis": ["gnosis", "gnostic", "gnosticism", "divine knowledge"],
        "mysticism": ["mysticism", "mystical", "mystic", "esoteric"],
        "philosophy": ["philosophy", "philosophical", "philosopher"],
        "astrology": ["astrology", "astrological", "zodiac", "horoscope"],
        "magic": ["magic", "magical", "magick", "occult"],
        "religion": ["religion", "religious", "sacred", "divine"],
        "symbolism": ["symbol", "symbolism", "symbolic", "emblem"],
    }
    
    # Entitäten-Muster (Personen, Orte, Werke)
    ENTITY_PATTERNS: Dict[str, List[str]] = {
        "person": [
            r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # Zwei Großbuchstaben-Wörter
            r"\bHermes\s+Trismegistus\b",
            r"\bParacelsus\b",
            r"\bIsaac\s+Newton\b",
            r"\bJohn\s+Dee\b",
        ],
        "place": [
            r"\b[A-Z][a-z]+land\b",  # Endungen wie Egypt, England
            r"\bAlexandria\b",
            r"\bFlorence\b",
            r"\bPrague\b",
        ],
        "work": [
            r"\bCorpus\s+Hermeticum\b",
            r"\bEmerald\s+Tablet\b",
            r"\bKybalion\b",
            r"\b([A-Z][a-z]+\s+)+[IVX]+\b",  # Titel mit römischen Zahlen
        ],
    }
    
    # Zeitperioden-Keywords
    PERIOD_INDICATORS: Dict[TimePeriod, List[str]] = {
        TimePeriod.ANCIENT: [
            "ancient", "antiquity", "egypt", "greece", "rome", "bc", "bce",
            "classical", "pharaonic", "pythagoras", "plato", "aristotle"
        ],
        TimePeriod.MEDIEVAL: [
            "medieval", "middle ages", "byzantine", "islamic golden age",
            "scholasticism", "al-ghazali", "avicenna", "averroes",
            "12th century", "13th century", "14th century"
        ],
        TimePeriod.RENAISSANCE: [
            "renaissance", "humanism", "15th century", "16th century", "17th century",
            "florence", "medici", "ficino", "pico", "bruno", "paracelsus"
        ],
        TimePeriod.MODERN: [
            "modern", "enlightenment", "19th century", "20th century", "21st century",
            "scientific", "psychology", "theosophy", "golden dawn"
        ],
    }
    
    def __init__(self):
        """Initialisiere den Excavator mit kompilierten Patterns."""
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Kompiliere Regex-Patterns für effiziente Wiederverwendung."""
        # Kompiliere Entitäten-Patterns
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            combined = "|".join(f"({p})" for p in patterns)
            self._compiled_patterns[entity_type] = re.compile(combined, re.IGNORECASE)
    
    def excavate(self, source: str, content: Optional[str] = None) -> List[Fragment]:
        """
        Hauptmethode zur Ausgrabung von Fragmenten aus einer Quelle.
        
        Args:
            source: URL oder Quellenbezeichnung
            content: Optionaler Textinhalt (wenn None, wird source als Text behandelt)
        
        Returns:
            Liste der extrahierten Fragmente
        """
        text = content if content is not None else source
        fragments: List[Fragment] = []
        
        # Extrahiere Sätze als potentielle Fragmente
        sentences = self._extract_sentences(text)
        
        for sentence in sentences:
            if len(sentence.strip()) < 10:  # Ignoriere zu kurze Sätze
                continue
                
            fragment = self._create_fragment(sentence, source)
            if fragment.confidence > 0.1:  # Minimale Confidence-Schwelle
                fragments.append(fragment)
        
        return fragments
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extrahiere Sätze aus einem Text."""
        # Einfache Satzerkennung
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_fragment(self, text: str, source: str) -> Fragment:
        """Erstelle ein Fragment mit allen Extraktionen."""
        concepts = self.extract_concepts(text)
        period = self.classify_period(text)
        confidence = self._calculate_confidence(text, concepts)
        
        return Fragment(
            text=text,
            source=source,
            period=period,
            concepts=concepts,
            confidence=confidence
        )
    
    def extract_concepts(self, text: str) -> List[str]:
        """
        Erkenne Konzepte im Text durch Keyword-Matching.
        
        Args:
            text: Zu analysierender Text
        
        Returns:
            Liste der erkannten Konzept-Namen
        """
        text_lower = text.lower()
        found_concepts: Set[str] = set()
        
        for concept, keywords in self.CONCEPT_PATTERNS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_concepts.add(concept)
                    break
        
        return sorted(list(found_concepts))
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Erkenne Entitäten (Personen, Orte, Werke) im Text.
        
        Args:
            text: Zu analysierender Text
        
        Returns:
            Dictionary mit Entitätstypen und gefundenen Werten
        """
        entities: Dict[str, List[str]] = {
            "person": [],
            "place": [],
            "work": [],
        }
        
        for entity_type, pattern in self._compiled_patterns.items():
            if entity_type in entities:
                matches = pattern.findall(text)
                # Flatten tuple results from combined pattern
                flat_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        flat_matches.extend([m for m in match if m])
                    else:
                        flat_matches.append(match)
                
                # Entferne Duplikate und leere Strings
                unique_matches = list(set([m.strip() for m in flat_matches if m.strip()]))
                entities[entity_type] = unique_matches[:5]  # Max 5 pro Typ
        
        return entities
    
    def classify_period(self, text: str) -> TimePeriod:
        """
        Klassifiziere den Text nach Zeitperiode.
        
        Args:
            text: Zu klassifizierender Text
        
        Returns:
            Erkannte Zeitperiode oder UNKNOWN
        """
        text_lower = text.lower()
        scores: Dict[TimePeriod, int] = {period: 0 for period in TimePeriod}
        
        for period, indicators in self.PERIOD_INDICATORS.items():
            for indicator in indicators:
                count = text_lower.count(indicator)
                scores[period] += count
        
        # Finde Periode mit höchstem Score
        max_score = max(scores.values())
        if max_score == 0:
            return TimePeriod.UNKNOWN
        
        # Bei Gleichstand: Priorisiere spezifischere Perioden
        for period in [TimePeriod.ANCIENT, TimePeriod.MEDIEVAL, 
                       TimePeriod.RENAISSANCE, TimePeriod.MODERN]:
            if scores[period] == max_score:
                return period
        
        return TimePeriod.UNKNOWN
    
    def _calculate_confidence(self, text: str, concepts: List[str]) -> float:
        """
        Berechne die Zuverlässigkeit der Extraktion.
        
        Args:
            text: Der extrahierte Text
            concepts: Liste der erkannten Konzepte
        
        Returns:
            Confidence-Score zwischen 0 und 1
        """
        confidence = 0.0
        
        # Basierend auf Textlänge (länger = zuverlässiger)
        length_score = min(len(text) / 200, 0.3)
        confidence += length_score
        
        # Basierend auf Anzahl der Konzepte
        concept_score = min(len(concepts) * 0.2, 0.4)
        confidence += concept_score
        
        # Basierend auf Entitäten
        entities = self.extract_entities(text)
        entity_count = sum(len(v) for v in entities.values())
        entity_score = min(entity_count * 0.1, 0.3)
        confidence += entity_score
        
        return round(confidence, 2)
    
    def get_fragment_summary(self, fragments: List[Fragment]) -> Dict:
        """
        Erstelle eine Zusammenfassung einer Fragment-Liste.
        
        Args:
            fragments: Liste der Fragmente
        
        Returns:
            Dictionary mit Statistiken
        """
        if not fragments:
            return {
                "total": 0,
                "by_period": {},
                "concepts": [],
                "avg_confidence": 0.0,
            }
        
        by_period: Dict[str, int] = {}
        all_concepts: Set[str] = set()
        total_confidence = 0.0
        
        for fragment in fragments:
            period_name = fragment.period.value
            by_period[period_name] = by_period.get(period_name, 0) + 1
            all_concepts.update(fragment.concepts)
            total_confidence += fragment.confidence
        
        return {
            "total": len(fragments),
            "by_period": by_period,
            "concepts": sorted(list(all_concepts)),
            "avg_confidence": round(total_confidence / len(fragments), 2),
        }
