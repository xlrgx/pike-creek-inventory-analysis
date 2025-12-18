# Hardware Store Inventory Health Analyzer

A Python-based tool I built to identify and quantify common inventory issues in independent hardware retail:

- Overstock from discontinued → replacement SKU substitution
- Negative Quantity on Hand (QOH)
- Dead/slow-moving stock with no write-offs
- Hidden financial impact (distorted COGS, tied-up cash)

## Why This Tool Exists
In my role at a mid-sized hardware chain, I've observed systemic issues that artificially inflate reported profits while hurting cash flow and competitiveness. Management has not prioritized fixes, so I built this analyzer to:
- Document problems with data
- Propose actionable solutions
- Improve accuracy and operations

## Features
- Connects to MySQL database (or uses sample data)
- Reports:
  - Replacement overstock
  - Negative QOH and estimated shrink
  - Dead stock (no sales in 18+ months)
  - Total financial exposure
- Easy to customize for any retail POS system

## How to Run
```bash
pip install pandas numpy mysql-connector-python
python inventory_analyzer.py