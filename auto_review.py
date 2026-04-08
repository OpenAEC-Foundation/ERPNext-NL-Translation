#!/usr/bin/env python3
"""
ERPNext NL Vertalingen - Automatische AI Review Pipeline

Verwerkt ongereviewed vertalingen in batches via de Anthropic API.
Per vertaling wordt gecontroleerd:
  1. Is de Nederlandse vertaling correct en natuurlijk?
  2. Moet de term in het Engels blijven (gangbaar vakjargon)?
  3. Is er een betere vertaling?

Gebruik:
    python auto_review.py                     # Verwerk alle unreviewed
    python auto_review.py --batch-size 100    # Grotere batches
    python auto_review.py --origin erpnext    # Alleen ERPNext vertalingen
    python auto_review.py --dry-run           # Toon resultaten zonder opslaan
    python auto_review.py --stats             # Toon voortgang
    python auto_review.py --resume            # Hervat na onderbreking

Vereisten:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-...
"""

import csv
import json
import os
import sys
import time
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Fout: 'anthropic' package niet gevonden.")
    print("Installeer met: pip install anthropic")
    sys.exit(1)

CSV_PATH = Path(__file__).parent / "translations.csv"
PROGRESS_PATH = Path(__file__).parent / ".auto_review_progress.json"
LIVE_PATH = Path(__file__).parent / ".live_review.json"
FIELDNAMES = ["source", "translation", "status", "origin"]

# Termen die NIET vertaald moeten worden (gangbaar Engels in NL bedrijfsleven)
KEEP_ENGLISH = {
    "dashboard", "template", "export", "import", "manager", "email", "server",
    "widget", "login", "logout", "pdf", "api", "crm", "pos", "bom", "uom",
    "budget", "workflow", "routing", "prospect", "contract", "scorecard", "hr",
    "batch", "serial", "stock", "lead", "pipeline", "setup", "backup", "log",
    "webhook", "sandbox", "cache", "module", "patch", "bench", "site",
    "chart", "report", "print", "format", "status", "draft", "submit",
    "cancel", "amend", "link", "check", "data", "select", "attach",
}

SYSTEM_PROMPT = """Je bent een expert vertaler Engels-Nederlands voor ERPNext/Frappe bedrijfssoftware.

Je taak: beoordeel of Nederlandse vertalingen correct en natuurlijk zijn voor gebruik in een ERP-systeem in Nederland.

REGELS:
1. Nederlandse vertalingen moeten klinken zoals een Nederlandse boekhouder, projectleider of HR-medewerker ze zou gebruiken.
2. Vakjargon dat in het Nederlands bedrijfsleven STANDAARD in het Engels wordt gebruikt, moet Engels BLIJVEN:
   - IT/software: Dashboard, Login, Server, API, Widget, Template, Export, Import, Backup, Cache, Webhook
   - Business: Budget, Contract, Manager, Lead, Pipeline, Prospect, Workflow, Scorecard, CRM, POS, HR
   - ERP-specifiek: BOM (Bill of Materials), UOM (Unit of Measure), Stock, Batch, Serial
3. Vertaal WEL wanneer er een gangbaar Nederlands woord bestaat dat in de praktijk wordt gebruikt:
   - Invoice -> Factuur, Customer -> Klant, Supplier -> Leverancier, Employee -> Werknemer
   - Quotation -> Offerte, Purchase Order -> Inkooporder, Sales Order -> Verkooporder
   - Warehouse -> Magazijn, Payment -> Betaling, Journal Entry -> Journaalboeking
4. Gebruik GEEN letterlijke vertalingen die onnatuurlijk klinken:
   - FOUT: "Attachment" -> "Gehechtheid" (moet zijn: "Bijlage")
   - FOUT: "Close" -> "Dichtbij" (moet zijn: "Sluiten")
   - FOUT: "Outstanding" -> "Uitstekend" (moet zijn: "Openstaand" in financiele context)
5. Wees consistent in terminologie. Gebruik altijd dezelfde vertaling voor dezelfde term.
6. Gebruik GEEN em-dashes in vertalingen.
7. CONTEXTANALYSE (KRITIEK): Bepaal EERST het domein van de brontekst voordat je vertaalt:
   - BOEKHOUDING: Account=Rekening, Balance=Saldo, Entry=Boeking, Outstanding=Openstaand, Ledger=Grootboek, Period=Periode, Opening=Beginsaldo, Close=Afsluiten
   - HR/PERSONEEL: Employee=Werknemer, Leave=Verlof, Attendance=Aanwezigheid, Shift=Dienst, Payroll=Salarisadministratie
   - VERKOOP: Invoice=Factuur, Quotation=Offerte, Customer=Klant, Delivery Note=Afleverbon, Outstanding=Openstaand
   - INKOOP: Supplier=Leverancier, Purchase Order=Inkooporder, Warehouse=Magazijn
   - IT/SYSTEEM: Account=Account, Log=Log, Server=Server, Cache=Cache, Session=Sessie, Close=Sluiten
   - PROJECT: Task=Taak, Timesheet=Urenregistratie, Activity=Activiteit, Progress=Voortgang
   Kijk naar de HELE zin om het domein te bepalen. "Account" in "Account {0} is frozen" is boekhouding (Rekening). "Account" in "A new account has been created for you" is IT (Account).
8. Gebruik GEEN em-dashes in vertalingen.

RESPONSE FORMAT:
Geef per vertaling een JSON object terug met:
- "source": de Engelse brontekst (ongewijzigd)
- "action": "approve" (vertaling is goed), "correct" (betere vertaling), of "keep_english" (niet vertalen)
- "translation": de (eventueel gecorrigeerde) Nederlandse vertaling
- "reason": korte uitleg (max 10 woorden) waarom je deze keuze maakt

Geef je antwoord als een JSON array. Geen andere tekst."""


def load_all():
    """Laad alle vertalingen uit CSV."""
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def save_all(rows):
    """Sla alle vertalingen op naar CSV."""
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def load_progress():
    """Laad voortgang van vorige sessie."""
    if PROGRESS_PATH.exists():
        with open(PROGRESS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"processed_count": 0, "batch_number": 0}


def save_progress(data):
    """Sla voortgang op."""
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


def update_live_dashboard(data):
    """Schrijf live status voor het HTML dashboard."""
    with open(LIVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def git_commit_and_push(batch_num, approved, corrected, kept):
    """Commit en push na elke batch naar GitHub."""
    import subprocess
    repo_dir = Path(__file__).parent

    try:
        # Stage translations.csv
        subprocess.run(
            ["git", "add", "translations.csv"],
            cwd=repo_dir, capture_output=True, timeout=10,
        )

        # Commit
        total = approved + corrected + kept
        msg = (
            f"chore: auto-review batch {batch_num} "
            f"({total} vertalingen: {approved} OK, {corrected} gecorrigeerd, {kept} Engels)\n\n"
            f"Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>"
        )
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=repo_dir, capture_output=True, timeout=10,
        )

        # Push
        result = subprocess.run(
            ["git", "push"],
            cwd=repo_dir, capture_output=True, timeout=30,
        )
        if result.returncode == 0:
            print(f"    Git: commit + push OK")
        else:
            print(f"    Git: push failed ({result.stderr.decode()[:100]})")

    except Exception as e:
        print(f"    Git: fout ({e})")


def show_stats(rows):
    """Toon voortgangsstatistieken."""
    reviewed = sum(1 for r in rows if r["status"] == "reviewed")
    unreviewed = sum(1 for r in rows if r["status"] == "unreviewed")
    deleted = sum(1 for r in rows if r.get("status") == "deleted")
    total = len(rows)
    pct = (reviewed / total * 100) if total else 0

    print(f"\n{'=' * 60}")
    print(f"ERPNext NL Vertalingen - Auto Review Status")
    print(f"{'=' * 60}")
    print(f"  Totaal:       {total}")
    print(f"  Reviewed:     {reviewed} ({pct:.1f}%)")
    print(f"  Unreviewed:   {unreviewed}")
    print(f"  Verwijderd:   {deleted}")
    print(f"{'=' * 60}\n")


def build_batch_prompt(batch):
    """Bouw de prompt voor een batch vertalingen."""
    items = []
    for row in batch:
        items.append({
            "source": row["source"],
            "translation": row["translation"],
        })
    return json.dumps(items, ensure_ascii=False, indent=2)


def process_batch(client, batch, batch_num, total_batches):
    """Verwerk een batch vertalingen via Claude API."""
    prompt = build_batch_prompt(batch)

    print(f"\n  Batch {batch_num}/{total_batches} ({len(batch)} vertalingen)...")

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Beoordeel deze {len(batch)} vertalingen:\n\n{prompt}",
                }
            ],
        )

        response_text = message.content[0].text.strip()

        # Parse JSON response (handle markdown code blocks)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        results = json.loads(response_text)
        return results

    except json.JSONDecodeError as e:
        print(f"    JSON parse error: {e}")
        print(f"    Response: {response_text[:200]}...")
        return None
    except Exception as e:
        print(f"    API error: {e}")
        return None


def apply_results(rows, batch_indices, results):
    """Pas AI resultaten toe op de CSV data."""
    if not results:
        return 0, 0, 0

    # Maak lookup van source -> result
    result_map = {}
    for r in results:
        if isinstance(r, dict) and "source" in r:
            result_map[r["source"]] = r

    approved = 0
    corrected = 0
    kept_english = 0

    for idx in batch_indices:
        row = rows[idx]
        source = row["source"]
        if source in result_map:
            result = result_map[source]
            action = result.get("action", "approve")

            if action == "approve":
                row["status"] = "reviewed"
                approved += 1
            elif action == "correct":
                row["translation"] = result.get("translation", row["translation"])
                row["status"] = "reviewed"
                corrected += 1
            elif action == "keep_english":
                row["translation"] = result.get("translation", source)
                row["status"] = "reviewed"
                kept_english += 1
            else:
                row["status"] = "reviewed"
                approved += 1

    return approved, corrected, kept_english


def main():
    flags = set(sys.argv[1:])
    dry_run = "--dry-run" in flags
    resume = "--resume" in flags

    # Parse batch size
    batch_size = 50
    for i, arg in enumerate(sys.argv):
        if arg == "--batch-size" and i + 1 < len(sys.argv):
            batch_size = int(sys.argv[i + 1])

    # Parse origin filter
    origin_filter = None
    for i, arg in enumerate(sys.argv):
        if arg == "--origin" and i + 1 < len(sys.argv):
            origin_filter = sys.argv[i + 1]

    rows = load_all()

    if "--stats" in flags:
        show_stats(rows)
        return

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Fout: ANTHROPIC_API_KEY environment variable niet gezet.")
        print("Gebruik: export ANTHROPIC_API_KEY=sk-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Selecteer unreviewed vertalingen
    unreviewed_indices = []
    for i, row in enumerate(rows):
        if row["status"] == "unreviewed":
            if origin_filter is None or row.get("origin") == origin_filter:
                unreviewed_indices.append(i)

    if not unreviewed_indices:
        print("Geen unreviewed vertalingen gevonden!")
        return

    # Resume support
    start_offset = 0
    if resume:
        progress = load_progress()
        start_offset = progress.get("processed_count", 0)
        if start_offset > 0:
            print(f"Hervat vanaf vertaling {start_offset}")
            unreviewed_indices = unreviewed_indices[start_offset:]

    total = len(unreviewed_indices)
    total_batches = (total + batch_size - 1) // batch_size

    filter_label = f" (origin={origin_filter})" if origin_filter else ""
    print(f"\n{'=' * 60}")
    print(f"ERPNext NL Vertalingen - Auto Review{filter_label}")
    print(f"{'=' * 60}")
    print(f"  Te verwerken:  {total}")
    print(f"  Batch grootte: {batch_size}")
    print(f"  Batches:       {total_batches}")
    if dry_run:
        print(f"  MODUS:         Dry run")
    print(f"{'=' * 60}")

    total_approved = 0
    total_corrected = 0
    total_kept = 0
    total_failed = 0

    for batch_num in range(1, total_batches + 1):
        start = (batch_num - 1) * batch_size
        end = min(start + batch_size, total)
        batch_indices = unreviewed_indices[start:end]
        batch = [rows[i] for i in batch_indices]

        # Pre-batch: update live dashboard met huidige batch
        live_data = {
            "total_processed": total_approved + total_corrected + total_kept,
            "total_approved": total_approved,
            "total_corrected": total_corrected,
            "total_kept_english": total_kept,
            "total_unreviewed": total,
            "total_batches": total_batches,
            "current_batch": {
                "number": batch_num,
                "size": len(batch),
                "status": "processing",
                "items": [{"source": b["source"], "translation": b["translation"]} for b in batch],
            },
        }
        update_live_dashboard(live_data)

        # Stap 1: AI review
        results = process_batch(client, batch, batch_num, total_batches)

        if results:
            # Stap 2: Apply resultaten
            approved, corrected, kept = apply_results(
                rows, batch_indices, results
            )
            total_approved += approved
            total_corrected += corrected
            total_kept += kept

            print(f"    OK: {approved} goedgekeurd, {corrected} gecorrigeerd, {kept} Engels gehouden")

            # Stap 3: Update live dashboard met resultaten
            result_map = {}
            for r in results:
                if isinstance(r, dict) and "source" in r:
                    result_map[r["source"]] = r

            live_items = []
            for b in batch:
                r = result_map.get(b["source"], {})
                live_items.append({
                    "source": b["source"],
                    "translation": r.get("translation", b["translation"]),
                    "original_translation": b["translation"],
                    "action": r.get("action", "approve"),
                    "reason": r.get("reason", ""),
                })

            live_data["total_processed"] = total_approved + total_corrected + total_kept
            live_data["total_approved"] = total_approved
            live_data["total_corrected"] = total_corrected
            live_data["total_kept_english"] = total_kept
            live_data["current_batch"]["status"] = "done"
            live_data["current_batch"]["items"] = live_items
            update_live_dashboard(live_data)

            if not dry_run:
                # Stap 4: Opslaan CSV
                save_all(rows)
                save_progress({
                    "processed_count": start_offset + end,
                    "batch_number": batch_num,
                })
                print(f"    CSV opgeslagen ({start_offset + end} vertalingen verwerkt)")

                # Stap 5: Git commit + push
                git_commit_and_push(batch_num, approved, corrected, kept)

        else:
            total_failed += len(batch)
            print(f"    FOUT: batch {batch_num} mislukt")

        # Rate limiting
        if batch_num < total_batches:
            time.sleep(1)

    # Eindresultaat opslaan
    if not dry_run:
        save_all(rows)
        if total_failed == 0 and PROGRESS_PATH.exists():
            PROGRESS_PATH.unlink()

    print(f"\n{'=' * 60}")
    print(f"RESULTAAT")
    print(f"{'=' * 60}")
    print(f"  Goedgekeurd:    {total_approved}")
    print(f"  Gecorrigeerd:   {total_corrected}")
    print(f"  Engels gehouden: {total_kept}")
    print(f"  Mislukt:        {total_failed}")
    print(f"  Totaal:         {total_approved + total_corrected + total_kept + total_failed}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
