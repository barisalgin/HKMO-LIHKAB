import sqlite3
import bcrypt

DB_PATH = 'lihkab_havuz.db'

def create_users_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Check if user exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'barisalgin'")
    if cursor.fetchone()[0] == 0:
        # Create default user
        password = "baris123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ('barisalgin', hashed))
        print("Kullanıcı 'barisalgin' (şifre: baris123) başarıyla oluşturuldu.")
    else:
        print("Kullanıcı zaten mevcut.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_users_table()
