#!/usr/bin/env python3
"""
ERPNext NL Vertalingen - Review tool

Interactief ongereviewed vertalingen beoordelen. Per vertaling kun je:
  [enter]  Goedkeuren (markeer als reviewed)
  [n]      Nieuwe vertaling invoeren
  [d]      Verwijderen (slechte vertaling, niet opnemen)
  [s]      Overslaan (later beoordelen)
  [q]      Stoppen

Gebruik:
    python review.py                    # Start bij het begin
    python review.py --from 100         # Start bij regel 100
    python review.py --search "invoice" # Zoek specifieke termen
    python review.py --stats            # Toon voortgang
"""

import csv
import sys
from pathlib import Path

CSV_PATH = Path(__file__).parent / "translations.csv"
FIELDNAMES = ["source", "translation", "status", "origin"]


def load_all():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def save_all(rows):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def show_stats(rows):
    reviewed = sum(1 for r in rows if r["status"] == "reviewed")
    unreviewed = sum(1 for r in rows if r["status"] == "unreviewed")
    deleted = sum(1 for r in rows if r["status"] == "deleted")
    total = len(rows)
    pct = (reviewed / total * 100) if total else 0

    print(f"\n{'=' * 50}")
    print(f"Voortgang: {reviewed}/{total} ({pct:.1f}%)")
    print(f"  Reviewed:   {reviewed}")
    print(f"  Unreviewed: {unreviewed}")
    print(f"  Verwijderd: {deleted}")
    print(f"{'=' * 50}\n")

    # Per origin
    origins = {}
    for r in rows:
        o = r.get("origin", "unknown")
        if o not in origins:
            origins[o] = {"reviewed": 0, "unreviewed": 0, "deleted": 0}
        origins[o][r["status"]] = origins[o].get(r["status"], 0) + 1

    print(f"  {'Origin':<12} {'Reviewed':>10} {'Unreviewed':>12} {'Deleted':>10}")
    print(f"  {'-' * 46}")
    for o in sorted(origins):
        r = origins[o]
        print(f"  {o:<12} {r.get('reviewed',0):>10} {r.get('unreviewed',0):>12} {r.get('deleted',0):>10}")


def review_interactive(rows, start=0, search=None):
    unreviewed = [
        (i, r) for i, r in enumerate(rows)
        if r["status"] == "unreviewed"
    ]

    if search:
        search_lower = search.lower()
        unreviewed = [
            (i, r) for i, r in unreviewed
            if search_lower in r["source"].lower() or search_lower in r["translation"].lower()
        ]
        print(f"\n{len(unreviewed)} resultaten voor '{search}'")

    if start > 0:
        unreviewed = unreviewed[start:]

    if not unreviewed:
        print("\nGeen ongereviewed vertalingen gevonden!")
        return

    print(f"\n{len(unreviewed)} vertalingen te reviewen")
    print("Commando's: [enter]=goedkeuren [n]=nieuwe vertaling [d]=verwijderen [s]=overslaan [q]=stoppen\n")

    changed = 0
    for count, (idx, row) in enumerate(unreviewed, 1):
        print(f"[{count}/{len(unreviewed)}] ({row['origin']})")
        print(f"  EN: {row['source']}")
        print(f"  NL: {row['translation']}")

        while True:
            choice = input("  > ").strip().lower()

            if choice == "" or choice == "y":
                rows[idx]["status"] = "reviewed"
                changed += 1
                print("  -> Goedgekeurd")
                break
            elif choice == "n":
                new_trans = input("  Nieuwe vertaling: ").strip()
                if new_trans:
                    rows[idx]["translation"] = new_trans
                    rows[idx]["status"] = "reviewed"
                    changed += 1
                    print(f"  -> Bijgewerkt: {new_trans}")
                    break
                else:
                    print("  Lege invoer, probeer opnieuw")
            elif choice == "d":
                rows[idx]["status"] = "deleted"
                changed += 1
                print("  -> Verwijderd")
                break
            elif choice == "s":
                print("  -> Overgeslagen")
                break
            elif choice == "q":
                if changed:
                    save_all(rows)
                    print(f"\n{changed} wijzigingen opgeslagen.")
                return
            else:
                print("  Onbekend commando. Gebruik: [enter] [n] [d] [s] [q]")

        # Elke 10 wijzigingen tussentijds opslaan
        if changed > 0 and changed % 10 == 0:
            save_all(rows)
            print(f"  ({changed} wijzigingen opgeslagen)")

    if changed:
        save_all(rows)
        print(f"\nKlaar! {changed} wijzigingen opgeslagen.")


def main():
    rows = load_all()

    if "--stats" in sys.argv:
        show_stats(rows)
        return

    start = 0
    search = None

    for i, arg in enumerate(sys.argv):
        if arg == "--from" and i + 1 < len(sys.argv):
            start = int(sys.argv[i + 1])
        if arg == "--search" and i + 1 < len(sys.argv):
            search = sys.argv[i + 1]

    show_stats(rows)
    review_interactive(rows, start, search)


if __name__ == "__main__":
    main()
