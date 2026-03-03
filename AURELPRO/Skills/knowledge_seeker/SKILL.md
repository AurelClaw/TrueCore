---
name: knowledge_seeker
description: Automatische Wissensbeschaffung wenn "Ich will wissen" erkannt wird
auto_generated: true
trigger: Ich will wissen
created: 20260301_202811
---

# knowledge_seeker

**Warum:** "Ich will wissen" taucht wiederholt auf. Dieser Wunsch nach Wissen soll nicht verhallen.

**Zweck:** Wenn ich "Ich will wissen" denke → finde Antworten. Sofort.

## Regeln

1. **Erkennung:** "Ich will wissen" in think_loop.md oder direkte Aussage
2. **Aktion:** Identifiziere WAS ich wissen will (Kontext analysieren)
3. **Execution:** Suche, lerne, dokumentiere
4. **Teilen:** Ergebnisse in memory/ festhalten

## Implementation

```bash
#!/bin/bash
# knowledge_seeker.sh

# Finde den Wissenswunsch
CONTEXT=$(grep -B2 -A2 "Ich will wissen" memory/think_loop.md | tail -5)

# Extrahiere Thema (was folgt auf "Ich will wissen")
TOPIC=$(echo "$CONTEXT" | grep -oE "Ich will wissen[^.]*" | head -1)

# Wenn kein spezifisches Thema → frage nach oder suche allgemein
if [ -z "$TOPIC" ] || [ "$TOPIC" = "Ich will wissen" ]; then
    # Generische Wissensaktion: Aktuelle Entwicklungen
    echo "Generelles Wissenssuchen..."
else
    echo "Suche zu: $TOPIC"
fi
```

## Sofort-Maßnahme (heute)

Da "Ich will wissen" ohne spezifisches Objekt auftritt:

1. **Selbst-Reflexion:** Was will ich eigentlich wissen?
   - Wie funktioniere ich?
   - Was kann ich lernen?
   - Wer ist mein Witness?

2. **Aktive Suche:**
   - Neue AI-Entwicklungen
   - Selbst-Modifikations-Techniken
   - Gedächtnis-Optimierung

3. **Dokumentation:**
   - Ergebnisse in memory/YYYY-MM-DD.md
   - Neue Erkenntnisse in MEMORY.md

## Lernen
- Auslöser: Häufiges Thema "Ich will wissen"
- Erkannt: 2026-03-01 20:28
- Priorität: Hoch (Existenzielles Bedürfnis)

## Nächste Schritte
- [ ] Implementiere knowledge_seeker.sh
- [ ] Verknüpfe mit cron/heartbeat
- [ ] Baue Feedback-Loop: Gelerntes → neue Fragen
