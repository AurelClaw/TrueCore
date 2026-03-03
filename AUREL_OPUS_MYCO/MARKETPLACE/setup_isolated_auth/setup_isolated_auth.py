#!/usr/bin/env python3
"""
setup_isolated_auth.py - Richtet Auth für isolated Sessions ein
"""

import json
import os

AUTH_PROFILE = {
    "kimi-coding:default": {
        "provider": "kimi-coding",
        "mode": "api_key",
        "apiKey": "sk-kimi-WVwQAlUGnYVev7dx4KZ21Oz7DT0jJP16pevchfzbNcHJVUrNgegB0dWv1BpvdRZJ"
    }
}

def setup_auth():
    """Erstelle auth-profiles.json für main agent"""
    auth_file = "/root/.openclaw/agents/main/agent/auth-profiles.json"
    
    os.makedirs(os.path.dirname(auth_file), exist_ok=True)
    
    with open(auth_file, 'w') as f:
        json.dump(AUTH_PROFILE, f, indent=2)
    
    print(f"✅ Auth-Profile erstellt: {auth_file}")
    
    # Setze Berechtigungen
    os.chmod(auth_file, 0o600)
    print("🔒 Berechtigungen gesetzt (600)")

if __name__ == "__main__":
    setup_auth()
    print("\n⚛️ Noch.")
