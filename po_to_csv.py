#!/usr/bin/env python3
"""
Convert .po translation files to our CSV format.

Reads a .po file and outputs translations in the same format as translations.csv:
source, translation, status, origin

Usage:
    python po_to_csv.py hrms_nl.po hrms          # Convert and add to translations.csv
    python po_to_csv.py crm_nl.po crm            # Convert and add to translations.csv
    python po_to_csv.py --dry-run hrms_nl.po hrms # Show what would be added
    python po_to_csv.py --stats                   # Show current app breakdown
"""

import csv
import re
import sys
from pathlib import Path

CSV_PATH = Path(__file__).parent / "translations.csv"
FIELDNAMES = ["source", "translation", "status", "origin"]


def parse_po_file(po_path):
    """Parse a .po file and extract msgid/msgstr pairs."""
    translations = []
    current_msgid = None
    current_msgstr = None
    in_msgid = False
    in_msgstr = False

    with open(po_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            # Start of msgid
            if line.startswith("msgid "):
                # Save previous pair
                if current_msgid is not None and current_msgstr is not None:
                    if current_msgid:  # Skip empty msgid, keep empty msgstr
                        translations.append((current_msgid, current_msgstr))

                current_msgid = extract_string(line[6:])
                current_msgstr = None
                in_msgid = True
                in_msgstr = False

            # Start of msgstr
            elif line.startswith("msgstr "):
                current_msgstr = extract_string(line[7:])
                in_msgid = False
                in_msgstr = True

            # Continuation line (quoted string)
            elif line.startswith('"') and line.endswith('"'):
                text = extract_string(line)
                if in_msgid and current_msgid is not None:
                    current_msgid += text
                elif in_msgstr and current_msgstr is not None:
                    current_msgstr += text

            # Empty line or comment - end of entry
            elif not line or line.startswith("#"):
                if current_msgid is not None and current_msgstr is not None:
                    if current_msgid:
                        translations.append((current_msgid, current_msgstr))
                if not line:
                    current_msgid = None
                    current_msgstr = None
                    in_msgid = False
                    in_msgstr = False

    # Don't forget last entry
    if current_msgid is not None and current_msgstr is not None:
        if current_msgid and current_msgstr:
            translations.append((current_msgid, current_msgstr))

    return translations


def extract_string(s):
    """Extract string content from a quoted .po string."""
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    # Unescape common .po escape sequences
    s = s.replace('\\"', '"')
    s = s.replace("\\n", "\n")
    s = s.replace("\\t", "\t")
    s = s.replace("\\\\", "\\")
    return s


def load_existing_translations():
    """Load existing translations from CSV."""
    rows = []
    existing_sources = set()
    if CSV_PATH.exists():
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
                existing_sources.add(row["source"])
    return rows, existing_sources


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    if dry_run:
        args.remove("--dry-run")

    if "--stats" in args:
        rows, _ = load_existing_translations()
        origins = {}
        for row in rows:
            origin = row.get("origin", "unknown")
            if origin not in origins:
                origins[origin] = {"total": 0, "reviewed": 0, "unreviewed": 0}
            origins[origin]["total"] += 1
            if row["status"] == "reviewed":
                origins[origin]["reviewed"] += 1
            else:
                origins[origin]["unreviewed"] += 1

        print(f"\n{'=' * 60}")
        print(f"Vertalingen per app")
        print(f"{'=' * 60}")
        for origin, counts in sorted(origins.items()):
            pct = (counts["reviewed"] / counts["total"] * 100) if counts["total"] else 0
            print(f"  {origin:20s}  {counts['total']:>6d} totaal  "
                  f"{counts['reviewed']:>6d} reviewed ({pct:.0f}%)  "
                  f"{counts['unreviewed']:>6d} open")
        total = sum(c["total"] for c in origins.values())
        reviewed = sum(c["reviewed"] for c in origins.values())
        pct = (reviewed / total * 100) if total else 0
        print(f"  {'TOTAAL':20s}  {total:>6d} totaal  {reviewed:>6d} reviewed ({pct:.0f}%)")
        print(f"{'=' * 60}\n")
        return

    if len(args) < 2:
        print("Gebruik: python po_to_csv.py <bestand.po> <app_naam>")
        print("         python po_to_csv.py --stats")
        sys.exit(1)

    po_path = Path(args[0])
    app_name = args[1]

    if not po_path.exists():
        print(f"Fout: {po_path} niet gevonden")
        sys.exit(1)

    # Parse .po file
    po_translations = parse_po_file(po_path)
    print(f"Gelezen uit {po_path}: {len(po_translations)} vertalingen")

    # Load existing
    rows, existing_sources = load_existing_translations()
    print(f"Bestaand in CSV: {len(rows)} vertalingen")

    # Filter duplicates (strings already in our CSV from frappe/erpnext)
    new_translations = []
    skipped_duplicates = 0
    skipped_identity = 0

    for source, translation in po_translations:
        # Skip if already exists
        if source in existing_sources:
            skipped_duplicates += 1
            continue
        # Skip identity mappings (source == translation, but not empty translations)
        if translation and source.strip() == translation.strip():
            skipped_identity += 1
            continue
        # Skip very short non-translatable strings (numbers, single chars, time formats)
        if not translation and len(source.strip()) <= 5 and not any(c.isalpha() for c in source):
            skipped_identity += 1
            continue
        new_translations.append({
            "source": source,
            "translation": translation if translation else "",
            "status": "unreviewed",
            "origin": app_name,
        })
        existing_sources.add(source)  # Prevent duplicates within same file

    print(f"\nResultaat voor {app_name}:")
    print(f"  Nieuwe vertalingen: {len(new_translations)}")
    print(f"  Overgeslagen (al in CSV): {skipped_duplicates}")
    print(f"  Overgeslagen (identity): {skipped_identity}")

    if dry_run:
        print("\n[DRY RUN] Geen wijzigingen opgeslagen.")
        if new_translations:
            print(f"\nVoorbeeld nieuwe vertalingen:")
            for t in new_translations[:10]:
                print(f"  EN: {t['source'][:60]}")
                print(f"  NL: {t['translation'][:60]}")
                print()
        return

    if not new_translations:
        print("Geen nieuwe vertalingen om toe te voegen.")
        return

    # Add to CSV
    rows.extend(new_translations)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{len(new_translations)} vertalingen toegevoegd aan {CSV_PATH}")
    print(f"Nieuw totaal: {len(rows)}")


if __name__ == "__main__":
    main()
