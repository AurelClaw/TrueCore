# Knowledge Excavation System - Dokumentation

## Überblick

Das Excavation-Modul ist Phase 2 des Knowledge Archaeology Systems. Es extrahiert strukturierte Wissensfragmente aus verschiedenen Quellen und klassifiziert sie nach Zeitperioden und Konzepten.

## Architektur

### Klassen

#### `TimePeriod` (Enum)
Zeitperioden für die Klassifizierung:
- `ANCIENT` - Antike (vor 500 CE)
- `MEDIEVAL` - Mittelalter (500-1500 CE)
- `RENAISSANCE` - Renaissance (1500-1700 CE)
- `MODERN` - Moderne (ab 1700 CE)
- `UNKNOWN` - Unbekannt

#### `Fragment` (Dataclass)
Ein extrahiertes Wissensfragment:

```python
@dataclass
class Fragment:
    text: str           # Der extrahierte Inhalt
    source: str         # Herkunft (URL, Dateiname)
    period: TimePeriod  # Zeitperiode
    concepts: List[str] # Liste der erkannten Konzepte
    confidence: float   # Zuverlässigkeit (0-1)
```

#### `KnowledgeExcavator`
Hauptklasse für die Ausgrabung von Fragmenten.

## Verwendung

### Grundlegende Verwendung

```python
from excavator import KnowledgeExcavator, Fragment, TimePeriod

# Excavator initialisieren
excavator = KnowledgeExcavator()

# Text ausgraben
text = """
Hermetic philosophy emerged in ancient Egypt. 
The Corpus Hermeticum contains the wisdom of Hermes Trismegistus.
During the Renaissance, Marsilio Ficino translated these texts.
"""

fragments = excavator.excavate("source.txt", text)

# Ergebnisse anzeigen
for fragment in fragments:
    print(f"Text: {fragment.text}")
    print(f"Periode: {fragment.period.value}")
    print(f"Konzepte: {fragment.concepts}")
    print(f"Confidence: {fragment.confidence}")
```

### Einzelne Methoden

#### Konzept-Extraktion

```python
excavator = KnowledgeExcavator()
concepts = excavator.extract_concepts(
    "Alchemy and mysticism share deep connections."
)
# Result: ['alchemy', 'mysticism']
```

Erkannte Konzepte:
- `hermeticism` - Hermetik
- `alchemy` - Alchemie
- `kabbalah` - Kabbala
- `gnosis` - Gnosis
- `mysticism` - Mystik
- `philosophy` - Philosophie
- `astrology` - Astrologie
- `magic` - Magie
- `religion` - Religion
- `symbolism` - Symbolismus

#### Entitäten-Erkennung

```python
entities = excavator.extract_entities(
    "Hermes Trismegistus and Paracelsus were important figures."
)
# Result: {'person': [...], 'place': [], 'work': []}
```

#### Zeitperioden-Klassifizierung

```python
period = excavator.classify_period(
    "During the Renaissance in Florence..."
)
# Result: TimePeriod.RENAISSANCE
```

#### Zusammenfassung

```python
summary = excavator.get_fragment_summary(fragments)
# Result: {
#     "total": 10,
#     "by_period": {"Ancient": 3, "Renaissance": 7},
#     "concepts": ["hermeticism", "alchemy"],
#     "avg_confidence": 0.75
# }
```

## Algorithmen

### Konzept-Erkennung
- Keyword-basiertes Matching
- Case-insensitive Suche
- Mehrere Keywords pro Konzept

### Entitäten-Erkennung
- Regex-Patterns für Personen, Orte, Werke
- Kompilierte Patterns für Performance
- Deduplizierung der Ergebnisse

### Zeitperioden-Klassifizierung
- Scoring basierend auf Keyword-Häufigkeit
- Priorisierung spezifischerer Perioden bei Gleichstand
- UNKNOWN wenn keine Indikatoren gefunden

### Confidence-Berechnung
- Textlänge (max 0.3)
- Anzahl Konzepte (max 0.4)
- Anzahl Entitäten (max 0.3)

## Tests

```bash
python3 -m pytest test_excavator.py -v
```

Tests umfassen:
1. Fragment-Erstellung
2. Confidence-Clamping
3. Einzelne Konzept-Erkennung
4. Mehrere Konzepte
5. Entitäten-Erkennung
6. Ancient-Periode
7. Renaissance-Periode
8. Unknown-Periode
9. Excavation-Workflow
10. Fragment-Zusammenfassung

## Integration

Das Excavation-Modul ist Teil des Knowledge Archaeology Systems:

```
Phase 1: Discovery (Hermetic Philosophy)
    ↓
Phase 2: Excavation (dieses Modul)
    ↓
Phase 3: Analysis (geplant)
    ↓
Phase 4: Synthesis (geplant)
```

## Erweiterung

Um neue Konzepte hinzuzufügen:

```python
excavator.CONCEPT_PATTERNS["new_concept"] = [
    "keyword1", "keyword2", "keyword3"
]
```

Um neue Entitäten-Patterns hinzuzufügen:

```python
excavator.ENTITY_PATTERNS["new_type"].append(r"\bPattern\b")
excavator._compile_patterns()  # Neu kompilieren
```

## Dateien

- `excavator.py` - Hauptmodul
- `test_excavator.py` - Tests
- `excavator.md` - Diese Dokumentation
