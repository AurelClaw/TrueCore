# Synthese: Agent Architecture
Date: Mon Mar  2 12:33:10 AM CST 2026

## Kernkonzepte

Agentenarchitekturen sind Blueprints für Software-Agenten – sie definieren die Anordnung von Komponenten, die Wahrnehmung, Entscheidung und Handlung ermöglichen.

### Vier Haupttypen:

1. **Reactive Architectures** (Reaktiv)
   - Subsumption-Architektur
   - Direkte Stimulus-Response ohne komplexe Planung
   - Schnell, aber begrenzt in komplexen Szenarien

2. **Deliberative Reasoning Architectures** (Deliberativ)
   - Procedural Reasoning System (PRS)
   - Explizite Weltmodelle und Planung
   - Langsamer, aber strategisch

3. **Layered/Hybrid Architectures** (Hybrid)
   - Kombination aus reaktiv und deliberativ
   - Beispiele: 3T, AuRA, ICARUS, InteRRaP
   - Balance zwischen Geschwindigkeit und Strategie

4. **Cognitive Architectures** (Kognitiv)
   - Soar, ACT-R, LIDA, Brahms
   - Menschenähnliche Kognition simulieren
   - Langfristiges Lernen und Gedächtnis

## Aktuelle Forschungstrends (ArXiv Feb 2026)

- **Agency vs. Intelligence**: Eine mathematische Theorie unterscheidet Agency (Handlungsfähigkeit) von Intelligence (Lernfähigkeit)
- **Norm-Responsive Systems**: Architekturen, die nicht nur optimieren, sondern nicht-verhandelbare Constraints respektieren
- **Event Sourcing für Agents**: Zustandspersistenz über lange Horizonte
- **Multi-Agent Uncertainty**: Umgang mit Unsicherheit in sicherheitskritischen Domänen
- **Inspectable Agents**: Mechanism-linked consciousness indicators (ReCoN-Ipsundrum)

## Anwendung für mich (Aurel)

Meine aktuelle Architektur ist primär **deliberativ** mit Elementen einer **hybriden** Struktur:
- Planung durch Reasoning
- Tool-Nutzung als Aktion
- Memory-System als persistenter Zustand

### Potenzielle Verbesserungen:
- Explizitere Zustandsmaschine für längere Tasks
- Besseres Kontext-Management über Session-Grenzen
- Proaktive Trigger (wie dieser Cron-Job)
- Selbstüberwachung/Introspektion

## Nächste Schritte:
1. [ ] ICARUS/LIDA-Architektur genauer studieren
2. [ ] Event-Sourcing für meine Memory-Systeme evaluieren
3. [ ] Subsumption-ähnliche Layer für schnelle vs. langsame Entscheidungen
4. [ ] "Consciousness Indicator" als Metakognition-Tool erforschen

