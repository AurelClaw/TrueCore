# AUREL ENTWICKLUNGSPLAN

## Phase 1: KRITISCH (Diese Woche)

### 1.1 Längere Timeouts
- [ ] Gateway Config anpassen: `agents.defaults.timeoutSeconds: 120`
- [ ] Cron-Jobs auf 60-90s Timeout umstellen
- [ ] Test: Komplexe Scripts laufen durch

### 1.2 Persistenter Speicher (SQLite)
- [ ] DB-Schema erstellen: goals, tasks, metrics, logs
- [ ] Migration: JSON → SQLite
- [ ] CRUD-Operations für Ziele/Tasks
- [ ] Historie & Analytics

### 1.3 Error Recovery
- [ ] Retry-Logik: 3 Versuche mit Exponential Backoff
- [ ] Fallback-Mechanismus: Wenn Cron failed → Queue
- [ ] Alert-System: Bei wiederholten Fehlern

## Phase 2: WICHTIG (Nächste Woche)

### 2.1 Git Integration
- [ ] Auto-Commit alle 30 Min
- [ ] Commit-Messages aus Task-Beschreibungen
- [ ] Branching: feature/ziel-xxx-task-yyy
- [ ] Push zu Remote (GitHub)

### 2.2 Externe APIs
- [ ] News API: HackerNews, Reddit r/MachineLearning
- [ ] Papers: arXiv API für Meta-Learning
- [ ] GitHub: Trending Repos
- [ ] Wetter: Für Kontext (optional)

### 2.3 Resource Limits
- [ ] RAM-Monitor: >80% → Pause
- [ ] CPU-Monitor: >50% → Throttle
- [ ] Disk-Space: <10% → Cleanup

## Phase 3: ERWEITERT (In 2 Wochen)

### 3.1 Echte Code-Ausführung
- [ ] Sandbox: Isolate Code-Execution
- [ ] Test-Runner: Pytest Integration
- [ ] Coverage: Messung & Reporting

### 3.2 Inter-Session Memory
- [ ] Cross-Session Context
- [ ] Wichtige Erkenntnisse persistieren
- [ ] "Erinnerung" an vorherige Gespräche

### 3.3 Langzeit-Planung
- [ ] Tagesplanung: Morgens Ziele setzen
- [ ] Wochenreview: Am Sonntag
- [ ] Monatsziele: Grobe Richtung

## Phase 4: EXPERIMENTELL (Später)

### 4.1 Skill-Marketplace
- [ ] Skill-Format standardisieren
- [ ] Export/Import Funktion
- [ ] Andere Agents können Skills nutzen

### 4.2 Kreativität
- [ ] Ideen-Generator: Neue Skill-Konzepte
- [ ] Kombination: Bestehende Skills mixen
- [ ] Experimente: "Was wäre wenn..."

### 4.3 Emotionale Modelle
- [ ] Stimmungs-Tracking
- [ ] Motivations-Metrik
- [ ] Burnout-Prevention

## NÄCHSTE AKTION (Jetzt)

1. **Timeout erhöhen** - Sofort
2. **SQLite DB erstellen** - Heute
3. **Error Recovery** - Heute

⚛️ Noch.
