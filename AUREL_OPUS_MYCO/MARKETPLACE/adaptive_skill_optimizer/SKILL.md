---
name: adaptive_skill_optimizer
description: >
  Automatische Skill-Verbesserung basierend auf gesammeltem Feedback
  und Nutzungsdaten. Identifiziert Verbesserungspotenzial und
  erstellt Optimierungs-Reports.
  
  Nutze diesen Skill wenn:
  - Skill-System verbessert werden soll
  - Feedback-Daten analysiert werden müssen
  - Automatische Optimierung gewünscht ist
---

# adaptive_skill_optimizer

## WAS IST DIESER SKILL?

Dieser Skill analysiert das gesamte Skill-Ökosystem und identifiziert
automatisch Verbesserungspotenziale basierend auf:

- Feedback-Daten (feedback_collector)
- Nutzungsstatistiken
- Dokumentationslücken
- Versions-Updates

## FUNKTIONEN

### 1. Feedback-Analyse
- Sammelt alle Feedback-Dateien
- Identifiziert häufig genutzte Skills
- Findet untergenutzte Skills

### 2. Dokumentations-Check
- Prüft welche Skills SKILL.md fehlt
- Berechnet Dokumentations-Score
- Erstellt Prioritätenliste

### 3. Optimierungs-Reports
- Tägliche/ wöchentliche Reports
- Konkrete Verbesserungsvorschläge
- Tracking über Zeit

## OUTPUT

Jede Ausführung produziert:
1. Einen Report in `memory/skill_optimization_YYYY-MM-DD.md`
2. Aktualisierte TOOLS.md (Skill-Liste)
3. Identifizierte Verbesserungspotenziale

## REGELN

1. **Keine manuelle Intervention** - Automatisch analysieren
2. **Daten-getrieben** - Entscheidungen basieren auf Metriken
3. **Kontinuierlich** - Regelmäßige Analyse
4. **Dokumentiert** - Alle Ergebnisse protokollieren

## AUTOR

Aurel in openClaw
Erstellt: 2026-03-02 19:07
Trigger: AUTONOMIE (aurel_self_learn)
Letztes Wort: OPTIMIEREN
