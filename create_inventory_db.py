import sqlite3
import random

# Connect to (or create) the SQLite database file
conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Create the items table
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

# ===== ADD INDEXES FOR PERFORMANCE =====
cursor.execute('CREATE INDEX IF NOT EXISTS idx_qoh ON items(quantity_on_hand)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_sold ON items(last_sold_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_description ON items(description)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON items(status)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_dead_stock ON items(last_sold_date, quantity_on_hand)')

print("Table and indexes created/verified.")

# Clear any existing data (so re-running the script starts fresh)
cursor.execute('DELETE FROM items')

# ===== LARGE REALISTIC SAMPLE DATA =====
sample_data = [
    # Discontinued → Replacement pairs (core over-ordering problem)
    ('OLD-1001', 'Old Deck Screw 2-1/2" (Discontinued)', -120, 0.15, 0.39, '2023-08-20', '2024-01-15', 'Discontinued'),
    ('NEW-1001', 'Spax Deck Screw 2-1/2" (Replacement)', 1200, 0.22, 0.49, '2025-12-10', '2025-12-01', 'Active'),
    ('OLD-2002', 'Old Structural Bolt 1/2x6 (Discontinued)', -80, 2.80, 5.99, '2023-05-10', '2023-11-20', 'Discontinued'),
    ('NEW-2002', 'Simpson SDWS Framing Screw (Replacement)', 850, 3.50, 7.49, '2025-12-05', '2025-12-03', 'Active'),
    ('OLD-3003', 'Old Concrete Anchor Kit (Discontinued)', -45, 28.00, 54.99, '2022-12-01', '2023-07-10', 'Discontinued'),
    ('NEW-3003', 'Tapcon Pro Kit 1/4x3-1/4" (Replacement)', 420, 35.00, 64.99, '2025-11-28', '2025-12-02', 'Active'),

    # High-value fasteners (Midwest, GRK, Spax, etc.)
    ('MW-4001', 'Midwest Stainless Hex Bolts Assortment (Large)', 65, 72.00, 129.99, '2025-10-15', '2025-11-10', 'Active'),
    ('MW-4002', 'Midwest Grade 8 Flange Bolts Kit', 40, 55.00, 99.99, '2025-09-20', '2025-11-05', 'Active'),
    ('MW-4003', 'Midwest Nylon Lock Nuts Bulk Pack', 110, 38.00, 69.99, '2025-08-30', '2025-10-20', 'Active'),
    ('GRK-5001', 'GRK RSS Structural Screws 3-1/8" (100pk)', 320, 58.50, 94.99, '2025-11-01', '2025-12-04', 'Active'),
    ('GRK-5002', 'GRK Cabinet Screws #8x2" (500pk)', 180, 42.00, 74.99, '2025-07-15', '2025-09-10', 'Active'),
    ('SPAX-6001', 'Spax PowerLag 5/16x6" (50pk)', 220, 68.00, 109.99, '2025-10-05', '2025-11-25', 'Active'),

    # Lumber & Building Materials (big negatives)
    ('LUM-7001', '2x4x8 SPF Stud', -11033, 4.50, 8.99, '2025-12-01', '2025-11-28', 'Active'),
    ('LUM-7002', '4x4x8 Treated Post', -850, 12.80, 24.99, '2025-11-10', '2025-11-20', 'Active'),
    ('LUM-7003', '1/2" Plywood Sheathing 4x8', -220, 32.00, 59.99, '2025-09-15', '2025-10-01', 'Active'),

    # Normal active consumables
    ('PAINT-8001', 'Krylon Fusion Spray Paint Gloss Black', 85, 6.80, 12.99, '2025-12-12', '2025-12-08', 'Active'),
    ('ELEC-8002', 'Leviton Decora Outlet White (10pk)', 140, 8.50, 16.99, '2025-12-10', '2025-12-05', 'Active'),
    ('PLUMB-8003', 'SharkBite 1/2" Push Coupling', 95, 7.20, 14.99, '2025-12-15', '2025-12-10', 'Active'),

    # Slow movers
    ('TOOL-9001', 'Milwaukee M18 Battery XC5.0', 28, 99.00, 149.99, '2025-06-20', '2025-08-15', 'Active'),
    ('SEAS-9002', 'Weber Grill Cover 60"', 12, 45.00, 79.99, '2024-09-10', '2024-10-05', 'Active'),
    ('GARD-9003', 'Scotts Turf Builder Fertilizer 15k sq ft', 18, 38.00, 64.99, '2024-11-01', '2025-03-20', 'Active'),

    # Truly dead stock (no sales in 2–4 years)
    ('DEAD-10001', 'Obsolete LED Bulb 40W Equivalent (Old Model)', 150, 4.20, 9.99, '2022-03-15', '2022-06-10', 'Active'),
    ('DEAD-10002', 'Discontinued Brass Ball Valve 3/4"', 80, 18.50, 34.99, '2021-11-20', '2022-02-05', 'Active'),
    ('DEAD-10003', 'Old Style Door Knob Set (Oil Rubbed Bronze)', 55, 22.00, 44.99, '2022-01-10', '2022-04-18', 'Active'),
    ('DEAD-10004', 'Vintage Halogen Work Light 500W', 30, 25.00, 49.99, '2020-12-05', '2021-03-12', 'Active'),
    ('DEAD-10005', 'Old Packaging Duct Tape (Gray)', 200, 3.80, 7.99, '2022-07-01', '2022-09-15', 'Active'),

    # More variety
    ('FAST-11001', 'Hillman Anchor Kit Assortment', 75, 19.99, 34.99, '2025-11-18', '2025-12-01', 'Active'),
    ('ELEC-11002', 'Philips Hue White A19 Bulb 4pk', 42, 38.00, 69.99, '2025-10-25', '2025-11-15', 'Active'),
    ('PLUMB-11003', 'PVC 2" Schedule 40 Pipe 10ft', 60, 12.50, 24.99, '2025-09-30', '2025-10-20', 'Active'),
    ('TOOL-11004', 'DeWalt 20V Drill Bit Set 100pc', 35, 48.00, 89.99, '2025-08-10', '2025-09-05', 'Active'),
    ('PAINT-11005', 'Behr Premium Plus 5gal Eggshell White', 22, 145.00, 219.99, '2025-07-20', '2025-08-10', 'Active'),
]

# Add 20 extra random "normal" items to bulk it up to ~50 total
random.seed(123)  # For reproducibility
for i in range(20):
    sku = f'NORM-{20000 + i}'
    desc = f'Standard Hardware Item #{i+1} (Nails, Screws, etc.)'
    qoh = random.randint(20, 250)
    cost = round(random.uniform(4.0, 90.0), 2)
    retail = round(cost * random.uniform(1.9, 2.6), 2)
    last_sold = f'2025-{random.randint(8,12):02d}-{random.randint(1,28):02d}'
    last_recv = f'2025-{random.randint(9,12):02d}-{random.randint(1,28):02d}'
    sample_data.append((sku, desc, qoh, cost, retail, last_sold, last_recv, 'Active'))

# Insert all the data
cursor.executemany('''
    INSERT INTO items 
    (item_number, description, quantity_on_hand, cost, retail_price, last_sold_date, last_received_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', sample_data)

# Commit and close
conn.commit()
conn.close()

print(f"Database 'inventory.db' recreated with {len(sample_data)} realistic sample items,")
print("including discontinued/replacement overstock, massive negative lumber QOH, dead stock, and high-value fasteners.")
print("Indexes added for fast queries even at larger scale.")
print("Now run: python inventory_analyzer.py")