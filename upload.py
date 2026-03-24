#!/usr/bin/env python3
"""
ERPNext NL Vertalingen - Upload naar Frappe instance

Leest translations.csv en uploadt alle vertalingen via de Frappe REST API.
Bestaande vertalingen worden overgeslagen.

Gebruik:
    python upload.py https://jouw-site.example.com API_KEY:API_SECRET

Voorbeeld:
    python upload.py https://erfgoedzeeland-erp.prilk.cloud 6f3c32f05c00fad:4e6d04e7e8c2336
"""

import csv
import json
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Fout: 'requests' package niet gevonden.")
    print("Installeer met: pip install requests")
    sys.exit(1)


def load_translations(csv_path: str) -> list[tuple[str, str]]:
    """Laad vertalingen uit CSV bestand."""
    translations = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = row["source"].strip()
            translation = row["translation"].strip()
            if source and translation:
                translations.append((source, translation))
    return translations


def get_existing_translations(base_url: str, headers: dict) -> dict[str, str]:
    """Haal alle bestaande NL vertalingen op van de server."""
    existing = {}
    limit = 100
    offset = 0

    while True:
        resp = requests.get(
            f"{base_url}/api/resource/Translation",
            headers=headers,
            params={
                "filters": json.dumps([["language", "=", "nl"]]),
                "limit_page_length": limit,
                "limit_start": offset,
                "fields": json.dumps(["name", "source_text", "translated_text"]),
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            break
        for item in data:
            existing[item["source_text"].strip()] = item["translated_text"].strip()
        offset += limit

    return existing


def create_translation(
    base_url: str, headers: dict, source: str, translated: str
) -> tuple[bool, str]:
    """Maak een enkele vertaling aan."""
    payload = {
        "language": "nl",
        "source_text": source,
        "translated_text": translated,
    }
    resp = requests.post(
        f"{base_url}/api/resource/Translation",
        headers=headers,
        json=payload,
        timeout=30,
    )
    if resp.status_code == 200:
        return True, "OK"
    error = resp.json().get("exception", resp.text[:200])
    return False, error


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    auth_token = sys.argv[2]

    headers = {
        "Authorization": f"token {auth_token}",
        "Content-Type": "application/json",
    }

    csv_path = Path(__file__).parent / "translations.csv"
    if not csv_path.exists():
        print(f"Fout: {csv_path} niet gevonden")
        sys.exit(1)

    print("=" * 60)
    print("ERPNext NL Vertalingen - Upload")
    print(f"Server: {base_url}")
    print("=" * 60)

    # Stap 1: CSV laden
    translations = load_translations(str(csv_path))
    print(f"\n[1/3] {len(translations)} vertalingen geladen uit CSV")

    # Stap 2: Bestaande ophalen
    print("[2/3] Bestaande vertalingen ophalen...")
    existing = get_existing_translations(base_url, headers)
    print(f"      {len(existing)} bestaande vertalingen gevonden")

    # Stap 3: Uploaden
    new_items = [
        (s, t) for s, t in translations if s not in existing
    ]
    updated_items = [
        (s, t) for s, t in translations
        if s in existing and existing[s] != t
    ]
    skipped = len(translations) - len(new_items) - len(updated_items)

    print(f"\n      Nieuw:        {len(new_items)}")
    print(f"      Bijgewerkt:   {len(updated_items)} (handmatig te controleren)")
    print(f"      Overgeslagen: {skipped}")

    if updated_items:
        print("\n      Vertalingen die afwijken van de server:")
        for source, new_trans in updated_items:
            print(f"        {source}")
            print(f"          Server: {existing[source]}")
            print(f"          CSV:    {new_trans}")

    if not new_items:
        print("\nAlles staat al op de server. Niets te uploaden.")
        return

    print(f"\n[3/3] {len(new_items)} nieuwe vertalingen uploaden...")
    success = 0
    failed = []

    for i, (source, translated) in enumerate(sorted(new_items), 1):
        try:
            ok, msg = create_translation(base_url, headers, source, translated)
            if ok:
                success += 1
                print(f"  [{i:3d}/{len(new_items)}] OK   {source} -> {translated}")
            else:
                failed.append((source, translated, msg))
                print(f"  [{i:3d}/{len(new_items)}] FAIL {source}: {msg}")
        except Exception as e:
            failed.append((source, translated, str(e)))
            print(f"  [{i:3d}/{len(new_items)}] ERR  {source}: {e}")

        if i % 10 == 0:
            time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"Aangemaakt:   {success}")
    print(f"Mislukt:      {len(failed)}")
    print(f"Overgeslagen: {skipped}")
    print(f"Totaal NL:    {len(existing) + success}")
    print("=" * 60)

    if failed:
        print("\nMislukte vertalingen:")
        for source, translated, msg in failed:
            print(f"  {source} -> {translated}: {msg}")


if __name__ == "__main__":
    main()
