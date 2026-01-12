import sqlite3

DB_FILE = "flashcards.db"

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                term TEXT NOT NULL,
                definition TEXT NOT NULL,
                FOREIGN KEY (deck_id) REFERENCES decks(id)
            )
        """)

def create_deck(name: str) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO decks(name) VALUES (?)", (name,))
        cur.execute("SELECT id FROM decks WHERE name = ?", (name,))
        return cur.fetchone()[0]

def add_card(deck_id: int, term: str, definition: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO cards(deck_id, term, definition) VALUES (?, ?, ?)",
            (deck_id, term, definition)
        )

def get_cards(deck_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, term, definition FROM cards WHERE deck_id = ?", (deck_id,))
        return cur.fetchall()
    
def get_decks():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM decks ORDER BY name")
        return cur.fetchall()

def get_random_card(deck_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, term, definition FROM cards WHERE deck_id = ? ORDER BY RANDOM() LIMIT 1",
            (deck_id,)
        )
        return cur.fetchone()  # (id, term, definition) or None

def count_cards(deck_id: int) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM cards WHERE deck_id = ?", (deck_id,))
        return cur.fetchone()[0]
