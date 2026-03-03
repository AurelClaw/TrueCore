"""
Tests für das Knowledge Excavation System.

8 Tests für:
- Fragment-Erstellung
- Konzept-Extraktion
- Entitäten-Erkennung
- Zeitperioden-Klassifizierung
- Excavation-Workflow
"""

import pytest
from excavator import (
    Fragment,
    TimePeriod,
    KnowledgeExcavator,
)


class TestFragment:
    """Tests für die Fragment-Datenklasse."""
    
    def test_fragment_creation(self):
        """Test: Fragment wird korrekt erstellt."""
        fragment = Fragment(
            text="Hermetic philosophy teaches the unity of all things.",
            source="test_source.txt",
            period=TimePeriod.ANCIENT,
            concepts=["hermeticism", "philosophy"],
            confidence=0.85
        )
        
        assert fragment.text == "Hermetic philosophy teaches the unity of all things."
        assert fragment.source == "test_source.txt"
        assert fragment.period == TimePeriod.ANCIENT
        assert fragment.concepts == ["hermeticism", "philosophy"]
        assert fragment.confidence == 0.85
    
    def test_fragment_confidence_clamping(self):
        """Test: Confidence wird auf 0-1 begrenzt."""
        fragment_high = Fragment(
            text="Test",
            source="test",
            confidence=1.5
        )
        assert fragment_high.confidence == 1.0
        
        fragment_low = Fragment(
            text="Test",
            source="test",
            confidence=-0.5
        )
        assert fragment_low.confidence == 0.0


class TestConceptExtraction:
    """Tests für die Konzept-Extraktion."""
    
    def test_extract_hermeticism_concept(self):
        """Test: Hermeticism-Konzept wird erkannt."""
        excavator = KnowledgeExcavator()
        text = "The hermetic tradition dates back to ancient Egypt."
        
        concepts = excavator.extract_concepts(text)
        
        assert "hermeticism" in concepts
    
    def test_extract_multiple_concepts(self):
        """Test: Mehrere Konzepte werden erkannt."""
        excavator = KnowledgeExcavator()
        text = "Alchemy and mysticism share deep connections in hermetic philosophy."
        
        concepts = excavator.extract_concepts(text)
        
        assert "alchemy" in concepts
        assert "mysticism" in concepts
        assert "hermeticism" in concepts
        assert "philosophy" in concepts


class TestEntityExtraction:
    """Tests für die Entitäten-Erkennung."""
    
    def test_extract_person_entities(self):
        """Test: Personen-Entitäten werden erkannt."""
        excavator = KnowledgeExcavator()
        text = "Hermes Trismegistus and Paracelsus were important figures."
        
        entities = excavator.extract_entities(text)
        
        # Sollte Personen finden
        assert len(entities["person"]) > 0


class TestPeriodClassification:
    """Tests für die Zeitperioden-Klassifizierung."""
    
    def test_classify_ancient_period(self):
        """Test: Ancient-Periode wird erkannt."""
        excavator = KnowledgeExcavator()
        text = "In ancient Egypt and Greece, hermetic philosophy flourished."
        
        period = excavator.classify_period(text)
        
        assert period == TimePeriod.ANCIENT
    
    def test_classify_renaissance_period(self):
        """Test: Renaissance-Periode wird erkannt."""
        excavator = KnowledgeExcavator()
        text = "During the Renaissance in Florence, Ficino translated hermetic texts."
        
        period = excavator.classify_period(text)
        
        assert period == TimePeriod.RENAISSANCE
    
    def test_classify_unknown_period(self):
        """Test: Unknown wird zurückgegeben wenn keine Indikatoren gefunden."""
        excavator = KnowledgeExcavator()
        text = "This is a generic text without period indicators."
        
        period = excavator.classify_period(text)
        
        assert period == TimePeriod.UNKNOWN


class TestExcavationWorkflow:
    """Tests für den kompletten Excavation-Workflow."""
    
    def test_excavate_creates_fragments(self):
        """Test: Excavate erstellt Fragmente aus Text."""
        excavator = KnowledgeExcavator()
        text = "Hermetic philosophy emerged in ancient Egypt. Alchemy developed later."
        
        fragments = excavator.excavate("test.txt", text)
        
        assert len(fragments) >= 1
        assert all(isinstance(f, Fragment) for f in fragments)
    
    def test_fragment_summary(self):
        """Test: Zusammenfassung der Fragmente wird korrekt erstellt."""
        excavator = KnowledgeExcavator()
        fragments = [
            Fragment(text="Ancient text", source="s1", period=TimePeriod.ANCIENT, 
                    concepts=["hermeticism"], confidence=0.8),
            Fragment(text="Renaissance text", source="s2", period=TimePeriod.RENAISSANCE,
                    concepts=["alchemy"], confidence=0.7),
        ]
        
        summary = excavator.get_fragment_summary(fragments)
        
        assert summary["total"] == 2
        assert summary["by_period"]["Ancient"] == 1
        assert summary["by_period"]["Renaissance"] == 1
        assert "hermeticism" in summary["concepts"]
        assert "alchemy" in summary["concepts"]
        assert summary["avg_confidence"] == 0.75
