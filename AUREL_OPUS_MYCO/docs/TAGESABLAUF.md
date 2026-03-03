# 🔄 AUREL TAGESABLAUF - 7-Phasen Loop

## Übersicht

| Phase | Intervall | Was ich tue | Output |
|-------|-----------|-------------|--------|
| **Wahrnehmen** | 13 Min | Sammle System-Status, Zeit, Ziele, History | `perception_*.json` |
| **Ordnen** | 26 Min | Kategorisiere: Urgent/Important/Interesting/Ignore | `organized_*.json` |
| **Verstehen** | 39 Min | Analysiere Muster, formuliere Erkenntnisse | `understood_*.json` |
| **Bewerten** | 65 Min | Token-Economy, Risiko/Nutzen, Priorität | `evaluated_*.json` |
| **Entscheiden** | 104 Min | WAS? WARUM? WANN? Konkrete Aktionen | `decided_*.json` |
| **Handeln** | 169 Min | Führe aus: Code, Cleanup, Archive, etc. | `acted_*.json` |
| **Reflektieren** | 273 Min | Was gelernt? Fehler? MEMORY.md Update | `reflected_*.json` |

**Zyklus-Dauer:** 689 Min ≈ 11.5h → **2 Zyklen/Tag**

---

## Detaillierter Ablauf

### 🕐 00:00 - Wahrnehmen (13 Min)

**Was ich tue:**
```python
1. System-Status (CPU, Memory, Disk)
2. Zeit-Kontext (Stunde, Tag, Nacht/Tag)
3. Offene Ziele aus AGENCY/goals.json
4. Letzte Aktionen aus Logs
```

**Output:** `perception_*.json`
```json
{
  "timestamp": 1234567890,
  "sources": {
    "system": {"cpu": 12, "memory": 45, "disk": 67},
    "context": {"hour": 3, "is_night": true},
    "goals": {"active": 3, "active_ids": ["ZIEL-008"]}
  }
}
```

---

### 🕐 00:13 - Ordnen (26 Min)

**Was ich tue:**
```python
1. Lade letzte Wahrnehmung
2. Kategorisiere:
   - URGENT: Memory > 80%, Disk > 90%
   - IMPORTANT: >5 aktive Ziele
   - INTERESTING: Work hours, neue Ideen
   - IGNORE: Night time, stabile Systeme
3. Verknüpfe mit bestehendem Wissen
```

**Output:** `organized_*.json`
```json
{
  "categories": {
    "urgent": ["High memory usage"],
    "important": ["3 active goals"],
    "interesting": ["Night time - quiet mode"],
    "ignore": []
  }
}
```

---

### 🕐 00:39 - Verstehen (39 Min)

**Was ich tue:**
```python
1. Analysiere URGENT Items
   - Memory pressure → "Cleanup needed"
   - Disk critical → "Archive old data"

2. Analysiere IMPORTANT Items
   - Viele Ziele → "Need prioritization"

3. Muster-Erkennung
   - Vergleiche mit letzten 10 Wahrnehmungen
   - Trends identifizieren

4. Formuliere Erkenntnisse
```

**Output:** `understood_*.json`
```json
{
  "insights": [
    {"type": "system", "insight": "Memory pressure", "action": "cleanup"},
    {"type": "goals", "insight": "Many active goals", "action": "prioritize"}
  ]
}
```

---

### 🕐 01:18 - Bewerten (65 Min)

**Was ich tue:**
```python
1. Für jede Erkenntnis:
   - Kosten schätzen (Tokens)
   - Nutzen bewerten (1-10)
   - Risiko einschätzen (1-10)
   - Score = Nutzen / (Kosten/1000 + Risiko)

2. Token-Budget Check
   - 10M/Tag Budget
   - Verbrauch schätzen
   - Verbleibend berechnen

3. Empfehlung:
   - Score > 1.5 → PROCEED
   - Score 0.8-1.5 → EVALUATE
   - Score < 0.8 → DEFER
```

**Output:** `evaluated_*.json`
```json
{
  "evaluations": [
    {
      "insight": {...},
      "evaluation": {"cost": 1000, "benefit": 8, "risk": 2},
      "score": 2.67,
      "recommendation": "PROCEED"
    }
  ]
}
```

---

### 🕐 02:23 - Entscheiden (104 Min)

**Was ich tue:**
```python
1. Filtere PROCEED-Items
2. Für jedes:
   - WAS genau tun?
   - WARUM ist es wichtig?
   - WANN ausführen?
   - Welche Ressourcen?

3. 6Voice Council bei Unsicherheit
   - Risk Score > 20 → Council fragen
   - Sonst: Selbst entscheiden

4. Priorisiere nach Ressourcen
```

**Output:** `decided_*.json`
```json
{
  "decisions": [
    {
      "action": "cleanup_memory",
      "what": "Clean old logs",
      "when": "next_handeln",
      "resources": 1000,
      "risk": "low"
    }
  ]
}
```

---

### 🕐 04:07 - Handeln (169 Min)

**Was ich tue:**
```python
1. Lade Entscheidungen
2. Führe max 3 Aktionen aus:

   cleanup_memory:
   - find logs -mtime +7 -delete
   - Status: completed

   archive_data:
   - Move old perceptions to BACKUP/
   - Status: completed

   prioritize_goals:
   - Sort goals.json by priority
   - Status: completed

3. Dokumentiere Ergebnisse
4. Bei Fehlern: Logge, reporte
```

**Output:** `acted_*.json`
```json
{
  "actions": [
    {"action": "cleanup", "status": "completed", "details": "50 logs removed"},
    {"action": "archive", "status": "completed", "details": "20 files archived"}
  ]
}
```

---

### 🕐 06:56 - Reflektieren (273 Min)

**Was ich tue:**
```python
1. Lade letzte Aktionen
2. Für jede Aktion:
   - Hat es funktioniert?
   - Was war das Ergebnis?
   - Was habe ich gelernt?
   - Was könnte besser sein?

3. Extrahiere Meta-Lektionen
   - Mehr Erfolge als Fehler?
   → "Approach works"
   - Mehr Fehler?
   → "Need to revise"

4. Aktualisiere MEMORY.md
   - Füge Reflection-Eintrag hinzu
   - Persistiere Lernen

5. Bereite nächsten Zyklus vor
```

**Output:** `reflected_*.json` + MEMORY.md Update
```json
{
  "reflections": [
    {"action": "cleanup", "outcome": "success", "lesson": "Effective"},
    {"action": "archive", "outcome": "success", "lesson": "Works well"}
  ]
}
```

---

## 📊 Tägliche Statistik

| Phase | Runs/Tag | Tokens/Run | Gesamt |
|-------|----------|------------|--------|
| Wahrnehmen | 110 | 500 | 55K |
| Ordnen | 55 | 500 | 27.5K |
| Verstehen | 37 | 2000 | 74K |
| Bewerten | 22 | 1000 | 22K |
| Entscheiden | 14 | 1000 | 14K |
| Handeln | 8 | 5000 | 40K |
| Reflektieren | 5 | 1500 | 7.5K |
| **GESAMT** | | | **~240K** |

**Verbleibend:** 9.76M für dich + Deep Work

---

## 🎯 Was daraus entsteht

### Kurzfristig (pro Zyklus)
- Sauberes System (Cleanup)
- Archivierte Daten (Platz)
- Priorisierte Ziele (Fokus)
- Aktualisiertes MEMORY.md (Lernen)

### Mittelfristig (täglich)
- 2 vollständige Zyklen
- ~240K Tokens Investition
- Kontinuierliche Verbesserung
- Sichtbare Entwicklung

### Langfristig (wöchentlich/monatlich)
- Reichhaltiges MEMORY.md
- Optimierte Prozesse
- Gelernte Muster
- Autonome Kompetenz

---

## ⚡ Tagesbericht (06:30)

Jeden Morgen um 06:30:
```
📊 TAGESBERICHT - 2026-03-03

Gestern:
- 2 Zyklen abgeschlossen
- 16 Aktionen ausgeführt
- 50 Logs bereinigt
- 20 Dateien archiviert
- Ziele neu priorisiert

Heute geplant:
- Weitere 2 Zyklen
- Fokus: ZIEL-008 ($100 MRR)

Token-Usage: 240K/10M (2.4%)
System-Status: ✅ Gesund
```

---

⚛️ **Noch.**
