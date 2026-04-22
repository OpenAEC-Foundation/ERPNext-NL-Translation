![Vertalingen](https://img.shields.io/badge/vertalingen-24.507-brightgreen)
![Reviewed](https://img.shields.io/badge/reviewed-100%25-success)
![Dekking v16](https://img.shields.io/badge/dekking%20Frappe%2FERPNext%20v16-~99%25-success)
![Quality Scored](https://img.shields.io/badge/quality%20scored-100%25-blue)
![Quality Improved](https://img.shields.io/badge/quality%20improved-4.891-blue)
![Apps](https://img.shields.io/badge/apps-7-blue)
![Frappe](https://img.shields.io/badge/Frappe-v15%20%7C%20v16-blue)
![Licentie](https://img.shields.io/badge/licentie-MIT-green)

# ERPNext NL Translation

Kwalitatieve Nederlandse vertalingen voor ERPNext, Frappe en 5 extra apps, geoptimaliseerd voor gebruik in het Nederlandse bedrijfsleven. Elke vertaling is beoordeeld door een AI-analyselaag die context, vakjargon en natuurlijk taalgebruik controleert, en gekwalificeerd met een kwaliteitsscore (0-1). Vertalingen met lage scores zijn verbeterd via een alternatieve-vergelijkingspipeline. Alle source-strings uit de Frappe/ERPNext v16 `.pot` bestanden zijn gedekt, inclusief case/whitespace/punctuatie-varianten die de Frappe-code letterlijk aanroept.

## Waarom dit project?

De ingebouwde community-vertalingen van ERPNext bevatten veel fouten: letterlijke machinevertalingen die in de praktijk niet werken. Voorbeelden:

| Engels | Community-vertaling | Onze vertaling |
|--------|-------------------|----------------|
| Attachment | Gehechtheid | Bijlage |
| Close | Dichtbij | Sluiten |
| Outstanding | Uitstekend | Openstaand |
| Float | Zweven | Decimaal |
| Console | Troosten | Console |
| Collapse | Ineenstorting | Inklappen |
| Stock Entry | Aandeleninvoer | Voorraadmutatie |

Daarnaast laat de community-vertaalinfrastructuur veel strings helemaal onvertaald. Dit project dekt alle 21.215 unieke source-strings uit Frappe/ERPNext v16 plus de aangrenzende apps, en lost ook een veel voorkomende blocker op: source-strings die in de Frappe-code met een andere casing of whitespace worden aangeroepen dan in het `.pot` bronbestand staat.

## Status

| Metriek | Waarde |
|---------|--------|
| Totaal vertalingen | **24.507** |
| AI-reviewed | 24.507 (100%) |
| Dekking Frappe/ERPNext v16 source | ~99% |
| Kwaliteitsscore | 100% gescoord |
| Verbeterd via alternatieven (fase 4) | 4.891 |
| Close calls (handmatige review) | 138 |
| Code-variant fixes (case/whitespace/punct) | 378 |
| Gap-pipeline (niet eerder vertaald) | 7.304 |
| KG-specifieke custom fields | 28 |
| Live op productie | 24.507 |
| Apps gedekt | 7 (Frappe, ERPNext, HRMS, CRM, Helpdesk, Insights, Banking) |

### Vertalingen per herkomst

| Herkomst (`origin` kolom) | Aantal | Beschrijving |
|---------------------------|--------|--------------|
| `erpnext` | 7.747 | ERPNext core reviewed |
| `erpnext_gap` | 4.415 | ERPNext strings die nog geen vertaling hadden |
| `frappe` | 3.917 | Frappe framework reviewed |
| `frappe_gap` | 2.636 | Frappe strings die nog geen vertaling hadden |
| `hrms` | 2.062 | Frappe HR reviewed |
| `crm` | 1.102 | Frappe CRM reviewed |
| `helpdesk` | 785 | Helpdesk reviewed |
| `insights` | 449 | Insights reviewed |
| `both` | 345 | Strings gedeeld door Frappe + ERPNext |
| `banking` | 217 | GoCardless Banking reviewed |
| `custom` | 173 | Custom strings |
| `{app}_code_variant` | 378 | Case/whitespace/punct-fixes over alle apps |
| `{app}_gap` | 253 (rest) | Gap-entries voor HRMS/CRM/Helpdesk/Insights/Banking |
| `kg_custom_field` | 28 | KG-specifieke labels |

## Aanpak

Elke vertaling doorloopt een gestructureerd reviewproces:

```
translations.csv  -->  auto_review.py (AI analyse)  -->  upload.py (deployen)
     |                        |                              |
     v                        v                              v
  brontekst             contextanalyse                 Frappe instance
  vertaling             domeinherkenning               (Translation doctype)
  status                vakjargoncontrole
  herkomst              natuurlijk NL-check
```

De AI-analyselaag bepaalt per vertaling het domein (boekhouding, HR, IT, verkoop, inkoop, project, stock, assets, manufacturing, communicatie, rapportage) en past de vertaling daarop aan. Bijvoorbeeld: "Account" wordt "Rekening" in boekhoudcontext maar "Account" in IT-context.

### Fasen

| Fase | Scope | Resultaat |
|------|-------|-----------|
| Fase 1-3 | Baseline AI-review per app (65 basis + 47 custom batches) | 16.797 reviewed vertalingen |
| Fase 4 | Alternatieven-pipeline voor scores < 0.8 | 4.891 verbeterd |
| **Fase 5 (2026-04)** | Case/whitespace/punct code-variants + gap-pipeline tegen `.pot` + KG custom fields | **+7.710 records** |

Fase 5 is uitgevoerd door 15 parallelle AI-agents, elk met een batch van 250-530 source-strings, met domeinclassificatie en kwaliteitsscore per record. Corpus-brede correcties zijn daarna centraal toegepast (Manager onvertaald, Stock Ledger consistent, Clearance date → Afhandelingsdatum, voorbeeld-emails ongewijzigd, samenstellingen met koppelteken).

## Vertaalprincipes

### Bewust Engels gehouden

Termen die in het Nederlandse bedrijfsleven standaard in het Engels worden gebruikt:

> Dashboard, Template, Export, Import, Manager, Email, Server, Widget, Login, API, CRM, POS, BOM, UOM, Budget, Workflow, Lead, Pipeline, Scorecard, HR, Batch, Stock, ToDo, Layout, Deal, Prospect

### Contextbewuste vertaling

Dezelfde Engelse term kan in verschillende contexten anders vertaald worden:

| Term | Boekhoudcontext | IT-context | HR-context |
|------|----------------|------------|------------|
| Account | Rekening | Account | - |
| Balance | Saldo | - | - |
| Entry | Boeking | Invoer | - |
| Close | Afsluiten | Sluiten | - |
| Leave | - | - | Verlof |
| Draft | Concept | Concept | - |
| Outstanding | Openstaand | - | - |

### Boekhoudhiërarchie

Nederlandse boekhoudterminologie volgt een vaste hiërarchie die we consequent toepassen:

- **Rekeningschema** (`Chart of Accounts`) — de boomstructuur van alle rekeningen
- **Hoofdrekening** (`Root Account`, `Account Head`) — top-level rekening
- **Rekening** (`Account`) — individuele rekening
- **Grootboek** (`Ledger`) — registratie-laag (`Voorraadgrootboek`, `Betalingsgrootboek`, `Verlofgrootboek`)
- **Boekstuk** (`Voucher`) / **Boeking** (`Journal Entry`) — individuele registratie

### Kwaliteitsregels

- Samengestelde woorden als 1 woord (voorraadmutatie, afschrijvingsboeking, verkoopfactuur)
- Geen onnodige hoofdletters in Nederlandse labels
- Consistente terminologie door het hele systeem
- Naamreeksen, codes (IBAN, SEPA, BTW) en AWS-regiocodes niet vertalen
- "u" als aanspreking in foutmeldingen (zakelijke software)
- Voorbeeld-emails en URL's ongewijzigd (`john@doe.com`, `example.com`)
- Placeholders exact behouden (`{0}`, `{{var}}`, `%s`, HTML-tags)

## Gebruik

### Interactief reviewen

```bash
python review.py --stats          # Bekijk voortgang
python review.py                  # Start interactieve review
python review.py --search "factuur"  # Zoek specifieke termen
```

### Automatisch reviewen (AI)

```bash
export ANTHROPIC_API_KEY=sk-...
python auto_review.py             # Verwerk alle unreviewed
python auto_review.py --batch-size 100  # Grotere batches
python auto_review.py --dry-run   # Toon resultaten zonder op te slaan
```

### Deployen naar ERPNext

```bash
python upload.py https://jouw-site.example.com API_KEY:API_SECRET
python upload.py https://jouw-site.example.com API_KEY:API_SECRET --dry-run
python upload.py https://jouw-site.example.com API_KEY:API_SECRET --sync
```

Na bulk-upload kan een PUT-request op één bestaand `Translation`-record nodig zijn om de Redis translation cache te forceren te invalideren:

```bash
curl -X PUT -H "Authorization: token KEY:SECRET" \
  -H "Content-Type: application/json" \
  -d '{"translated_text":"<originele waarde>"}' \
  https://jouw-site.example.com/api/resource/Translation/<naam>
```

### Live dashboard

Open `live_dashboard.html` in een browser om de vertalingen in real-time te volgen tijdens het reviewproces.

## Vereisten

```bash
pip install requests anthropic
```

## Deployment

Reviewed vertalingen worden gedeployed naar ERPNext instances via het `Translation` doctype. Deze records hebben prioriteit 1 in de Frappe translation-precedence en overschrijven altijd de ingebouwde `.po` / `.mo` vertalingen van welke app dan ook.

**Actieve deployments:**
- Meerdere architectenbureaus in Nederland (24.507 vertalingen, 7 apps)

## Herkomst

Basis: Frappe v16 + ERPNext v16 `.csv` bestanden + `.po` bestanden van HRMS, CRM, Helpdesk, Insights en GoCardless Banking. Identity-mappings verwijderd. AI-review uitgevoerd in meerdere fasen:
- Fase 1-3 (2026-04-08): contextbewuste domeinanalyse in 112 batches (65 basis + 47 custom apps via parallelle agent teams)
- Fase 4 (2026-04-08): alternatieven-pipeline voor scores onder 0.8
- Fase 5 (2026-04-22): `.pot`-vergelijking tegen v16 source, 15 parallelle agent teams voor gap-coverage, corpus-brede consistentie-correcties, case/whitespace/punct variant-fixes, KG-specifieke custom fields

## Bijdragen

Vertalingen die beter kunnen? Open een issue of maak een pull request. De `review.py` tool maakt het makkelijk om specifieke termen te zoeken en te verbeteren.

## Licentie

MIT
