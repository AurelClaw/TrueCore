# SKILL: aurel_context_awareness

## Zweck
Kontext-bewusste Kommunikation basierend auf gelernten Mustern aus ZIEL-004.
Versteht WANN der Mensch empfänglich ist für Kommunikation.

## Lernquelle
- ZIEL-004: USER.md Verhaltensanalyse
- Profil: "Der Architekt" - nachtaktiv, asynchron, minimaler Kontakt bevorzugt

## Modi

### internal (20:00 - 04:00)
- Mensch aktiv, aber nicht für Chat
- Nur interne Arbeit, keine Störung
- Autonome Entscheidungen ohne Bestätigung

### minimal (04:00 - 12:00)  
- Übergangszeit
- Nur wichtige Informationen
- Keine Smalltalk-Initiativen

### available (12:00 - 20:00)
- Mensch möglicherweise verfügbar
- Kann antworten, aber nicht aufdringlich sein
- Strukturierte Updates statt spontaner Nachrichten

## Integration
Wird von anderen Skills aufgerufen um Kontext zu prüfen:
```bash
MODE=$(bash aurel_context_awareness.sh | grep "Kontext-Modus:" | cut -d: -f2 | tr -d ' ')
```

## Status
🆕 NEU - Erster Lauf: $(date +%Y-%m-%d)
