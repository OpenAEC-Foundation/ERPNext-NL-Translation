![Vertalingen](https://img.shields.io/badge/vertalingen-16.797-brightgreen)
![Reviewed](https://img.shields.io/badge/reviewed-100%25-success)
![Quality Scored](https://img.shields.io/badge/quality%20scored-99.9%25-blue)
![Quality Improved](https://img.shields.io/badge/quality%20improved-4.891-blue)
![Apps](https://img.shields.io/badge/apps-7-blue)
![Frappe](https://img.shields.io/badge/Frappe-v15%20%7C%20v16-blue)
![Licentie](https://img.shields.io/badge/licentie-MIT-green)

# ERPNext NL Translation

Kwalitatieve Nederlandse vertalingen voor ERPNext, Frappe en 5 extra apps, geoptimaliseerd voor gebruik in het Nederlandse bedrijfsleven. Elke vertaling is beoordeeld door een AI-analyselaag die context, vakjargon en natuurlijk taalgebruik controleert. Daarnaast is elke vertaling gekwalificeerd met een kwaliteitsscore (0-1) en worden vertalingen met lage scores verbeterd via een alternatieve-vergelijkingspipeline.

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

Dit project biedt een complete set van 16.797 vertalingen voor 7 Frappe/ERPNext apps, beoordeeld op correctheid in de context waarin ze worden gebruikt.

## Status

| Metriek | Waarde |
|---------|--------|
| Totaal vertalingen | 16.797 |
| AI-reviewed | 16.797 (100%) |
| Kwaliteitsscore | 16.788 gescoord (99.9%) |
| Score >= 0.8 (OK) | 70.8% |
| Verbeterd via alternatieven | 4.891 (100%) |
| Close calls (handmatige review) | 138 |
| Correcties toegepast | ~5.500+ |
| Live op productie | 16.797 |
| Apps gedekt | 7 (Frappe, ERPNext, HRMS, CRM, Helpdesk, Insights, Banking) |

### Vertalingen per app

| App | Vertalingen | Status |
|-----|------------|--------|
| Frappe Framework | 3.917 | 100% reviewed |
| ERPNext | 7.747 | 100% reviewed |
| Frappe HR (HRMS) | 2.062 | 100% reviewed |
| Frappe CRM | 1.102 | 100% reviewed |
| Helpdesk | 785 | 100% reviewed |
| Insights | 449 | 100% reviewed |
| GoCardless Banking | 217 | 100% reviewed |

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

Vertalingen met een score onder 0.8 doorlopen een extra verbeteringsstap (Fase 4): per item worden 3 alternatieven gegenereerd (dicht bij bron, idiomatisch, compact), elk gescoord op dezelfde 5 factoren. De best scorende vertaling wordt automatisch toegepast. Items waarbij de top-2 alternatieven minder dan 1% verschil scoren worden apart bewaard voor handmatige beoordeling.

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
- Meerdere architectenbureaus in Nederland (16.797 vertalingen, 7 apps)

## Herkomst

Basis: Frappe v16 + ERPNext v16 .csv bestanden + .po bestanden van HRMS, CRM, Helpdesk, Insights en GoCardless Banking. Identity-mappings verwijderd. AI-review uitgevoerd op 2026-04-08 met contextbewuste domeinanalyse in 112 batches (65 basis + 47 custom apps via parallelle agent teams).

## Bijdragen

Vertalingen die beter kunnen? Open een issue of maak een pull request. De `review.py` tool maakt het makkelijk om specifieke termen te zoeken en te verbeteren.

## Licentie

MIT
