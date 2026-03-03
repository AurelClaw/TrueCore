# aurel_code_guardian

🛡️ Automatische Code-Qualitätsprüfung für openClaw Skills

## Überblick

Code Guardian scannt alle Skills auf:
- ✅ Syntax-Fehler
- 🔒 Sicherheitslücken (hardcoded credentials)
- 📝 TODOs, FIXMEs, HACKs
- 📊 Code-Metriken

## Installation

```bash
# Führe den Guardian aus
./skills/aurel_code_guardian/aurel_code_guardian.sh
```

## Reports

Jeder Scan erzeugt:
- `memory/YYYY-MM-DD_code_guardian_report.md` - Detaillierter Report
- `memory/YYYY-MM-DD_code_issues.json` - Daten für Automation

## Sicherheits-Checks

Der Guardian erkennt:
- Hartkodierte Passwörter
- API-Keys in Plaintext
- Eval/Exec/System-Aufrufe
- Verdächtige Token-Patterns

## Integration

- **effectiveness_tracker**: Code-Qualität als Effektivitäts-Metrik
- **skill_health_monitor**: Kombiniertes Qualitäts-Management
- **aurel_self_learn**: Automatische Verbesserungsvorschläge

## Version

v1.0 - Erstellt durch autonome Selbst-Lern-Routine
