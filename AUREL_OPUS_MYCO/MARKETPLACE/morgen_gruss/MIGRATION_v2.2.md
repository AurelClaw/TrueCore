# Migrations-Guide: Morgengruß v2.0/v2.1 → v2.2

## Überblick

Diese Anleitung beschreibt die Migration von Morgengruß v2.0 oder v2.1 auf die finale Version v2.2 mit Wetter- und Kalender-Integration.

## Was ist neu in v2.2?

### 🌟 Haupt-Features
1. **Kalender-Integration** - Zeigt heutige Termine und nächsten Termin
2. **Kontextbezogene Grußformeln** - Kombiniert Wetter + Kalender ("Heute regnet es, nimm einen Schirm mit. Du hast um 10:00 einen Termin.")
3. **Graceful Degradation** - Funktioniert auch ohne Wetter/Kalender
4. **System-Status-Anzeige** - Zeigt welche Module aktiv sind

### 📊 Vergleich

| Feature | v2.0 | v2.1 | v2.2 |
|---------|------|------|------|
| Dynamische Grüße | ✅ | ✅ | ✅ |
| Wetter-Integration | ❌ | ✅ | ✅ |
| Kalender-Integration | ❌ | ❌ | ✅ |
| Kontext-Grüße | ❌ | ❌ | ✅ |
| Graceful Degradation | ❌ | ⚠️ | ✅ |

## Migrationsschritte

### Schritt 1: Backup erstellen

```bash
cd /root/.openclaw/workspace/skills/morgen_gruss

# Backup der aktuellen Version
cp morgen_gruss_v2.sh morgen_gruss_v2.sh.backup.$(date +%Y%m%d)

# Falls v2.1 existiert
cp morgen_gruss_v2.1.sh morgen_gruss_v2.1.sh.backup.$(date +%Y%m%d) 2>/dev/null || true
```

### Schritt 2: Voraussetzungen prüfen

#### Wetter-Integration (sollte bereits vorhanden sein)
```bash
# Prüfe ob Wetter-Modul existiert
ls -la skills/wetter_integration/wetter_integration.sh

# Teste Wetter-Modul
bash skills/wetter_integration/wetter_integration.sh short
```

**Falls nicht vorhanden:**
Siehe `skills/wetter_integration/SKILL.md` für Installationsanleitung.

#### Kalender-Integration (neu in v2.2)
```bash
# Prüfe ob Kalender-Modul existiert
ls -la skills/kalender_integration/kalender_integration.sh
```

**Falls nicht vorhanden:**
Siehe `skills/kalender_integration/SKILL.md` für Installationsanleitung.

### Schritt 3: Kalender konfigurieren (optional aber empfohlen)

```bash
# Erstelle Konfigurationsdatei
mkdir -p .config

# Füge Kalender-Quellen hinzu
cat > .config/calendar_sources << 'EOF'
# Kalender-Quellen für kalender_integration
# Format: NAME|TYPE|PATH/URL
# 
# Lokale ICS-Datei
MeinKalender|ics|/pfad/zu/deinem/kalender.ics

# Entfernte ICS-Datei (URL)
# Arbeit|ics|https://example.com/calendar.ics
EOF

# Passe den Pfad an deine ICS-Datei an
# Oder lasse es leer für Demo-Modus
```

### Schritt 4: Neue Version testen

```bash
# Führe v2.2 aus
bash skills/morgen_gruss/morgen_gruss_v2.2.sh

# Prüfe die Ausgabe
cat gifts/morgen_gruss_$(date +%Y-%m-%d).md
```

**Erwartete Ausgabe:**
- Kontextbezogener Gruß ODER klassischer Gruß
- Wetter-Info (falls konfiguriert)
- Kalender-Info (falls konfiguriert)
- System-Status am Ende

### Schritt 5: Cron-Job aktualisieren (falls vorhanden)

Falls du einen Cron-Job für den Morgengruß hast:

```bash
# Zeige aktuelle Cron-Jobs
crontab -l | grep morgen_gruss

# Aktualisiere auf v2.2
# Alt: 0 8 * * * cd /root/.openclaw/workspace && bash skills/morgen_gruss/morgen_gruss_v2.sh
# Neu: 0 8 * * * cd /root/.openclaw/workspace && bash skills/morgen_gruss/morgen_gruss_v2.2.sh
```

### Schritt 6: Integration mit anderen Skills aktualisieren

Falls `morning_presence` oder andere Skills den Morgengruß aufrufen:

```bash
# Suche nach Verwendungen von morgen_gruss_v2
grep -r "morgen_gruss_v2" skills/ --include="*.sh" | grep -v "v2.2"

# Aktualisiere auf v2.2
# Beispiel in morning_presence/skill.sh:
# Alt: bash "$SKILLS_DIR/morgen_gruss/morgen_gruss_v2.sh"
# Neu: bash "$SKILLS_DIR/morgen_gruss/morgen_gruss_v2.2.sh"
```

## Konfigurations-Optionen

### Minimal (nur v2.0 Features)
Keine zusätzliche Konfiguration nötig. v2.2 funktioniert ohne Wetter/Kalender als v2.0.

### Standard (Wetter + Demo-Kalender)
```bash
# Wetter-Modul vorhanden
# Keine Kalender-Konfiguration → Demo-Modus aktiviert
```

### Vollständig (Wetter + Echter Kalender)
```bash
# Wetter-Modul vorhanden
# .config/calendar_sources mit ICS-Datei(en) konfiguriert
```

## Fehlerbehebung

### Problem: "Kalender-Integration nicht verfügbar"

**Ursache:** Kalender-Modul nicht gefunden oder nicht funktionsfähig

**Lösung:**
```bash
# Prüfe ob Modul existiert
ls -la skills/kalender_integration/kalender_integration.sh

# Teste Modul manuell
bash skills/kalender_integration/kalender_integration.sh short

# Prüfe Berechtigungen
chmod +x skills/kalender_integration/kalender_integration.sh
```

### Problem: "Wetter-Integration nicht verfügbar"

**Ursache:** Wetter-Modul nicht gefunden

**Lösung:**
```bash
# Prüfe ob Modul existiert
ls -la skills/wetter_integration/wetter_integration.sh

# Teste Modul manuell
bash skills/wetter_integration/wetter_integration.sh short
```

### Problem: Keine kontextbezogenen Grüße

**Ursache:** 
- 30% der Grüße sind absichtlich klassisch (Variation)
- Module nicht verfügbar

**Lösung:**
```bash
# Prüfe System-Status in der Ausgabe
# Suche nach "Gruß-Typ: Contextual" vs "Gruß-Typ: Warm/Energetic/..."
```

### Problem: Kalender zeigt Demo-Termine statt echte

**Ursache:** Keine Kalender-Quellen konfiguriert

**Lösung:**
```bash
# Konfiguriere .config/calendar_sources
cat > .config/calendar_sources << 'EOF'
MeinKalender|ics|/pfad/zu/deinem/kalender.ics
EOF
```

## Rollback

Falls Probleme auftreten:

```bash
cd /root/.openclaw/workspace/skills/morgen_gruss

# Stelle v2.0/v2.1 wieder her
cp morgen_gruss_v2.sh.backup.* morgen_gruss_v2.sh

# Aktualisiere Cron-Jobs/Integrationen zurück
crontab -e
# ... ändere v2.2 zurück zu v2.0/v2.1
```

## Zusammenfassung

| Schritt | Zeitaufwand | Komplexität |
|---------|-------------|-------------|
| Backup | 1 Min | ⭐ |
| Voraussetzungen prüfen | 2 Min | ⭐⭐ |
| Kalender konfigurieren | 5 Min | ⭐⭐⭐ |
| Testen | 2 Min | ⭐ |
| Cron-Job aktualisieren | 2 Min | ⭐⭐ |
| **Gesamt** | **~12 Min** | **⭐⭐** |

## Support

Bei Problemen:
1. Prüfe `skills/wetter_integration/SKILL.md`
2. Prüfe `skills/kalender_integration/SKILL.md`
3. Siehe Troubleshooting-Sektion oben
4. Führe Module manuell aus um Fehler zu isolieren

---

**Migration erfolgreich!** 🎉

Du hast jetzt den vollständig integrierten Morgengruß v2.2 mit Wetter- und Kalender-Unterstützung.

⚛️ Noch 🗡️💚🔍
