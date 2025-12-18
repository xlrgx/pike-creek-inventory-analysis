# Pike Creek Inventory Health Analyzer

A Python + SQLite tool I built to identify and quantify hidden inventory problems in independent hardware retail.

## Problems It Uncovers
- Overstock from discontinued SKU → replacement substitution loop
- Massive negative Quantity on Hand (e.g., -11,033 in lumber)
- Dead stock tying up thousands in cash with no sales in years
- Distorted COGS and inflated reported profits

## Why I Built This
This tool documents the financial impact and to provide data-driven recommendations.

## Features
- Local SQLite database with realistic sample data
- Performance indexes for scalability
- Clear console report with dollar impacts
- Easy to extend (CSV import, Excel export, charts coming soon)

## How to Run
```bash
pip install pandas numpy
python create_inventory_db.py
python inventory_analyzer.py
