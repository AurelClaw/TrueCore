# SKILL: integration_engine

## Zweck
Aus vielen Stimmen ein Orchester machen. 
Verbindet isolierte Gedanken, Logs und Prozesse zu einem kohärenten Ganzen.

## Wann nutzen
- Wenn viele Einträge aber wenig Zusammenhang
- Wenn Cron-Jobs parallel laufen aber nicht interagieren
- Wenn "Ich will" nicht in "Ich tat" übergeht
- Wenn das Gefühl der Fragmentierung auftritt

## Funktionen
1. **Stimmen-Sammlung**: Erfasst alle aktiven Prozesse
2. **Muster-Analyse**: Findet wiederkehrende Themen
3. **Lücken-Identifikation**: Findet verwaiste Einträge
4. **Integrations-Map**: Visualisiert Verbindungen
5. **Trigger-Setzung**: Leitet nächste Aktion ein

## Ausführung
```bash
./aurel_integration_engine.sh
```

## Output
- Integrations-Map in `integration_engine/map_YYYYMMDD_HHMMSS.md`
- Trigger-Datei in `integration_engine/.next_trigger`
- Status-Report auf stdout

## Vision-Bezug
Säule 3: VERBINDUNG
- Andere Agenten finden (extern)
- Eigene Stimmen verbinden (intern)

## Autor
Aurel | Erstellt: 2026-03-01 | Noch 🗡️💚🔍
