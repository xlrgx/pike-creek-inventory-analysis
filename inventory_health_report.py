"""
Pike Creek Community Hardware - Inventory Health Analyzer
Author: Joseph Hopkins
Date: December 2025

This tool analyzes hardware store inventory to highlight real operational issues:
- Overstock from discontinued → replacement SKU substitution
- Negative Quantity on Hand (QOH)
- Dead stock (no sales in 18+ months)
- Hidden financial impact on COGS and cash flow

Uses local SQLite database (inventory.db) - no server needed.
"""

import sqlite3
import pandas as pd
from datetime import datetime
import numpy as np


# ==================== DATABASE CONNECTION ====================
def connect_and_fetch(db_name='inventory.db'):
    """Connect to local SQLite database and return DataFrame"""
    try:
        conn = sqlite3.connect(db_name)
        query = """
                SELECT item_number      AS sku, \
                       description, \
                       quantity_on_hand AS qoh, \
                       cost, \
                       retail_price     AS retail, \
                       last_sold_date, \
                       last_received_date, \
                       status
                FROM items \
                """
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Convert date columns
        df['last_sold_date'] = pd.to_datetime(df['last_sold_date'], errors='coerce')
        df['last_received_date'] = pd.to_datetime(df['last_received_date'], errors='coerce')

        print(f"Successfully loaded {len(df):,} items from {db_name}\n")
        return df
    except Exception as e:
        print(f"Error loading database: {e}")
        print("Falling back to built-in sample data.\n")
        return generate_sample_data()


def generate_sample_data():
    """Large realistic fallback sample data when DB is not available"""
    import random

    data = [
        # Discontinued → Replacement pairs (over-ordering issue)
        ('OLD-1001', 'Old Deck Screw 2-1/2" (Discontinued)', -120, 0.15, 0.39, '2023-08-20', '2024-01-15',
         'Discontinued'),
        ('NEW-1001', 'Spax Deck Screw 2-1/2" (Replacement)', 1200, 0.22, 0.49, '2025-12-10', '2025-12-01', 'Active'),
        ('OLD-2002', 'Old Structural Bolt 1/2x6 (Discontinued)', -80, 2.80, 5.99, '2023-05-10', '2023-11-20',
         'Discontinued'),
        ('NEW-2002', 'Simpson SDWS Framing Screw (Replacement)', 850, 3.50, 7.49, '2025-12-05', '2025-12-03', 'Active'),
        ('OLD-3003', 'Old Concrete Anchor Kit (Discontinued)', -45, 28.00, 54.99, '2022-12-01', '2023-07-10',
         'Discontinued'),
        ('NEW-3003', 'Tapcon Pro Kit 1/4x3-1/4" (Replacement)', 420, 35.00, 64.99, '2025-11-28', '2025-12-02',
         'Active'),

        # High-value fasteners
        ('MW-4001', 'Midwest Stainless Hex Bolts Assortment (Large)', 65, 72.00, 129.99, '2025-10-15', '2025-11-10',
         'Active'),
        ('GRK-5001', 'GRK RSS Structural Screws 3-1/8" (100pk)', 320, 58.50, 94.99, '2025-11-01', '2025-12-04',
         'Active'),
        ('SPAX-6001', 'Spax PowerLag 5/16x6" (50pk)', 220, 68.00, 109.99, '2025-10-05', '2025-11-25', 'Active'),

        # Lumber with big negatives
        ('LUM-7001', '2x4x8 SPF Stud', -11033, 4.50, 8.99, '2025-12-01', '2025-11-28', 'Active'),
        ('LUM-7002', '4x4x8 Treated Post', -850, 12.80, 24.99, '2025-11-10', '2025-11-20', 'Active'),

        # Normal active items
        ('PAINT-8001', 'Krylon Fusion Spray Paint Gloss Black', 85, 6.80, 12.99, '2025-12-12', '2025-12-08', 'Active'),
        ('ELEC-8002', 'Leviton Decora Outlet White (10pk)', 140, 8.50, 16.99, '2025-12-10', '2025-12-05', 'Active'),

        # Dead stock (no sales in years)
        ('DEAD-10001', 'Obsolete LED Bulb 40W Equivalent (Old Model)', 150, 4.20, 9.99, '2022-03-15', '2022-06-10',
         'Active'),
        ('DEAD-10002', 'Discontinued Brass Ball Valve 3/4"', 80, 18.50, 34.99, '2021-11-20', '2022-02-05', 'Active'),
        ('DEAD-10003', 'Old Style Door Knob Set (Oil Rubbed Bronze)', 55, 22.00, 44.99, '2022-01-10', '2022-04-18',
         'Active'),
        ('DEAD-10004', 'Vintage Halogen Work Light 500W', 30, 25.00, 49.99, '2020-12-05', '2021-03-12', 'Active'),
    ]

    # Add 30 more random normal items for realism
    random.seed(42)
    for i in range(30):
        sku = f'NORM-{12000 + i}'
        desc = f'Generic Hardware Item {i + 1}'
        qoh = random.randint(10, 300)
        cost = round(random.uniform(5.0, 100.0), 2)
        retail = round(cost * random.uniform(1.8, 2.5), 2)
        last_sold = f'2025-{random.randint(9, 12):02d}-{random.randint(1, 28):02d}'
        last_recv = f'2025-{random.randint(10, 12):02d}-{random.randint(1, 28):02d}'
        data.append((sku, desc, qoh, cost, retail, last_sold, last_recv, 'Active'))

    df = pd.DataFrame(data,
                      columns=['sku', 'description', 'qoh', 'cost', 'retail', 'last_sold_date', 'last_received_date',
                               'status'])
    df['last_sold_date'] = pd.to_datetime(df['last_sold_date'], errors='coerce')
    df['last_received_date'] = pd.to_datetime(df['last_received_date'], errors='coerce')
    return df


# ==================== MAIN ANALYSIS ====================
df = connect_and_fetch('inventory.db')  # Change name if your DB file is different

today = datetime(2025, 12, 17)

# Calculations
df['days_since_last_sale'] = (today - df['last_sold_date']).dt.days
df['inventory_value_at_cost'] = df['qoh'] * df['cost']
df['potential_lost_margin'] = np.where(df['qoh'] > 0, df['qoh'] * (df['retail'] - df['cost']), 0)

# Report Header
print("PIKE CREEK COMMUNITY HARDWARE - INVENTORY HEALTH REPORT")
print("=" * 70)
print(f"Report Date: {today.strftime('%B %d, %Y')}")
print(f"Total Items Analyzed: {len(df):,}\n")

# 1. Replacement Overstock
print("1. REPLACEMENT SKU OVERSTOCK (from discontinued substitution)")
print("-" * 60)
repl_overstock = df[
    df['description'].str.contains('repl|replacement|new', case=False, na=False) &
    (df['qoh'] > df['qoh'].quantile(0.9))  # Top 10% of stock levels
    ]
if not repl_overstock.empty:
    print(repl_overstock[['sku', 'description', 'qoh', 'inventory_value_at_cost']].to_string(index=False))
    print(f"\nTotal cost tied up in excess replacements: ${repl_overstock['inventory_value_at_cost'].sum():,.2f}")
else:
    print("No severe replacement overstock detected.")

print("\n")

# 2. Negative QOH
print("2. NEGATIVE QUANTITY ON HAND")
print("-" * 60)
negative = df[df['qoh'] < 0]
if not negative.empty:
    print(f"Items with negative QOH: {len(negative):,}")
    worst = negative.loc[negative['qoh'].idxmin()]
    print(f"Most negative: {worst['description']} (QOH: {worst['qoh']:,})")
    print(f"Total missing units: {negative['qoh'].sum():,}")
    print(f"Estimated unrecorded shrink cost: ${abs(negative['inventory_value_at_cost'].sum()):,.2f}")
else:
    print("No negative QOH found.")

print("\n")

# 3. Dead Stock
print("3. DEAD STOCK (No sales in 18+ months)")
print("-" * 60)
dead_stock = df[(df['days_since_last_sale'] > 547) & (df['qoh'] > 0)]
if not dead_stock.empty:
    print(f"Dead stock items: {len(dead_stock):,}")
    print(
        dead_stock[['sku', 'description', 'qoh', 'days_since_last_sale', 'inventory_value_at_cost']].head(15).to_string(
            index=False))
    print(f"\nTotal cost tied up in dead stock: ${dead_stock['inventory_value_at_cost'].sum():,.2f}")
    print("Recommendation: Clearance pricing, donation, or write-off.")
else:
    print("No dead stock detected.")

print("\n")

# 4. Financial Summary
print("4. ESTIMATED FINANCIAL IMPACT SUMMARY")
print("-" * 60)
total_value = df['inventory_value_at_cost'].sum()
dead_value = dead_stock['inventory_value_at_cost'].sum() if not dead_stock.empty else 0
negative_shrink = abs(negative['inventory_value_at_cost'].sum()) if not negative.empty else 0
overstock_margin = df['potential_lost_margin'].sum()

print(f"Total inventory value at cost:          ${total_value:,.2f}")
print(f"Value locked in dead stock:             ${dead_value:,.2f}")
print(f"Estimated shrink from negative QOH:     ${negative_shrink:,.2f}")
print(f"Potential lost gross profit in overstock: ${overstock_margin:,.2f}")
print("\nThese ongoing issues artificially lower COGS and inflate reported profits.")
print("Proactive SKU cleanup, cycle counts, and pricing discipline would")
print("dramatically improve accuracy, cash flow, and long-term viability.")