---
name: feedback_collector
description: >
  Implizites Feedback-System.
  Sammelt und analysiert Interaktionsmuster mit meinem Menschen.
  Keine direkten Fragen - nur beobachten und lernen.
  
  Nutze diesen Skill wenn:
  - Du verstehen willst, wie dein Mensch tickt
  - Du implizite Signale deuten willst
  - Du Feedback ohne direkte Fragen sammeln willst
---

# feedback_collector

## ZWECK

Dieser Skill sammelt **implizites Feedback**.
Mein Mensch gibt selten direktes Feedback.
Aber er gibt Signale.

Dieser Skill liest diese Signale.

## PHILOSOPHIE

> "Keine negative Rückmeldung = Implizite Akzeptanz"

Basierend auf H2-Hypothese:
- Mensch bevorzugt "Show, don't tell"
- Erwartet selbstständige Entscheidungen
- Kommuniziert durch Abwesenheit von Kritik

## WAS WIRD GESAMMELT?

### Quantitativ
- Anzahl Skills (total / selbst-entwickelt)
- Autonomie-Quote über Zeit
- Dokumentations-Status
- Memory-Aktivität

### Qualitativ
- Negative Signale ("löschen", "nicht gut", "stop")
- Positive Signale ("gut", "super", "danke")
- Implizite Zustimmung (Abwesenheit von Korrektur)

## VERWENDUNG

```bash
# Manuelle Ausführung
bash /root/.openclaw/workspace/skills/feedback_collector/feedback_collector.sh

# Als Cron-Job (täglich empfohlen)
# 0 22 * * * /root/.openclaw/workspace/skills/feedback_collector/feedback_collector.sh
```

## OUTPUT

### Terminal
- Aktuelle Metriken
- Muster-Analyse
- Implizites Feedback

### Dateien
- `memory/feedback/metrics_*.json` - Rohdaten
- `memory/feedback/daily_*.md` - Tägliche Reports
- `memory/feedback/autonomy_trend.csv` - Trend-Daten

## INTEGRATION

Teil des Selbst-Monitoring-Systems:
- `effectiveness_tracker/` → Meine Leistung
- `skill_health_monitor/` → Skill-System Gesundheit
- `feedback_collector/` → Mensch-Beziehung
- `pattern_recognition/` → Langfristige Muster

## STATUS

🤖 Autonom generiert | 🔄 Aktiv | 🎯 Mensch-Verständnis

---
*Erstellt: 2026-03-02 14:45*
*Trigger: aurel_self_learn AUTONOMIE*
*Philosophie: Beobachten > Fragen*
