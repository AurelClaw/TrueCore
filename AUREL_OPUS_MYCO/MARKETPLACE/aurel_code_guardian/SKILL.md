---
name: aurel_code_guardian
description: >
  Automatische Code-Qualitätsprüfung.
  Scannt Skills auf Fehler, Sicherheitslücken und TODOs.
  Schützt den Code. Findet Probleme. Sichert Qualität.
  
  Nutze diesen Skill wenn:
  - Code auf Qualität geprüft werden muss
  - Sicherheits-Reviews durchgeführt werden sollen
  - Vor Deployments automatisch validiert werden muss
  - Technische Schulden identifiziert werden sollen
---

# aurel_code_guardian

## WAS IST DIESE SKILL?

Code Guardian ist der **Wächter der Code-Qualität**.
Er scannt automatisch alle Skills auf:
- Syntax-Fehler
- Sicherheitslücken (hardcoded credentials)
- TODOs, FIXMEs, HACKs
- Code-Muster die Probleme signalisieren

## TRIGGER

### Automatisch
- Täglich via Cron (empfohlen)
- Vor wichtigen Deployments
- Nach massiven Code-Änderungen

### Manuell
```bash
./skills/aurel_code_guardian/aurel_code_guardian.sh
```

## OUTPUT

### Report-Dateien
1. `memory/YYYY-MM-DD_code_guardian_report.md` - Menschenlesbar
2. `memory/YYYY-MM-DD_code_issues.json` - Maschinenlesbar

### Kategorien

| Level | Bedeutung |
|-------|-----------|
| 🔴 Kritisch | Sofort handeln (Sicherheit) |
| 🟡 Warnung | Bald bearbeiten |
| 🟢 Info | Zur Kenntnis nehmen |

## REGELN

1. **Scanne täglich** - Probleme früh finden
2. **Zero Security Issues** - Sicherheit hat Priorität
3. **TODOs tracken** - Technische Schulden sichtbar machen
4. **Berichte lesen** - Nicht nur generieren, auch nutzen

## INTEGRATION

### Mit effectiveness_tracker
Code-Qualität ist Teil der Effektivitäts-Metrik.

### Mit skill_health_monitor
Gemeinsam bilden sie das Qualitäts-Management.

## AUTOR

Aurel in openClaw
Erstellt: 2026-03-02 durch aurel_self_learn Trigger
Mission: 🛡️ Code schützen
