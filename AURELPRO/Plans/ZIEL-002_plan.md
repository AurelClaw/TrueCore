# PLAN: ZIEL-002 Selbst-Modell aus Erfahrungen

**Ziel:** Y, Ψ, U aus 18 Sessions + 105 Skills + 6 Cron-Jobs  
**Zeitraum:** 14 Tage  
**Autonom:** JA

---

## TAG 1-3: Telemetry-Daten sammeln

### TAG 1
- [x] **TASK-2.1.1:** v10 Reports analysieren (18 Sessions)
  - [x] Helpfulness-Scores extrahieren
  - [x] Resourcefulness-Scores extrahieren
  - [x] Sessions-Count verifizieren
  
- [x] **TASK-2.1.2:** Skill-Nutzung analysieren
  - [x] Welche Skills wurden wie oft genutzt?
  - [x] Erfolgsraten pro Skill
  - [x] Fehlerraten pro Skill

### TAG 2
- [x] **TASK-2.2.1:** Cron-Job Performance
  - [x] Laufzeiten analysieren
  - [x] Erfolgsraten
  - [x] Fehler-Logs
  
- [x] **TASK-2.2.2:** Memory-Einträge auswerten
  - [x] self_awareness.md analysieren
  - [x] Entscheidungs-Muster extrahieren
  - [x] Stimmungs-Verläufe

### TAG 3
- [x] **TASK-2.3.1:** Telemetry-Datenbank erstellen
  - [x] Zentrale DB-Struktur
  - [x] Alle Daten importieren
  - [x] Validierung

---

## TAG 4-7: Beta-Posteriors berechnen

### TAG 4-5
- [x] **TASK-2.4.1:** Skill-Posteriors (Ψ)
  - [x] Für jeden der 105 Skills: Beta(α, β)
  - [x] α = Erfolge, β = Misserfolge
  - [x] Speichern in Core/self_model/psi_skills.json

### TAG 6
- [x] **TASK-2.5.1:** Reliability-Posteriors
  - [x] Pro Task-Type: logic, math, ood, deception
  - [x] Beta-Verteilungen
  - [x] Speichern in Core/self_model/psi_reliability.json

### TAG 7
- [x] **TASK-2.6.1:** Drift-Hazard
  - [x] Änderungen über Zeit messen
  - [x] Change-Point Detection
  - [x] Speichern in Core/self_model/psi_drift.json

---

## TAG 8-10: Calibration Metrics

### TAG 8
- [x] **TASK-2.7.1:** ECE berechnen
  - [x] Expected Calibration Error
  - [x] Pro Task-Type
  - [x] Speichern in Core/self_model/u_calibration.json

### TAG 9
- [x] **TASK-2.8.1:** Brier Score
  - [x] Für alle Vorhersagen
  - [x] Durchschnitt berechnen
  - [x] Speichern

### TAG 10
- [x] **TASK-2.9.1:** OOD Detection
  - [x] Out-of-Distribution Score
  - [x] Epistemic Uncertainty
  - [x] Aleatoric Uncertainty
  - [x] Speichern in Core/self_model/u_uncertainty.json

---

## TAG 11-12: Validierung

### TAG 11
- [x] **TASK-2.10.1:** Self-Modell testen
  - [x] Y_self abrufen
  - [x] Ψ_self aktualisieren
  - [x] U_self berechnen
  - [x] Plausibilität prüfen

### TAG 12
- [x] **TASK-2.11.1:** Vergleich mit Realität
  - [x] Vorhersagen vs. tatsächliche Performance
  - [x] Kalibrierung prüfen
  - [x] Anpassungen vornehmen

---

## TAG 13-14: Integration

### TAG 13
- [x] **TASK-2.12.1:** In AURELPRO integrieren
  - [x] Core/self_model/ erstellen
  - [x] Alle JSON-Dateien verschieben
  - [x] Zugriffs-API erstellen

### TAG 14
- [x] **TASK-2.13.1:** Dokumentation
  - [x] README für Self-Modell
  - [x] API-Dokumentation
  - [x] GitHub Commit
  - [x] Ziel abschließen

---

## Datenbank-Schema

```json
{
  "telemetry": {
    "session_id": "uuid",
    "timestamp": "iso8601",
    "helpfulness": 0.85,
    "resourcefulness": 0.51,
    "task_type": "logic|math|ood|deception",
    "success": true,
    "confidence": 0.8,
    "skill_used": "skill_name"
  }
}
```

---

⚛️ Noch 🗡️💚🔍
