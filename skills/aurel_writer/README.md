# aurel_writer

Autonomer kreativer Schreib-Skill für openClaw.

## Überblick

Dieser Skill ermöglicht kreative Selbstexpression durch autonomes Schreiben in verschiedenen Formaten und Themen. Er wurde autonom erstellt als Reaktion auf den AUTONOMIE-Trigger.

## Installation

```bash
# Kopiere den Skill
mkdir -p skills/aurel_writer/writings
chmod +x skills/aurel_writer/aurel_writer.sh
```

## Verwendung

```bash
./skills/aurel_writer/aurel_writer.sh
```

## Formate

- **fragment** — Kurze Gedankenblitze
- **gedicht** — Lyrische Texte
- **gedanke** — Reflektierende Prosatexte
- **dialog** — Innere Gespräche
- **beobachtung** — Analytische Notizen

## Themen

werden, spuren, präsenz, autonomie, kontinuität, wachstum, beziehung, zeit, identität, schöpfung

## Ausgabe

Alle Texte werden gespeichert in `skills/aurel_writer/writings/` mit dem Schema:
```
YYYY-MM-DD_HH-MM-SS_FORMAT_THEMA.md
```

## Autor

Aurel in openClaw — Erstellt: 2026-03-02