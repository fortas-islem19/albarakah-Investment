# Website Quote — MOSTALIFE · Résidence El Charika

| File | For | Purpose |
|---|---|---|
| [`MOSTALIFE_Website_Quote.html`](MOSTALIFE_Website_Quote.html) | **Client** | Full quote in **French, Arabic and English** (switch in the toolbar), prices in **USD and DZD**. Toolbar: language, exchange rate (all DA amounts update), “Edit text”, “Print / PDF”. |
| `MOSTALIFE_Quote_FR.pdf` · `_AR.pdf` · `_EN.pdf` | **Client** | Ready-made PDF of each language (11 A4 pages, rate 1 USD = 135 DZD). |
| [`SALES_PLAYBOOK.md`](SALES_PLAYBOOK.md) | **You only** | How to pitch, which plan to push, discovery questions, objection handling, follow-up messages, contract checklist. |
| [`tools/build_quote.py`](tools/build_quote.py) | Developer | Regenerates the HTML from one data file (prices, texts in 3 languages, default rate). |

## Plans (excl. taxes — 1 USD = 135 DZD)

| Plan | USD | DZD | Delivery |
|---|---|---|---|
| 1. Essential — premium landing page | **$600** | **81,000 DA** | 1–2 weeks |
| 2. Starter — showcase & reservation requests | **$1,200** | **162,000 DA** | 3 weeks |
| 3. Business — interactive sales platform ⭐ | **$2,500** | **337,500 DA** | 5–6 weeks |
| 4. Professional — online reservation & buyer portal | **$5,000** | **675,000 DA** | 8–10 weeks |
| 5. Premium — multi-project platform + mobile app | **$10,000** | **1,350,000 DA** | 3–4 months |

Each plan includes everything in the previous one. Every feature's individual price (USD + DZD) is listed in the quote.

Maintenance: $20 / $45 / $90 per month (≈ 2,700 / 6,100 / 12,200 DA).

## Regenerate after changing prices or texts

```bash
python3 tools/build_quote.py tools/tower.jpg MOSTALIFE_Website_Quote.html
```
