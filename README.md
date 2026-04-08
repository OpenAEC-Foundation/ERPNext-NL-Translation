![Vertalingen](https://img.shields.io/badge/vertalingen-12.182-brightgreen)
![Reviewed](https://img.shields.io/badge/reviewed-100%25-success)
![Frappe](https://img.shields.io/badge/Frappe-v15%20%7C%20v16-blue)
![Licentie](https://img.shields.io/badge/licentie-MIT-green)

# ERPNext NL Translation

Kwalitatieve Nederlandse vertalingen voor ERPNext en Frappe, geoptimaliseerd voor gebruik in het Nederlandse bedrijfsleven. Elke vertaling is beoordeeld door een AI-analyselaag die context, vakjargon en natuurlijk taalgebruik controleert.

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

Dit project biedt een complete set van 12.182 vertalingen die zijn beoordeeld op correctheid in de context waarin ze worden gebruikt.

## Status

| Metriek | Waarde |
|---------|--------|
| Totaal vertalingen | 12.182 |
| AI-reviewed | 12.182 (100%) |
| Correcties toegepast | ~1.500+ |
| Live op productie | 12.182 |

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

De AI-analyselaag bepaalt per vertaling het domein (boekhouding, HR, IT, verkoop, inkoop, project) en past de vertaling daarop aan. Bijvoorbeeld: "Account" wordt "Rekening" in boekhoudcontext maar "Account" in IT-context.

## Vertaalprincipes

### Bewust Engels gehouden

Termen die in het Nederlandse bedrijfsleven standaard in het Engels worden gebruikt:

> Dashboard, Template, Export, Import, Manager, Email, Server, Widget, Login, API, CRM, POS, BOM, UOM, Budget, Workflow, Lead, Pipeline, Scorecard, HR, Batch, Stock

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

### Kwaliteitsregels

- Samengestelde woorden als 1 woord (voorraadmutatie, afschrijvingsboeking, verkoopfactuur)
- Geen onnodige hoofdletters in Nederlandse labels
- Consistente terminologie door het hele systeem
- Naamreeksen en AWS-regiocodes niet vertalen
- "u" als aanspreking in foutmeldingen (zakelijke software)

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

### Live dashboard

Open `live_dashboard.html` in een browser om de vertalingen in real-time te volgen tijdens het reviewproces.

## Vereisten

```bash
pip install requests anthropic
```

## Deployment

Reviewed vertalingen worden gedeployed naar ERPNext instances via het `Translation` doctype. Dit overschrijft de ingebouwde .po vertalingen waar nodig.

**Actieve deployments:**
- Kort Geytenbeek Architecten (12.182 vertalingen)

## Herkomst

Basis: Frappe v15 `nl.csv` (4.798 vertalingen) + ERPNext v15 `nl.csv` (8.746 vertalingen). Identity-mappings (983 stuks waar bron gelijk is aan vertaling) verwijderd. AI-review uitgevoerd op 2026-04-08 met contextbewuste domeinanalyse in 65 batches.

## Bijdragen

Vertalingen die beter kunnen? Open een issue of maak een pull request. De `review.py` tool maakt het makkelijk om specifieke termen te zoeken en te verbeteren.

## Licentie

MIT
