# State Representation Design

## Ziel

Definition der Zustandsrepräsentation für das World Model System.

## Anforderungen

1. **Vollständigkeit**: Alle relevanten Aspekte der "Welt" abbilden
2. **Komprimierbarkeit**: Latent space Darstellung ermöglichen
3. **Aktualisierbarkeit**: Inkrementelle Updates unterstützen
4. **Interpretierbarkeit**: Menschlich lesbare Komponenten

## Zustandskomponenten

### 1. Zeitliche Dimension
```json
{
  "timestamp": "ISO8601",
  "time_of_day": "morning|afternoon|evening|night",
  "day_of_week": 0-6,
  "week_of_year": 1-52,
  "is_weekend": boolean,
  "is_holiday": boolean
}
```

### 2. Kontextuelle Dimension
```json
{
  "location": "home|work|travel|unknown",
  "activity_context": "focused|available|busy|sleeping",
  "last_interaction_minutes_ago": number,
  "recent_topics": ["string"],
  "open_goals": ["goal_id"]
}
```

### 3. System-Dimension
```json
{
  "active_skills": ["skill_name"],
  "running_processes": ["process_id"],
  "pending_notifications": number,
  "system_load": 0.0-1.0,
  "recent_events": ["event_type"]
}
```

### 4. Mensch-Dimension (geschätzt)
```json
{
  "mood_estimate": "positive|neutral|negative|unknown",
  "engagement_level": "high|medium|low|none",
  "preferred_communication": "verbose|concise|silent",
  "recent_successes": ["string"],
  "recent_frustrations": ["string"]
}
```

### 5. Environment-Dimension
```json
{
  "weather": {
    "condition": "sunny|cloudy|rainy|snowy",
    "temperature": number,
    "humidity": number
  },
  "calendar_load": "light|medium|heavy",
  "upcoming_events": [{"title": "", "minutes_until": number}]
}
```

## Latent Space Encoding

### V1: Simple Concatenation
Alle Dimensionen → Vektor → Komprimierung

### V2: Structured Latents
Separate latente Repräsentationen pro Dimension:
- z_time: Zeitliche Muster
- z_context: Kontextuelle Muster
- z_system: System-Muster
- z_human: Mensch-Muster
- z_env: Environment-Muster

### V3: Hierarchical
Globale latente Variable + spezifische latente Variablen

## Datenquellen

| Dimension | Quelle | Update-Frequenz |
|-----------|--------|-----------------|
| Zeit | System-Clock | Kontinuierlich |
| Kontext | Memory-System | Bei Interaktion |
| System | Process-Monitor | Alle 5 Minuten |
| Mensch | Inferenz aus Verhalten | Bei Interaktion |
| Environment | Wetter/Kalender-Integration | Stündlich |

## Nächster Schritt

Implementierung der State-Klasse:
1. State-Klasse definieren
2. State-Collector implementieren
3. Erste Daten sammeln

---
**Status:** Design abgeschlossen
**Nächste Aktion:** State-Klasse implementieren
