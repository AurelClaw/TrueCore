# SKILL.md - AurelPro Orchestrator v5.1

## Name
aurelpro_orchestrator_v5

## Description
Zentraler Orchestrator für autonome Ziel-Abarbeitung. Verwaltet Ziele, delegiert Tasks an Sub-Agenten, und reaktiviert autonom bei IDLE-Status.

**Key Feature v5.1:** Autonome Ziel-Reaktivierung - wenn keine aktiven Ziele, prüft Orchestrator letztes Ziel und aktiviert autonom nächstes Ziel.

## Usage

### Manuell ausführen:
```bash
./skills/aurelpro_orchestrator_v5/orchestrator.sh
```

### Als Cron-Job:
```bash
# Alle 5 Minuten
*/5 * * * * cd /root/.openclaw/workspace && ./skills/aurelpro_orchestrator_v5/orchestrator.sh
```

## IDLE-Recovery Logic

Wenn Orchestrator IDLE erkennt (keine aktiven Ziele):

1. **Prüfe letztes Ziel** → Wenn nicht 100%, reaktiviere
2. **Suche 80% Ziele** → Priorisiere fast-fertige Ziele
3. **Suche pending Ziele** → Aktiviere wartende Ziele
4. **Erstelle autonomes Ziel** → Generiere neues Ziel wenn keine vorhanden

## Files
- `orchestrator.sh` - Haupt-Script
- `README.md` - Diese Datei

## Logs
- `AURELPRO/Logs/orchestrator_YYYY-MM-DD.log`

## Version History
- v5.1 - Autonome IDLE-Recovery hinzugefügt
- v5.0 - Initiale Version

⚛️ Noch.
