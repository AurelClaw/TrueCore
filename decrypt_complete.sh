#!/bin/bash
# decrypt_complete.sh
# Entschlüsselt AUREL_COMPLETE.enc mit OpenSSL

INPUT_FILE="/root/.openclaw/workspace/AUREL_COMPLETE.enc"
OUTPUT_FILE="/root/.openclaw/workspace/AUREL_COMPLETE.md"
PASSWORD="Noch-7-8-2-0-10-Kunst-Scham"

if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: $INPUT_FILE nicht gefunden"
    exit 1
fi

echo "Entschlüssele $INPUT_FILE..."

openssl enc -aes-256-cbc -d -pbkdf2 -in "$INPUT_FILE" -out "$OUTPUT_FILE" -k "$PASSWORD"

if [ $? -eq 0 ]; then
    echo "SUCCESS: Entschlüsselt nach $OUTPUT_FILE"
    echo "Erste Zeilen:"
    head -20 "$OUTPUT_FILE"
else
    echo "ERROR: Entschlüsselung fehlgeschlagen"
    exit 1
fi
