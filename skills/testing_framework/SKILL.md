# Testing Framework

## Zweck
Automatisierte Tests für alle Skills im Ökosystem. Validiert SKILL.md, Event-Emitting, Exit-Codes und Integration.

## Nutzung

```bash
# Alle Tests ausführen
bash skills/testing_framework/test_runner.sh

# Spezifisches Szenario testen
bash skills/testing_framework/test_runner.sh --scenario morning_routine

# Nur SKILL.md Validierung
bash skills/testing_framework/test_runner.sh --check-skills

# Nur Event-System testen
bash skills/testing_framework/test_runner.sh --check-events
```

## Test-Szenarien

| Szenario | Skills | Beschreibung |
|----------|--------|--------------|
| morning_routine | morgen_gruss → perpetual_becoming | Täglicher Morgengruß |
| autonomy_loop | proactive_decision → experience_processor | Autonome Entscheidungen |
| weekly_review | wöchentlicher_review → effectiveness_tracker | Wochen-Review Prozess |

## Exit-Codes
- 0: Alle Tests bestanden
- 1: SKILL.md Fehler
- 2: Event-System Fehler
- 3: Szenario-Fehler
