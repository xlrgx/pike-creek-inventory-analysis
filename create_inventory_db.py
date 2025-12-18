import sqlite3
from datetime import datetime

# Connect to (or create) the inventory database file
conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Create the 'items' table - this matches what our analyzer script expects
cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_number TEXT NOT NULL,
        description TEXT,
        quantity_on_hand INTEGER,
        cost REAL,
        retail_price REAL,
        last_sold_date DATE,
        last_received_date DATE,
        status TEXT
    )
''')

# Optional: Clear old data if re-running
cursor.execute('DELETE FROM items')

# Insert realistic sample data based on your store's issues
sample_data = [
    ('12345', 'Old Widget A (Discontinued)', -50, 12.50, 24.99, '2023-06-15', '2024-03-10', 'Discontinued'),
    ('12345-REPL', 'New Widget A (Replacement)', 450, 14.00, 27.99, '2025-12-10', '2025-12-01', 'Active'),
    ('67890', 'Old Bolt Pack (Discontinued)', -200, 8.75, 17.99, '2022-11-01', '2023-09-20', 'Discontinued'),
    ('67890-REPL', 'New Bolt Pack (Replacement)', 800, 10.20, 21.99, '2025-12-16', '2025-12-15', 'Active'),
    ('54321', 'Fastener Kit - Stainless (Midwest)', 120, 45.00, 89.99, '2025-11-20', '2025-10-30', 'Active'),
    ('98765', 'Spray Paint - Red (Slow Mover)', 15, 9.99, 14.99, '2024-01-05', '2024-02-20', 'Active'),
    ('11111', 'Lumber 2x4x8 (High Negative)', -11033, 4.50, 8.99, '2025-12-01', '2025-11-28', 'Active'),
    ('22222', 'Caulk Tube - White', 35, 6.50, 12.99, None, '2025-12-10', 'Active'),
    ('33333', 'GRK RSS Structural Screws 3" (100pk)', 280, 58.00, 89.99, '2025-10-15', '2025-12-05', 'Active'),
    ('44444', 'Tapcon Concrete Anchors 1/4x3" (100)', 95, 32.50, 59.99, '2025-08-20', '2025-11-01', 'Active'),
    ('55555', 'Dead Stock Item - No Sale in 3 Years', 60, 22.00, 44.99, '2022-04-10', '2023-01-15', 'Active'),
    ('66666', 'Midwest Stainless Hex Bolts Assortment', 45, 65.00, 119.99, '2025-09-30', '2025-11-20', 'Active'),
]

cursor.executemany('''
    INSERT INTO items 
    (item_number, description, quantity_on_hand, cost, retail_price, last_sold_date, last_received_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', sample_data)

# Commit and close
conn.commit()
conn.close()

print("Inventory database 'inventory.db' created and populated successfully!")
print("You can now run inventory_analyzer.py to generate the full report.")