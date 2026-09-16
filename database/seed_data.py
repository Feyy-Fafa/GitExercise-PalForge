import sqlite3
import os

def seed_database():
    db_path = os.path.join(os.path.dirname(__file__), 'palworld.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')

    # 1. WIPE OLD DATA (Prevents duplicates when re-running)
    cursor.execute('DELETE FROM recipes')
    cursor.execute('DELETE FROM drop_sources')
    cursor.execute('DELETE FROM user_queues')
    cursor.execute('DELETE FROM items')

    # 2. INSERT ALL BASE ITEMS (Armors, Spheres, Materials)
    items = [
        # Materials & Raw
        ('Corrosive Solvent', 'raw'), ('AI Core', 'materials'), ('Paloxite Ingot', 'materials'),
        ('Cryogenic Coolant', 'raw'), ('Thermal Core', 'materials'), ('Soralite Ingot', 'materials'),
        ('High Quality Cloth', 'materials'), ('Plasteel', 'materials'), ('Hexolite', 'materials'),
        ('Pal Metal Ingot', 'materials'), ('Flame Organ', 'raw'), ('Leather', 'raw'),
        ('Refined Ingot', 'materials'), ('High Quality Pal Oil', 'raw'), ('Ingot', 'materials'),
        ('Ice Organ', 'raw'), ('Cloth', 'materials'), ('Fiber', 'raw'), ('Hallowed Bar', 'materials'),
        ('Paldium Fragment', 'raw'), ('Wood', 'raw'), ('Stone', 'raw'), ('Cement', 'materials'),
        ('Hardwood', 'raw'), ('Mythical Wood', 'raw'),

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

    conn.commit()
    print(f"M2 Task 2 Complete: {len(items)} items and {len(recipes)} recipe links seeded!")
    conn.close()

if __name__ == "__main__":
    seed_database()