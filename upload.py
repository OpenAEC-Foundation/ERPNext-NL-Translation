#!/usr/bin/env python3
"""
ERPNext NL Vertalingen - Upload pipeline

Leest translations.csv en synchroniseert alle reviewed vertalingen
naar een Frappe instance via de REST API.

Gebruik:
    python upload.py https://jouw-site.example.com API_KEY:API_SECRET [--all]

Opties:
    --all       Upload ook unreviewed vertalingen (standaard: alleen reviewed)
    --sync      Verwijder vertalingen van server die niet in CSV staan
    --dry-run   Toon wat er zou gebeuren zonder wijzigingen te maken

Voorbeeld:
    python upload.py https://erfgoedzeeland-erp.prilk.cloud 6f3c32f05c00fad:4e6d04e7e8c2336
    python upload.py https://erfgoedzeeland-erp.prilk.cloud 6f3c32f05c00fad:4e6d04e7e8c2336 --all
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


def load_translations(csv_path: str, include_unreviewed: bool = False) -> list[dict]:
    """Laad vertalingen uit CSV bestand."""
    translations = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = row["source"].strip()
            translation = row["translation"].strip()
            status = row.get("status", "reviewed").strip()
            if source and translation:
                if include_unreviewed or status == "reviewed":
                    translations.append({
                        "source": source,
                        "translation": translation,
                        "status": status,
                    })
    return translations


def get_existing_translations(base_url: str, headers: dict) -> dict[str, dict]:
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
            existing[item["source_text"].strip()] = {
                "name": item["name"],
                "translated_text": item["translated_text"].strip(),
            }
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


def update_translation(
    base_url: str, headers: dict, name: str, translated: str
) -> tuple[bool, str]:
    """Werk een bestaande vertaling bij."""
    resp = requests.put(
        f"{base_url}/api/resource/Translation/{name}",
        headers=headers,
        json={"translated_text": translated},
        timeout=30,
    )
    if resp.status_code == 200:
        return True, "OK"
    error = resp.json().get("exception", resp.text[:200])
    return False, error


def delete_translation(
    base_url: str, headers: dict, name: str
) -> tuple[bool, str]:
    """Verwijder een vertaling."""
    resp = requests.delete(
        f"{base_url}/api/resource/Translation/{name}",
        headers=headers,
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
    flags = set(sys.argv[3:])
    include_all = "--all" in flags
    do_sync = "--sync" in flags
    dry_run = "--dry-run" in flags

    headers = {
        "Authorization": f"token {auth_token}",
        "Content-Type": "application/json",
    }

    csv_path = Path(__file__).parent / "translations.csv"
    if not csv_path.exists():
        print(f"Fout: {csv_path} niet gevonden")
        sys.exit(1)

    mode = "ALLE" if include_all else "REVIEWED"
    print("=" * 60)
    print(f"ERPNext NL Vertalingen - Upload ({mode})")
    print(f"Server: {base_url}")
    if dry_run:
        print("MODUS: Dry run (geen wijzigingen)")
    print("=" * 60)

    # Stap 1: CSV laden
    translations = load_translations(str(csv_path), include_all)
    csv_dict = {t["source"]: t["translation"] for t in translations}
    print(f"\n[1/3] {len(translations)} vertalingen geladen uit CSV ({mode})")

    # Stap 2: Bestaande ophalen
    print("[2/3] Bestaande vertalingen ophalen van server...")
    existing = get_existing_translations(base_url, headers)
    print(f"      {len(existing)} vertalingen op server")

    # Stap 3: Analyse
    to_create = []
    to_update = []
    to_skip = []
    for t in translations:
        source = t["source"]
        if source not in existing:
            to_create.append(t)
        elif existing[source]["translated_text"] != t["translation"]:
            to_update.append({**t, "name": existing[source]["name"]})
        else:
            to_skip.append(t)

    to_delete = []
    if do_sync:
        for source, info in existing.items():
            if source not in csv_dict:
                to_delete.append({"source": source, "name": info["name"]})

    print(f"\n      Nieuw:        {len(to_create)}")
    print(f"      Bijwerken:    {len(to_update)}")
    print(f"      Overgeslagen: {len(to_skip)}")
    if do_sync:
        print(f"      Verwijderen:  {len(to_delete)}")

    if to_update:
        print("\n      Vertalingen die bijgewerkt worden:")
        for t in to_update[:20]:
            print(f"        {t['source']}")
            print(f"          Oud: {existing[t['source']]['translated_text']}")
            print(f"          Nieuw: {t['translation']}")
        if len(to_update) > 20:
            print(f"        ... en {len(to_update) - 20} meer")

    if dry_run:
        print("\nDry run. Geen wijzigingen gemaakt.")
        return

    # Stap 4: Uitvoeren
    total_ops = len(to_create) + len(to_update) + len(to_delete)
    if total_ops == 0:
        print("\nAlles is in sync. Niets te doen.")
        return

    success = 0
    failed = []
    i = 0

    for t in to_create:
        i += 1
        try:
            ok, msg = create_translation(base_url, headers, t["source"], t["translation"])
            if ok:
                success += 1
                print(f"  [{i:4d}/{total_ops}] NEW  {t['source']} -> {t['translation']}")
            else:
                failed.append((t["source"], msg))
                print(f"  [{i:4d}/{total_ops}] FAIL {t['source']}: {msg}")
        except Exception as e:
            failed.append((t["source"], str(e)))
            print(f"  [{i:4d}/{total_ops}] ERR  {t['source']}: {e}")
        if i % 10 == 0:
            time.sleep(0.3)

    for t in to_update:
        i += 1
        try:
            ok, msg = update_translation(base_url, headers, t["name"], t["translation"])
            if ok:
                success += 1
                print(f"  [{i:4d}/{total_ops}] UPD  {t['source']} -> {t['translation']}")
            else:
                failed.append((t["source"], msg))
                print(f"  [{i:4d}/{total_ops}] FAIL {t['source']}: {msg}")
        except Exception as e:
            failed.append((t["source"], str(e)))
            print(f"  [{i:4d}/{total_ops}] ERR  {t['source']}: {e}")
        if i % 10 == 0:
            time.sleep(0.3)

    for t in to_delete:
        i += 1
        try:
            ok, msg = delete_translation(base_url, headers, t["name"])
            if ok:
                success += 1
                print(f"  [{i:4d}/{total_ops}] DEL  {t['source']}")
            else:
                failed.append((t["source"], msg))
                print(f"  [{i:4d}/{total_ops}] FAIL {t['source']}: {msg}")
        except Exception as e:
            failed.append((t["source"], str(e)))
            print(f"  [{i:4d}/{total_ops}] ERR  {t['source']}: {e}")
        if i % 10 == 0:
            time.sleep(0.3)

    print("\n" + "=" * 60)
    print(f"Gelukt:       {success}")
    print(f"Mislukt:      {len(failed)}")
    print(f"Overgeslagen: {len(to_skip)}")
    print("=" * 60)

    if failed:
        print("\nMislukte bewerkingen:")
        for source, msg in failed:
            print(f"  {source}: {msg}")


if __name__ == "__main__":
    main()
