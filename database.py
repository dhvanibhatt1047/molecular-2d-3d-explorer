import sqlite3

def init_db():
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect('molecules.db')
    cursor = conn.cursor()

    # Table to store all chemical informatics data for history and similarity
    # UPDATED: Removed Bond Analysis columns as requested
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,            -- The official IUPAC/Common name
            search_query TEXT,     -- NEW: Exactly what the user typed
            smiles TEXT,          -- 1D Chemical string (Needed for similarity algorithm)
            weight REAL,
            logp REAL,
            qed REAL,
            h_donors INTEGER,
            h_acceptors INTEGER,
            image_2d TEXT,        -- Base64 string for 2D diagram
            mol_3d TEXT,          -- MOL block for 3D viewer
            status TEXT,          -- Verified vs Approximate
            
            classification TEXT,   -- Aromatic, Cyclic, or Aliphatic
            lipinski_status TEXT,  -- Pass ✅ / Fail ❌
            
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database Initialized Successfully.")

if __name__ == "__main__":
    init_db()
