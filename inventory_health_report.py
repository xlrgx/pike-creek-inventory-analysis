"""
Pike Creek Community Hardware - Real Inventory Health Analyzer
Author: Joseph Hopkins
Date: August 2025

This version connects to a simulated MySQL database (AI generated)
and runs queries against the MySQL database.
to identify:
- Replacement SKU overstock from discontinued substitution
- Negative Quantity on Hand
- Dead stock (no sales in 18+ months)
- Hidden financial impact on COGS and cash flow

Perfect for documenting issues and proposed fixes professionally.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import numpy as np
import os

# ==== CONFIGURATION ====
# Fill these in with your database details (keep private - use .env or separate config in real use)
DB_CONFIG = {
    'host': 'localhost',          # or your server IP
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_inventory_db_name',
    'raise_on_warnings': True
}

# Query to pull relevant inventory data - customize table/column names to match your system
INVENTORY_QUERY = """
SELECT 
    item_number AS sku,
    description,
    quantity_on_hand AS qoh,
    cost,
    retail_price AS retail,
    last_sold_date,
    last_received_date,
    status  -- e.g., 'Active', 'Discontinued'
FROM items
WHERE 1=1
-- Optional filters to speed up: active locations only, etc.
"""

# ======================================================

def connect_and_fetch():
    """Connect to MySQL and return DataFrame with inventory data"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Successfully connected to database.")
        df = pd.read_sql(INVENTORY_QUERY, conn)
        conn.close()
        print(f"Loaded {len(df):,} items from database.\n")
        return df
    except Error as e:
        print(f"Database connection failed: {e}")
        print("Falling back to sample data for demonstration.\n")
        return generate_sample_data()

def generate_sample_data():
    """Fallback sample data when DB not available"""
    data = {
        'sku': ['12345', '12345-REPL', '67890', '67890-REPL', '54321', '98765', '11111', '22222'],
        'description': [
            'Old Widget A (Discontinued)',
            'New Widget A (Replacement)',
            'Old Bolt Pack (Discontinued)',
            'New Bolt Pack (Replacement)',
            'Fastener Kit - Stainless',
            'Spray Paint - Red (Slow Mover)',
            'Lumber 2x4x8 (High Negative)',
            'Caulk Tube - White'
        ],
        'qoh': [-50, 450, -200, 800, 120, 15, -11033, 35],
        'cost': [12.50, 14.00, 8.75, 10.20, 45.00, 9.99, 4.50, 6.50],
        'retail': [24.99, 27.99, 17.99, 21.99, 89.99, 14.99, 8.99, 12.99],
        'last_sold_date': [
            '2023-06-15', '2025-12-10', '2022-11-01', '2025-12-16', '2025-11-20',
            '2024-01-05', '2025-12-01', None
        ],
        'last_received_date': [
            '2024-03-10', '2025-12-01', '2023-09-20', '2025-12-15', '2025-10-30',
            '2024-02-20', '2025-11-28', '2025-12-10'
        ],
        'status': ['Discontinued', 'Active', 'Discontinued', 'Active', 'Active', 'Active', 'Active', 'Active']
    }
    df = pd.DataFrame(data)
    df['last_sold_date'] = pd.to_datetime(df['last_sold_date'])
    df['last_received_date'] = pd.to_datetime(df['last_received_date'])
    return df

# ===== MAIN ANALYSIS ====
df = connect_and_fetch()

today = datetime(2025, 12, 17)
df['days_since_last_sale'] = (today - df['last_sold_date']).dt.days
df['inventory_value_at_cost'] = df['qoh'] * df['cost']
df['potential_lost_margin'] = np.where(df['qoh'] > 0, df['qoh'] * (df['retail'] - df['cost']), 0)

print("PIKE CREEK COMMUNITY HARDWARE - INVENTORY HEALTH REPORT")
print("=" * 70)
print(f"Report Date: {today.strftime('%B %d, %Y')}")
print(f"Total Items Analyzed: {len(df):,}\n")

# 1. Replacement Overstock
print("1. REPLACEMENT SKU OVERSTOCK (Potential from discontinued substitution)")
print("-" * 60)
repl_overstock = df[
    df['description'].str.contains('repl|replacement|new version', case=False, na=False) &
    (df['qoh'] > df['qoh'].quantile(0.95))  # Top 5% of stock levels
]
if not repl_overstock.empty:
    print(repl_overstock[['sku', 'description', 'qoh', 'inventory_value_at_cost']].head(10))
    print(f"\nTotal cost tied up in high-stock replacements: ${repl_overstock['inventory_value_at_cost'].sum():,.2f}")
else:
    print("No obvious replacement overstock detected.")

print("\n")

# 2. Negative QOH
print("2. NEGATIVE QUANTITY ON HAND")
print("-" * 60)
negative = df[df['qoh'] < 0]
if not negative.empty:
    print(f"Items with negative QOH: {len(negative):,}")
    print(f"Most negative: {negative.loc[negative['qoh'].idxmin(), 'description']} (QOH: {negative['qoh'].min():,})")
    print(f"Total missing units: {negative['qoh'].sum():,}")
    print(f"Estimated unrecorded shrink cost: ${abs(negative['inventory_value_at_cost'].sum()):,.2f}")
else:
    print("No negative QOH found.")

print("\n")

# 3. Dead Stock
print("3. DEAD STOCK (No sales in 18+ months)")
print("-" * 60)
dead_stock = df[df['days_since_last_sale'] > 547]
dead_stock = dead_stock[dead_stock['qoh'] > 0]  # Only positive stock
if not dead_stock.empty:
    print(f"Dead stock items: {len(dead_stock):,}")
    print(dead_stock[['sku', 'description', 'qoh', 'days_since_last_sale', 'inventory_value_at_cost']].head(15))
    print(f"\nTotal cost tied up in dead stock: ${dead_stock['inventory_value_at_cost'].sum():,.2f}")
    print("Recommendation: Mark down, clearance, donate, or write off.")
else:
    print("No dead stock detected.")

print("\n")

# 4. Summary
print("4. ESTIMATED FINANCIAL IMPACT")
print("-" * 60)
total_value = df['inventory_value_at_cost'].sum()
dead_value = dead_stock['inventory_value_at_cost'].sum() if not dead_stock.empty else 0
negative_shrink = abs(negative['inventory_value_at_cost'].sum()) if not negative.empty else 0

print(f"Total inventory value at cost: ${total_value:,.2f}")
print(f"Value in dead stock: ${dead_value:,.2f}")
print(f"Estimated shrink from negatives: ${negative_shrink:,.2f}")
print(f"Potential lost gross profit in overstock: ${df['potential_lost_margin'].sum():,.2f}")
print("\nThese issues distort COGS downward, inflating reported profits.")
print("Proactive cleanup would improve accuracy, cash flow, and competitiveness.")