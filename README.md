# Pike Creek Inventory Health Analyzer

A Python + SQLite tool built to analyze and quantify hidden inventory issues in independent hardware retail.

**Demonstration only** — uses realistic simulated data based on observed patterns (no real store data included).

## Key Issues Highlighted
- Overstock from discontinued SKU → replacement substitution
- Negative Quantity on Hand (including extreme examples like -11,033 in lumber)
- Dead stock tying up cash with no sales in years
- Financial impact: distorted COGS, inflated profits, trapped capital

## Features
- Local SQLite database with indexed tables for performance
- Realistic sample data (~50 items across categories)
- Console report with dollar values and recommendations

## How to Run
```bash
pip install pandas numpy
python create_inventory_db.py   # Creates inventory.db
python inventory_health_report.py  # Generates the report
