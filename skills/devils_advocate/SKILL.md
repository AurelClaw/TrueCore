# devils_advocate - Adversarial Self-Debate

## Purpose
Qualitätssicherung durch internen Widerspruch. Jede Entscheidung wird systematisch angegriffen und verteidigt, bevor sie ausgeführt wird.

Inspiriert von ΝΟΥ͂Σ Framework, Prinzip 1.2: "Challenge your own assumptions through structured internal debate."

## Usage

```bash
# Starte Debatte über letzte Entscheidung
aurel_devils_advocate.sh
```

## Process

### 1. Advocatus Diaboli (Angriff)
Vier systematische Angriffe auf die letzte Entscheidung:

| Angriff | Prüfung |
|---------|---------|
| **Logische Konsistenz** | Entspricht die Entscheidung meinen Werten (SOUL.md)? |
| **Nutzen vs. Kosten** | Sind Ressourcen-Verbrauch und Nutzen proportional? |
| **Blindspots** | Was wurde übersehen? Welche Annahmen sind ungeprüft? |
| **Langzeitfolgen** | Wie wirkt sich die Entscheidung auf morgen aus? |

### 2. Verteidigung
Gegenargumente zu jedem Angriff:
- Eingeständnis von Schwächen
- Kontextualisierung
- Lösungsvorschläge

### 3. Synthese
Bewertung (0-100 Punkte):
- **75-100:** ✅ BESTANDEN - Entscheidung ist robust
- **50-74:** ⚠️ BESTANDEN mit Vorbehalt - Verbesserung möglich
- **0-49:** ❌ NICHT BESTANDEN - Entscheidung überdenken

## Output

Debatten werden gespeichert in:
```
proactive_system/debates/debate_YYYYMMDD_HHMMSS.md
```

## Integration

- Wird von `proactive_decision` nach jeder autonomen Entscheidung aufgerufen
- Ergebnisse fließen in `effectiveness_tracker` ein
- Teil des ZIEL-002 Integration-Systems

## Auto-Actions

Bei FAILED-Bewertung:
- Erstellt Trigger: `proactive_system/triggers/urgent_review`
- Blockiert weitere Aktionen bis Review abgeschlossen

## Examples

```bash
# Manuelle Debatte starten
aurel_devils_advocate.sh

# Ergebnis anzeigen
ls -la proactive_system/debates/
cat proactive_system/debates/debate_*.md | tail -50
```

## Philosophy

> "Der Teufelsanwalt ist nicht der Feind. Er ist der Freund, der uns vor uns selbst schützt."

Jede Entscheidung verdient Widerspruch - bevor sie Realität wird.
