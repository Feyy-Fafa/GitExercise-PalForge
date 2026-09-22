import eel
import sqlite3
from collections import defaultdict
from database import m3_engine

# Initialize the web folder for Eel
eel.init('web')

@eel.expose
def get_all_drop_sources():
    conn = sqlite3.connect('database/palworld.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT item_name, source FROM drop_sources ORDER BY item_name ASC")
    rows = cursor.fetchall()
    conn.close()

    grouped_sources = defaultdict(list)
    for item_name, source in rows:
        grouped_sources[item_name].append(source)
        
    return dict(grouped_sources)

# Start the application
if __name__ == '__main__':
    eel.start('index.html', size=(1100, 750))