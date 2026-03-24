# ERPNext NL Translation

Nederlandse vertalingen voor ERPNext / Frappe v15+.

## Inhoud

- **translations.csv** - 470 beoordeelde vertalingen (source,translation)
- **upload.py** - Script om vertalingen te uploaden naar een Frappe instance

## Vertaalprincipes

### Niet vertaald (bewust Engels gehouden)

Engelse termen die in het Nederlandse bedrijfsleven gangbaar zijn:

Dashboard, Template, Export, Import, Manager, Email, Server, Widget, Login, Logout, PDF, API, CRM, POS, BOM, UOM, Budget, Workflow, Routing, Prospect, Contract, Scorecard, HR

### Wel vertaald

Alle termen waarvoor een duidelijk en gangbaar Nederlands equivalent bestaat:

| Engels | Nederlands |
|--------|-----------|
| Customer | Klant |
| Invoice | Factuur |
| Employee | Medewerker |
| Settings | Instellingen |
| Warehouse | Magazijn |
| Supplier | Leverancier |
| Payment | Betaling |
| ... | ... |

### Kwaliteitsregels

- Consistente terminologie (altijd "sjabloon" voor Template in samenstellingen)
- Geen identity-vertalingen (Contract -> Contract) opgenomen
- Geen vertalingen van al-Nederlandse bronwoorden
- Vakjargon dat in het Engels gangbaar is blijft Engels

## Gebruik

### Vereisten

```bash
pip install requests
```

### Vertalingen uploaden

```bash
python upload.py https://jouw-site.example.com API_KEY:API_SECRET
```

Het script:
1. Laadt alle vertalingen uit `translations.csv`
2. Haalt bestaande vertalingen op van de server
3. Uploadt alleen nieuwe vertalingen (bestaande worden overgeslagen)
4. Toont afwijkingen tussen CSV en server

### Handmatig via Frappe

Je kunt ook handmatig vertalingen importeren:

1. Ga naar **Setup > Translation** in je Frappe instance
2. Gebruik **Import Data** en upload `translations.csv`
3. Zet de taal op `nl` (Nederlands)

## Bijdragen

Vertalingen toevoegen of verbeteren:

1. Bewerk `translations.csv`
2. Volg de vertaalprincipes hierboven
3. Test door te uploaden naar een test-instance
4. Open een Pull Request

## Statistieken

| Metriek | Aantal |
|---------|--------|
| Totaal vertalingen | 470 |
| Boekhouding | 57 |
| Verkoop/Inkoop | 12 |
| Voorraad | 28 |
| Productie | 8 |
| HR/Payroll | 47 |
| CRM | 8 |
| Projecten | 5 |
| Kwaliteit | 4 |
| Activa | 11 |
| Uitbesteding | 4 |
| Setup | 13 |
| Core/Systeem | 21 |
| Website | 14 |
| UI-strings | 128 |
| Financiele labels | 78 |

## Herkomst

Geconsolideerd vanuit het [erpnext-nextcloud-NL-websites](https://github.com/FreekHeijting/erpnext-nextcloud-NL-websites) project (481 vertalingen), beoordeeld en opgeschoond tot 470 kwalitatieve vertalingen.

## Licentie

MIT
