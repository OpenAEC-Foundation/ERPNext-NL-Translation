# ERPNext NL Translation

Nederlandse vertalingen voor ERPNext / Frappe v15+.

## Status

| Metriek | Aantal |
|---------|--------|
| Totaal vertalingen | 12.182 |
| Reviewed | 9.815 (80,6%) |
| Unreviewed | 2.367 |
| Gedeployed naar KG | 9.815 |

*Laatst bijgewerkt: 2026-04-08*

De ingebouwde Frappe/ERPNext community vertalingen zijn van wisselende kwaliteit
(bijv. "Attachment" -> "Gehechtheid", "Close" -> "Dichtbij"). Alle vertalingen
staan in een enkele CSV met review-status, zodat je er gestructureerd doorheen
kunt werken. Een AI-analyselaag controleert context, vakjargon en natuurlijk
Nederlands taalgebruik.

## Pipeline

```
translations.csv  -->  auto_review.py (AI analyse)  -->  upload.py (deployen)
     |                        |                              |
     |                        v                              v
     +-- source              Claude API                Frappe instance
     +-- translation         (context check,           (alleen reviewed)
     +-- status              vakjargon,
     +-- origin              natuurlijk NL)
                                  |
                             live_dashboard.html
                             (real-time voortgang)
```

De AI-analyselaag controleert per vertaling:
1. Is de vertaling correct en natuurlijk Nederlands?
2. Moet het woord in het Engels blijven (gangbaar vakjargon)?
3. Is er een betere vertaling gezien de context (boekhouding, HR, IT)?

### 1. Vertalingen reviewen

```bash
# Voortgang bekijken
python review.py --stats

# Interactief reviewen
python review.py

# Zoek specifieke termen
python review.py --search "invoice"

# Start bij regel 100
python review.py --from 100
```

Per vertaling kun je:
- **Enter**: goedkeuren (markeer als reviewed)
- **n**: nieuwe/betere vertaling invoeren
- **d**: verwijderen (slechte vertaling)
- **s**: overslaan
- **q**: stoppen (wijzigingen worden opgeslagen)

### 2. Uploaden naar Frappe

```bash
# Alleen reviewed vertalingen (standaard)
python upload.py https://jouw-site.example.com API_KEY:API_SECRET

# Alles uploaden (inclusief unreviewed)
python upload.py https://jouw-site.example.com API_KEY:API_SECRET --all

# Dry run (toon wat er zou gebeuren)
python upload.py https://jouw-site.example.com API_KEY:API_SECRET --dry-run

# Full sync (verwijder ook vertalingen die niet in CSV staan)
python upload.py https://jouw-site.example.com API_KEY:API_SECRET --sync
```

## Vertaalprincipes

### Niet vertalen (bewust Engels)

Engelse termen die in het Nederlandse bedrijfsleven gangbaar zijn:

Dashboard, Template, Export, Import, Manager, Email, Server, Widget,
Login, Logout, PDF, API, CRM, POS, BOM, UOM, Budget, Workflow,
Routing, Prospect, Contract, Scorecard, HR

### Wel vertalen

Alle termen waarvoor een duidelijk en gangbaar Nederlands equivalent bestaat.

### Kwaliteitsregels

- Consistente terminologie (altijd "sjabloon" voor Template in samenstellingen)
- Geen identity-vertalingen (source == translation)
- Vakjargon dat in het Engels gangbaar is blijft Engels
- Bij twijfel: zou een Nederlandse monumentenwachter dit woord gebruiken?

## Vereisten

```bash
pip install requests
```

## Deployment

Reviewed vertalingen worden gedeployed naar ERPNext instances via de
`Translation` doctype (Custom Translations). Dit overschrijft de ingebouwde
.po vertalingen waar nodig.

Actieve deployments:
- **Kort Geytenbeek** (kortgeytenbeek-erp.prilk.cloud): 9.815 vertalingen

## Herkomst

Basis: Frappe v15 nl.csv (4.798) + ERPNext v15 nl.csv (8.746) + 406 handmatig
beoordeelde vertalingen. Identity-mappings (983) verwijderd. AI-review gestart
op 2026-04-08 met contextbewuste analyse.

## Licentie

MIT
