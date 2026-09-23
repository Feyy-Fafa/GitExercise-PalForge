import sqlite3
import os

def seed_database():
    db_path = os.path.join(os.path.dirname(__file__), 'palworld.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')

    # 1. WIPE OLD DATA AND REBUILD BASE TABLES (Bulletproof Method)
    cursor.execute('DROP TABLE IF EXISTS recipes')
    cursor.execute('DROP TABLE IF EXISTS drop_sources')
    cursor.execute('DROP TABLE IF EXISTS user_queues')
    cursor.execute('DROP TABLE IF EXISTS items')

    cursor.execute('''
        CREATE TABLE items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            category TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE recipes (
            crafted_item_id INTEGER,
            ingredient_item_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY(crafted_item_id) REFERENCES items(id),
            FOREIGN KEY(ingredient_item_id) REFERENCES items(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE user_queues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            quantity INTEGER
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        item_name TEXT PRIMARY KEY,
        quantity INTEGER DEFAULT 0
    )
''')

    # 2. INSERT ALL BASE ITEMS
    items = [
        # Base Raw Items (Cannot be crafted)
        ('Flame Organ', 'raw'), ('Leather', 'raw'), ('High Quality Pal Oil', 'raw'),
        ('Ice Organ', 'raw'), ('Fiber', 'raw'), ('Paldium Fragment', 'raw'), 
        ('Wood', 'raw'), ('Stone', 'raw'), ('Hardwood', 'raw'), ('Mythical Wood', 'raw'),
        ('Ore', 'raw'), ('Pure Quartz', 'raw'), ('Coal', 'raw'), 
        ('Crude Oil', 'raw'), ('Chromite', 'raw'), ('Hexolite Quartz', 'raw'), 
        ('Soralite', 'raw'), ('Paloxite', 'raw'), ('World Tree Holy Water', 'raw'),
        ('Venom Gland', 'raw'), ('Sulfur', 'raw'), ('Electric Organ', 'raw'), 
        ('Aquatic Pal Fluids', 'raw'), ('Ancient Civilization Core', 'raw'),

        # Crafted Materials (Have recipes)
        ('Corrosive Solvent', 'materials'), ('Cryogenic Coolant', 'materials'), 
        ('Thermal Core', 'materials'), ('AI Core', 'materials'), 
        ('Paloxite Ingot', 'materials'), ('Soralite Ingot', 'materials'),
        ('High Quality Cloth', 'materials'), ('Plasteel', 'materials'), ('Hexolite', 'materials'),
        ('Pal Metal Ingot', 'materials'), ('Refined Ingot', 'materials'), ('Ingot', 'materials'),
        ('Cloth', 'materials'), ('Hallowed Bar', 'materials'), ('Cement', 'materials'),
        ('Bio Battery', 'materials'), ('Carbon Fiber', 'materials'), ('Computer', 'materials'),
        ('Circuit Board', 'materials'), ('Polymer', 'materials'),

        # Armor Sets
        ('Lightweight Ancient Armor', 'armor'), ('Cold-Resistant Ancient Armor', 'armor'),
        ('Heat-Resistant Ancient Armor', 'armor'), ('Ancient Armor', 'armor'),
        ('Lightweight Hexolite Armor', 'armor'), ('Hexolite Armor', 'armor'),
        ('V2 Armor', 'armor'), ('Plasteel Armor', 'armor'),
        ('Pal Metal Armor', 'armor'), ('Refined Metal Armor', 'armor'),
        ('V1 Armor', 'armor'), ('Metal Armor', 'armor'), ('Pelt Armor', 'armor'), 
        ('Tropical Outfit', 'armor'), ('Tundra Outfit', 'armor'), ('Cloth Outfit', 'armor'), 
        ('Hallowed Plate Mail', 'armor'),

        # Spheres
        ('Pal Sphere', 'spheres'), ('Mega Sphere', 'spheres'), ('Giga Sphere', 'spheres'),
        ('Hyper Sphere', 'spheres'), ('Ultra Sphere', 'spheres'), ('Legendary Sphere', 'spheres'),
        ('Ultimate Sphere', 'spheres'), ('Exotic Sphere', 'spheres'), ('Sol Sphere', 'spheres'),
        ('Ancient Sphere', 'spheres')
    ]
    cursor.executemany('INSERT INTO items (name, category) VALUES (?, ?)', items)

    def get_id(name):
        cursor.execute('SELECT id FROM items WHERE name = ?', (name,))
        result = cursor.fetchone()
        if result: return result[0]
        else: raise ValueError(f"Item '{name}' not found in database!")

    # 3. INSERT RECIPES
    recipes = [
        # --- MATERIALS & INGOTS ---
        ('Ingot', 'Ore', 2),
        ('Pal Metal Ingot', 'Ore', 4), ('Pal Metal Ingot', 'Paldium Fragment', 2), ('Pal Metal Ingot', 'Pure Quartz', 1),
        ('Refined Ingot', 'Ore', 2), ('Refined Ingot', 'Coal', 2),
        ('Plasteel', 'Crude Oil', 5), ('Plasteel', 'Paldium Fragment', 5), ('Plasteel', 'Ore', 10),
        ('Hexolite', 'Chromite', 5), ('Hexolite', 'Hexolite Quartz', 12), ('Hexolite', 'Ore', 20),
        ('Paloxite Ingot', 'Soralite', 1), ('Paloxite Ingot', 'Paloxite', 2), ('Paloxite Ingot', 'World Tree Holy Water', 1),
        ('Soralite Ingot', 'Soralite', 2), ('Soralite Ingot', 'Pure Quartz', 2),

        # --- COMPONENTS & INTERMEDIATES ---
        ('Corrosive Solvent', 'Venom Gland', 1), ('Corrosive Solvent', 'Sulfur', 1),
        ('Cryogenic Coolant', 'Aquatic Pal Fluids', 1), ('Cryogenic Coolant', 'Ice Organ', 1),
        ('Thermal Core', 'Flame Organ', 4), ('Thermal Core', 'Coal', 8), ('Thermal Core', 'Corrosive Solvent', 2), ('Thermal Core', 'Hexolite', 2),
        ('Bio Battery', 'Electric Organ', 1), ('Bio Battery', 'Refined Ingot', 1), ('Bio Battery', 'Carbon Fiber', 1), 
        ('AI Core', 'Computer', 5), ('AI Core', 'Soralite Ingot', 10), ('AI Core', 'Thermal Core', 2), ('AI Core', 'Ancient Civilization Core', 1),
        ('Computer', 'Circuit Board', 2), ('Computer', 'Plasteel', 3), ('Computer', 'Bio Battery', 2), ('Computer', 'Carbon Fiber', 2),
        ('Circuit Board', 'Pure Quartz', 2), ('Circuit Board', 'Polymer', 1),
        ('Polymer', 'High Quality Pal Oil', 2),
        ('Carbon Fiber', 'Coal', 2), ('Carbon Fiber', 'Flame Organ', 1),
        
        # --- SPHERES ---
        ('Pal Sphere', 'Paldium Fragment', 3),
        ('Mega Sphere', 'Wood', 3), ('Mega Sphere', 'Stone', 3), ('Mega Sphere', 'Ingot', 1), ('Mega Sphere', 'Paldium Fragment', 1),
        ('Giga Sphere', 'Wood', 5), ('Giga Sphere', 'Stone', 5), ('Giga Sphere', 'Ingot', 2), ('Giga Sphere', 'Paldium Fragment', 2),
        ('Hyper Sphere', 'Wood', 8), ('Hyper Sphere', 'Stone', 8), ('Hyper Sphere', 'Ingot', 3), ('Hyper Sphere', 'Paldium Fragment', 3), ('Hyper Sphere', 'Cement', 2),
        ('Ultra Sphere', 'Wood', 10), ('Ultra Sphere', 'Stone', 10), ('Ultra Sphere', 'Paldium Fragment', 5), ('Ultra Sphere', 'Refined Ingot', 3),
        ('Legendary Sphere', 'Stone', 20), ('Legendary Sphere', 'Paldium Fragment', 5), ('Legendary Sphere', 'Pal Metal Ingot', 3), ('Legendary Sphere', 'Hardwood', 3),
        ('Ultimate Sphere', 'Paldium Fragment', 10), ('Ultimate Sphere', 'Pal Metal Ingot', 5), ('Ultimate Sphere', 'Plasteel', 1), ('Ultimate Sphere', 'Hardwood', 10),
        ('Exotic Sphere', 'Paldium Fragment', 15), ('Exotic Sphere', 'Plasteel', 1), ('Exotic Sphere', 'Hexolite', 1), ('Exotic Sphere', 'Hardwood', 10),
        ('Sol Sphere', 'Paldium Fragment', 30), ('Sol Sphere', 'Soralite Ingot', 2), ('Sol Sphere', 'Hardwood', 10),
        ('Ancient Sphere', 'Paldium Fragment', 30), ('Ancient Sphere', 'Paloxite Ingot', 6), ('Ancient Sphere', 'Mythical Wood', 3),

        # --- ARMORS ---
        ('Lightweight Ancient Armor', 'Corrosive Solvent', 50), ('Lightweight Ancient Armor', 'AI Core', 7), ('Lightweight Ancient Armor', 'Paloxite Ingot', 30),
        ('Cold-Resistant Ancient Armor', 'Cryogenic Coolant', 50), ('Cold-Resistant Ancient Armor', 'AI Core', 5), ('Cold-Resistant Ancient Armor', 'Paloxite Ingot', 30),
        ('Heat-Resistant Ancient Armor', 'Thermal Core', 6), ('Heat-Resistant Ancient Armor', 'AI Core', 5), ('Heat-Resistant Ancient Armor', 'Paloxite Ingot', 30),
        ('Ancient Armor', 'Soralite Ingot', 30), ('Ancient Armor', 'AI Core', 3),
        ('Lightweight Hexolite Armor', 'High Quality Cloth', 10), ('Lightweight Hexolite Armor', 'Plasteel', 20), ('Lightweight Hexolite Armor', 'Hexolite', 100), ('Lightweight Hexolite Armor', 'Corrosive Solvent', 10),
        ('Hexolite Armor', 'High Quality Cloth', 10), ('Hexolite Armor', 'Plasteel', 20), ('Hexolite Armor', 'Hexolite', 50),
        ('V2 Armor', 'High Quality Cloth', 20), ('V2 Armor', 'Pal Metal Ingot', 40), ('V2 Armor', 'Plasteel', 40),
        ('Plasteel Armor', 'High Quality Cloth', 5), ('Plasteel Armor', 'Pal Metal Ingot', 30), ('Plasteel Armor', 'Plasteel', 30),
        ('Pal Metal Armor', 'Leather', 20), ('Pal Metal Armor', 'High Quality Cloth', 2), ('Pal Metal Armor', 'Pal Metal Ingot', 20),
        ('Refined Metal Armor', 'Leather', 15), ('Refined Metal Armor', 'High Quality Cloth', 1), ('Refined Metal Armor', 'Refined Ingot', 30),
        ('V1 Armor', 'High Quality Pal Oil', 15), ('V1 Armor', 'Ingot', 30),
        ('Metal Armor', 'Leather', 10), ('Metal Armor', 'Ingot', 30), ('Metal Armor', 'Cloth', 5),
        ('Pelt Armor', 'Leather', 10), ('Pelt Armor', 'Fiber', 20), ('Pelt Armor', 'Ingot', 10),
        ('Tropical Outfit', 'Flame Organ', 2), ('Tropical Outfit', 'Cloth', 3),
        ('Tundra Outfit', 'Ice Organ', 2), ('Tundra Outfit', 'Cloth', 3),
        ('Cloth Outfit', 'Fiber', 7), ('Cloth Outfit', 'Cloth', 2),
        ('Hallowed Plate Mail', 'Hallowed Bar', 20)
    ]

    for crafted, ingredient, qty in recipes:
        cursor.execute('''
            INSERT INTO recipes (crafted_item_id, ingredient_item_id, quantity)
            VALUES (?, ?, ?)
        ''', (get_id(crafted), get_id(ingredient), qty))

    # 4. INSERT DROP SOURCES (Drop Maps Feature)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drop_sources (
            item_name TEXT,
            source TEXT,
            UNIQUE(item_name, source)
        )
    ''')

    drop_data = [
        ("Flame Organ", "rooby, Kelpsea Ignis, Flambelle at ranch"),
        ("Leather", "surfent at ranch"),
        ("High Quality Pal Oil", "Dumud at ranch"),
        ("Ice Organ", "Foxcicle at ranch"),
        ("Fiber", "Crafted at Crusher"),
        ("Paldium Fragment", "Crafted at Crusher"),
        ("Paldium Fragment", "Mining Paldium Rocks"),
        ("Paldium Fragment", "Random drop from mining Stone"),
        ("Wood", "Lumbering trees"),
        ("Wood", "Logging site"),
        ("Stone", "Mining rocks"),
        ("Stone", "Mining Site"),
        ("Hardwood", "Logging site 2"),
        ("Mythical Wood", "Lumbering Trees at the World Tree"),
        ("Mythical Wood", "Ancient Relic Recycler"),
        ("Ore", "Mining Ore Nodes"),
        ("Ore", "Ore mining site"),
        ("Ore", "Ore mining site 2"),
        ("Pure Quartz", "Mined at Pure quatz nodes found at Astral Mountains"),
        ("Pure Quartz", "Pure Quartz Quarry"),
        ("Coal", "Coal Rocks"),
        ("Coal", "Coal Quarry"),
        ("Crude Oil", "Crude oil Extractor over crude oil deposit"),
        ("Crude Oil", "Treasure Chest"),
        ("Crude Oil", "Oil rigs"),
        ("Crude Oil", "Syndicate Thugs"),
        ("Chromite", "Capture or butcher Smokie"),
        ("Chromite", "Using Smokie's(Pal) partner skill in dungeons and around Feybreak"),
        ("Chromite", "Ancient Material Synthesizer"),
        ("Hexolite Quartz", "Mine at Hexolite Node at Feybreak Island"),
        ("Hexolite Quartz", "Hexolite Quartz Mine"),
        ("Soralite", "Mining Soralite nodes at Sunreach isle"),
        ("Soralite", "Soralite Quarry"),
        ("Paloxite", "Mining Paloxite Node at World Tree"),
        ("World Tree Holy Water", "Defeating Pals in the World Tree"),
        ("Venom Gland", "Depresso"),
        ("Venom Gland", "Capricity Noct at ranch"),
        ("Sulfur", "Mining Sulfur Rocks at Volcanic regions"),
        ("Sulfur", "Sulfur Mine"),
        ("Electric Organ", "Sparkit at ranch"),
        ("Aquatic Pal Fluids", "Kelpsea (Pal) at ranch"),
        ("Ancient Civilization Core", "Expeditions"),
        ("Ancient Civilization Core", "Ancient Relic Recycler"),
        ("Ancient Civilization Core", "Oil rigs"),
        ("Thermal Core", "Dropped By Aegidron"),
        ("High quality Pal Cloth", "Sibelyx at ranch"),
        ("Cloth", "Crafted for 2 wool"),
        ("Hallowed Bar", "Defeating enemies in Sealed Realm of Terraria"),
        ("Polymer", "Crafted from High Quality Pal Oil")
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO drop_sources (item_name, source) 
        VALUES (?, ?)
    ''', drop_data)

    conn.commit()
    print(f"Database successfully seeded with {len(items)} items and {len(recipes)} recipes, plus drop sources!")
    conn.close()

if __name__ == "__main__":
    seed_database()