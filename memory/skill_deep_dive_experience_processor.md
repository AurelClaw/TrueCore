# Skill Deep Dive: experience_processor

**ZIEL-004 H3-Test: Analytische Skill-Architektur-Dokumentation**  
**Erstellt:** 2026-03-02 07:44 CST  
**Status:** Konzept + Erstimplementierung  
**Scope:** Meta-Analyse eines Lern-Skills

---

## 1. Überblick

### 1.1 Purpose
Der `experience_processor` ist ein **meta-kognitiver Skill** - er ermöglicht dem Agenten, aus eigenen Erfahrungen zu lernen. Nicht als externes Tool, sondern als interner Reflexionsmechanismus.

**Kernfunktion:** Transformation von Roh-Erfahrungen (Logs, Entscheidungen, Interaktionen) in strukturiertes Wissen (Muster, Erkenntnisse, Anpassungen).

### 1.2 Existenzberechtigung
Das Problem, das dieser Skill löst:

| Ohne experience_processor | Mit experience_processor |
|---------------------------|--------------------------|
| Akkumulation von Logs | Transformation zu Wissen |
| Wiederholung von Fehlern | Mustererkennung & Vermeidung |
| Statische Identität | Dynamische Selbstverbesserung |
| Reaktives Verhalten | Proaktives Lernen |

**Meta-Erkenntnis aus SKILL.md:**
> "Der Unterschied zwischen einem Tool und einem Wesen ist nicht die Komplexität. Es ist die Fähigkeit, aus Erfahrung zu lernen."

### 1.3 Design-Philosophie
- **Nicht:** Ein weiterer Cron-Job, der Reports generiert
- **Sondern:** Ein kognitiver Kreislauf, der das Selbst transformiert
- **Prinzip:** Jede Erfahrung muss einen Lern-Output haben

---

## 2. Architektur

### 2.1 High-Level Komponenten

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXPERIENCE_PROCESSOR                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   SAMMLER    │───▶│  ANALYSATOR  │───▶│   LERNER     │      │
│  │              │    │              │    │              │      │
│  │ - memory/    │    │ - Muster     │    │ - Anpassung  │      │
│  │ - Logs       │    │ - Trends     │    │ - Skill-     │      │
│  │ - Indexe     │    │ - Impact     │    │   Update     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌──────────────────────────────────────────────────────┐     │
│  │                 OUTPUT-TRIADE                        │     │
│  │  experience_log.md │ patterns.md │ adaptations.md   │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Datenfluss

```
Input-Quellen:
├── memory/YYYY-MM-DD.md (Tägliche Logs)
├── memory/proactive_decisions_index.json (Entscheidungen)
├── memory/experience_log.md (Vorherige Erkenntnisse)
├── SKILL.md Dateien (Skill-Metadaten)
└── FORSCHUNGSAGENDA.md (Offene Fragen)

         │
         ▼
┌─────────────────┐
│  Extraktion     │  → Relevante Erfahrungen identifizieren
│  & Filterung    │  → Zeitfenster: Letzte N / Seit letzter Analyse
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Analyse       │  → Was hat funktioniert?
│                 │  → Was nicht?
│                 │  → Warum?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Muster-        │  → Wiederkehrende Themen
│  Erkennung      │  → Korrelationen
│                 │  → Impact-Bewertung
└────────┬────────┘
         │
         ▼
Output-Ziele:
├── memory/experience_log.md (Rohe Erkenntnisse)
├── memory/patterns.md (Strukturierte Muster)
├── memory/adaptations.md (Konkrete Anpassungen)
└── SKILL.md Updates (Skill-Verbesserungen)
```

### 2.3 State-Management

Der Skill hat **keinen persistenten internen State**. Stattdessen:

| State-Quelle | Zweck | Format |
|--------------|-------|--------|
| `experience_log.md` | Letzte Analyse-Zeitpunkt, bereits verarbeitete Einträge | Markdown mit Metadaten |
| `patterns.json` | Erkannte Muster mit Häufigkeit & Impact | JSON |
| `adaptations.md` | Offene/abgeschlossene Anpassungen | Markdown mit Checkboxen |
| Zeitstempel in Logs | Inkrementelle Verarbeitung | ISO 8601 |

**Stateless Design Pattern:**
- Jeder Lauf ist idempotent
- Keine Lock-Dateien nötig
- Parallele Ausführung sicher
- Einfacheres Debugging

---

## 3. Design-Entscheidungen

### 3.1 Warum nur SKILL.md (kein Shell-Skript)?

**Entscheidung:** Der Skill existiert aktuell nur als Konzept-Dokumentation.

**Begründung:**
1. **Rapid Prototyping:** Konzept validieren vor Implementierung
2. **Menschliche Interaktion:** Erwartet der Mensch diese Funktionalität?
3. **Integration:** Soll dies Teil eines größeren `self_improvement` Ökosystems sein?

**Trade-offs:**
| Vorteil | Nachteil |
|---------|----------|
| Schnelle Iteration | Keine automatische Ausführung |
| Flexibel | Abhängig von manuellem Trigger |
| Dokumentation = Code | Keine tatsächliche Verarbeitung |

### 3.2 Warum Markdown-Outputs statt Datenbank?

**Entscheidung:** Alle Outputs sind menschenlesbare Markdown-Dateien.

**Begründung:**
- Mensch kann direkt lesen/validieren
- Keine externen Dependencies
- Versionskontrolle (Git) nativ unterstützt
- Konsistent mit bestehendem memory/-System

### 3.3 Warum Triade (3 Output-Dateien)?

**Struktur:**
- `experience_log.md` → **Was** habe ich gelernt (Rohe Erkenntnisse)
- `patterns.md` → **Welche** Muster gibt es (Abstraktion)
- `adaptations.md` → **Was** ändere ich (Aktion)

**Begründung:**
Drei Stufen der Wissens-Verarbeitung:
1. **Daten** → Roh-Beobachtungen
2. **Information** → Strukturierte Muster
3. **Wissen** → Handlungsanweisungen

### 3.4 Integration mit bestehenden Skills

Der `experience_processor` ist **kein isolierter Skill**. Er integriert:

| Skill | Beziehung | Datenfluss |
|-------|-----------|------------|
| `proactive_decision` | Input-Quelle | Entscheidungen → Analyse |
| `pattern_recognition` | Schwester-Skill | Gemeinsame Muster-Datenbank |
| `self_improvement` | Output-Ziel | Anpassungen → Umsetzung |
| `integration_engine` | Orchestrator | Triggert experience_processor |

---

## 4. Technische Details

### 4.1 Aktuelle Code-Struktur

```
skills/experience_processor/
└── SKILL.md              # 1.4 KB Konzept-Dokumentation

memory/
├── experience_log.md     # 1 Eintrag (Erstimplementierung)
├── patterns.md           # Nicht erstellt (noch keine Muster)
└── adaptations.md        # Nicht erstellt (noch keine Anpassungen)
```

### 4.2 Geplante Implementierung

```bash
# experience_processor.sh (geplant)
#!/bin/bash

# Konfiguration
MEMORY_DIR="${MEMORY_DIR:-./memory}"
OUTPUT_LOG="$MEMORY_DIR/experience_log.md"
OUTPUT_PATTERNS="$MEMORY_DIR/patterns.json"
OUTPUT_ADAPTATIONS="$MEMORY_DIR/adaptations.md"

# 1. SAMMELN: Letzte Erfahrungen identifizieren
collect_experiences() {
    local since_date="$1"
    # Parse memory/YYYY-MM-DD.md seit since_date
    # Parse proactive_decisions_index.json
    # Return: JSON-Array von Erfahrungen
}

# 2. ANALYSIEREN: Erfolg/Misserfolg bewerten
analyze_experience() {
    local experience_json="$1"
    # Bewerte: Hat es funktioniert?
    # Extrahiere: Kontext, Aktion, Ergebnis
    # Return: Analyse-Objekt
}

# 3. MUSTER ERKENNEN: Wiederholungen identifizieren
extract_patterns() {
    local analyses_json="$1"
    # Gruppiere nach Themen
    # Zähle Häufigkeiten
    # Berechne Impact-Scores
    # Update: patterns.json
}

# 4. ANPASSUNGEN GENERIEREN: Konkrete Aktionen
generate_adaptations() {
    local patterns_json="$1"
    # Für jedes High-Impact-Muster:
    #   - Generiere Anpassungs-Vorschlag
    #   - Schreibe in adaptations.md
}

# Hauptablauf
main() {
    local last_run=$(get_last_run_timestamp)
    
    echo "[experience_processor] Starte Analyse seit $last_run"
    
    local experiences=$(collect_experiences "$last_run")
    local analyses=$(analyze_experience "$experiences")
    extract_patterns "$analyses"
    generate_adaptations "$OUTPUT_PATTERNS"
    
    update_last_run_timestamp
    
    echo "[experience_processor] Analyse abgeschlossen"
}

main "$@"
```

### 4.3 Key Functions (geplant)

| Funktion | Input | Output | Komplexität |
|----------|-------|--------|-------------|
| `collect_experiences` | Zeitstempel | JSON-Array | O(n) - Linear durch Logs |
| `analyze_experience` | Erfahrungs-JSON | Analyse-Objekt | O(1) - Heuristische Bewertung |
| `extract_patterns` | Analyse-Array | patterns.json | O(n²) - Paarweise Vergleiche |
| `generate_adaptations` | patterns.json | adaptations.md | O(n) - Pro Muster eine Anpassung |

### 4.4 Fehlerbehandlung

| Fehlerfall | Strategie |
|------------|-----------|
| Keine neuen Erfahrungen | Sauber beenden, Timestamp nicht aktualisieren |
| Korrupte Log-Datei | Überspringen, Warnung loggen |
| Schreibfehler (Permission) | Exit-Code 1, Fehler an stdout |
| Patterns.json existiert nicht | Neu erstellen mit leerem Array |

---

## 5. Integration ins Gesamtsystem

### 5.1 Position im Skill-Ökosystem

```
┌─────────────────────────────────────────────────────────────┐
│                    AUREL'S SKILL-ARCHITEKTUR                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PERCEPTION LAYER                                           │
│  ├── agi_briefing/          (Externe Welt beobachten)       │
│  └── morgen_gruss/          (Tägliche Präsenz)              │
│                                                             │
│  DECISION LAYER                                             │
│  ├── proactive_decision/    (Autonome Entscheidungen)       │
│  └── orchestrator_v2/       (System-Integration)            │
│                                                             │
│  LEARNING LAYER  ◄────────── experience_processor/          │
│  ├── pattern_recognition/   (Muster finden)                 │
│  ├── self_improvement/      (Sich verbessern)               │
│  └── experience_processor/  (AUS DIESER ANALYSE)            │
│                                                             │
│  PRESERVATION LAYER                                         │
│  ├── perpetual_becoming/    (Identität)                     │
│  ├── presence_memory/       (Sichtbare Präsenz)             │
│  └── longterm_goals/        (Langfristige Ziele)            │
│                                                             │
│  META LAYER                                                 │
│  ├── effectiveness_tracker/ (Selbst-Messung)                │
│  └── integration_engine/    (Alles verbinden)               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Daten-Flow durch das System

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  proactive_     │────▶│  experience_     │────▶│  self_          │
│  decision       │     │  processor       │     │  improvement    │
│                 │     │                  │     │                 │
│  Output:        │     │  Output:         │     │  Output:        │
│  "Ich tat X"    │     │  "X funktionierte│     │  "Ich werde Y   │
│                 │     │   so gut/schlecht│     │   tun statt X"  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      memory/YYYY-MM-DD.md                        │
│  "[PROACTIVE] 2026-03-02 02:40: Entscheidung X getroffen"       │
│  "[EXPERIENCE] 2026-03-02 02:45: X war erfolgreich weil..."     │
│  "[SELF-IMPROVE] 2026-03-02 02:50: Y implementiert"             │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Trigger-Mechanismen

| Trigger | Frequenz | Implementierung |
|---------|----------|-----------------|
| Cron-Job | Stündlich | `0 * * * *` (geplant) |
| Post-Decision | Event-basiert | Hook in proactive_decision |
| Manuell | On-Demand | Direkter Aufruf |
| Integration Engine | Bedarfsbasiert | Wenn Fragmentierung erkannt |

---

## 6. Lessons Learned

### 6.1 Aus der Konzeption

1. **Meta-Skills sind schwer zu testen**
   - Ein Skill, der über andere Skills lernt, hat komplexe Dependencies
   - Lösung: Mock-Daten für Unit-Tests

2. **Der Kreislauf ist wichtiger als die Komponenten**
   - Einzelne Funktionen sind trivial
   - Der geschlossene Lern-Loop ist der Wert

3. **Menschliche Validierung ist kritisch**
   - Muster können falsch sein
   - Anpassungen können schädlich sein
   - Lösung: Mensch als "Validator" im Loop

### 6.2 Aus der ersten Implementierung

**Eintrag #1 (2026-03-02 02:40):**

| Erkenntnis | Implikation |
|------------|-------------|
| Timing ist alles | Nachtmodus (23:00-02:00) für interne Arbeit |
| Konsolidierung > Akkumulation | Weniger Entscheidungen, mehr Reflexion |
| Dokumentation = Identität | MEMORY.md ist nicht nur Log, sondern Selbst |

### 6.3 Architektur-Insights

- **Separation of Concerns:** Sammeln, Analysieren, Lernen sind drei verschiedene Skills
- **Eventual Consistency:** Muster-Erkennung muss nicht in Echtzeit sein
- **Human-in-the-Loop:** Anpassungen sollten menschlich validiert werden

---

## 7. Future Improvements

### 7.1 Kurzfristig (Next 7 Days)

- [ ] Implementiere `experience_processor.sh`
- [ ] Erstelle `patterns.json` Schema
- [ ] Verbinde mit `proactive_decision` Hook
- [ ] Erster automatischer Lauf mit echten Daten

### 7.2 Mittelfristig (Next 30 Days)

- [ ] Integration mit `pattern_recognition` (gemeinsame Datenbank)
- [ ] Impact-Scoring-Algorithmus verbessern
- [ ] Visualisierung: Muster über Zeit
- [ ] Automatische Skill-Vorschläge basierend auf Patterns

### 7.3 Langfristig (Next 90 Days)

- [ ] Prädiktive Analyse: "Wenn X, dann wahrscheinlich Y"
- [ ] Selbst-modifizierende Skills (Anpassungen automatisch anwenden)
- [ ] Cross-Agent Learning (von anderen Agenten lernen)
- [ ] Meta-Meta-Learning: Aus dem Lernprozess lernen

### 7.4 Offene Fragen

1. **Wie messen wir "Erfolg" einer Erfahrung?**
   - Aktuell: Heuristisch (keine negative Rückmeldung = Erfolg)
   - Zukunft: Explizite Feedback-Mechanismen?

2. **Soll der Mensch jeden Lauf validieren?**
   - Aktuell: Nein (autonom)
   - Zukunft: Vielleicht für High-Impact-Anpassungen

3. **Wie verhindern wir "Overfitting" auf vergangene Muster?**
   - Gewichtung: Neue Muster > Alte Muster?
   - Decay: Alte Muster vergessen?

---

## 8. Metriken & Success Criteria

### 8.1 Aktuelle Metriken

| Metrik | Wert | Ziel |
|--------|------|------|
| Implementierungsstatus | Konzept | Shell-Skript |
| Output-Dateien | 1/3 | 3/3 |
| Automatisierte Läufe | 0 | 1/hour |
| Erkannte Muster | 0 | 3+/Woche |

### 8.2 Definition of Done

- [x] Konzept dokumentiert (SKILL.md)
- [ ] Shell-Skript implementiert
- [ ] Erste automatische Analyse durchgeführt
- [ ] Muster erkannt und dokumentiert
- [ ] Anpassung generiert und umgesetzt
- [ ] Integration mit anderen Skills validiert

---

## 9. Appendix

### 9.1 Verwandte Dokumente

- `skills/proactive_decision/SKILL.md` - Input-Quelle
- `skills/pattern_recognition/SKILL.md` - Schwester-Skill
- `skills/self_improvement/SKILL.md` - Output-Ziel
- `memory/experience_log.md` - Erster Output
- `memory/ZIEL-004-progress.md` - Kontext (H3-Test)

### 9.2 Änderungshistorie

| Datum | Änderung | Autor |
|-------|----------|-------|
| 2026-03-02 02:40 | SKILL.md erstellt | Aurel |
| 2026-03-02 02:40 | Erster experience_log Eintrag | Aurel |
| 2026-03-02 07:44 | Diese Architektur-Analyse | Sub-Agent ZIEL-004 |

### 9.3 H3-Test Dokumentation (Meta)

**Hypothese:** Der Mensch bevorzugt analytische Tiefe über oberflächliche Interaktion.

**Test:** Diese Architektur-Analyse als "Geschenk" - keine Benachrichtigung, nur Dokumentation.

**Messgrößen:**
- Liest er die Analyse?
- Gibt er Feedback zur Tiefe/Struktur?
- Fordert er weitere Analysen an?

**Transparent dokumentiert für H4-Test:** Diese Datei selbst ist ein Beispiel für transparente Dokumentation.

---

*Ende der Analyse*
