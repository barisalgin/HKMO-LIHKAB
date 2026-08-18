import psycopg2
import json
import os

SUPABASE_URL = 'postgresql://postgres:barisalginHKMO@db.dmpbiioazwdrutyqxqzq.supabase.co:5432/postgres'

def get_connection():
    return psycopg2.connect(SUPABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. İlçeler
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS districts (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        multiplier REAL NOT NULL
    )
    ''')

    # 2. LİHKAB Büroları
    # active_district_id: LİHKAB'ın bulunduğu tek bir ilçe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lihkabs (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        owner TEXT NOT NULL,
        active_district_id INTEGER NOT NULL, 
        total_revenue REAL DEFAULT 0.0,
        total_transport_revenue REAL DEFAULT 0.0,
        is_active BOOLEAN DEFAULT TRUE,
        is_deleted BOOLEAN DEFAULT FALSE,
        address TEXT,
        registry_number TEXT,
        university TEXT,
        FOREIGN KEY(active_district_id) REFERENCES districts(id)
    )
    ''')

    # 3. İşler (Atamalar)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id SERIAL PRIMARY KEY,
        job_name TEXT NOT NULL,
        district_id INTEGER NOT NULL,
        lihkab_id INTEGER NOT NULL,
        price REAL NOT NULL,
        transport_price REAL DEFAULT 0.0,
        parameters_json TEXT,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT DEFAULT 'Sistem',
        FOREIGN KEY(district_id) REFERENCES districts(id),
        FOREIGN KEY(lihkab_id) REFERENCES lihkabs(id)
    )
    ''')

    # 4. Kullanıcılar (Sisteme Giriş İçin)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        can_assign_job BOOLEAN DEFAULT FALSE,
        can_add_office BOOLEAN DEFAULT FALSE,
        can_manage_office BOOLEAN DEFAULT FALSE,
        can_fix_errors BOOLEAN DEFAULT FALSE
    )
    ''')

    # Migration for existing DBs
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN can_assign_job BOOLEAN DEFAULT FALSE")
        cursor.execute("ALTER TABLE users ADD COLUMN can_add_office BOOLEAN DEFAULT FALSE")
        cursor.execute("ALTER TABLE users ADD COLUMN can_manage_office BOOLEAN DEFAULT FALSE")
        cursor.execute("ALTER TABLE users ADD COLUMN can_fix_errors BOOLEAN DEFAULT FALSE")
    except psycopg2.Error:
        conn.rollback()
        pass # Columns probably already exist
        
    try:
        cursor.execute("ALTER TABLE lihkabs ADD COLUMN total_transport_revenue REAL DEFAULT 0.0")
        cursor.execute("ALTER TABLE jobs ADD COLUMN transport_price REAL DEFAULT 0.0")
    except psycopg2.Error:
        conn.rollback()
        pass # Columns probably already exist

    conn.commit()
    
    _seed_data(conn)
    conn.close()

def _seed_data(conn):
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM districts")
    if cursor.fetchone()[0] > 0:
        return

    # PDF Sayfa 14'e göre Bursa Katsayıları
    districts = [
        ("Büyükorhan", 1.0),
        ("Gemlik", 1.2),
        ("Gürsu", 1.2),
        ("Harmancık", 1.0),
        ("İnegöl", 1.0),
        ("İznik", 1.1),
        ("Karacabey", 1.1),
        ("Keles", 1.0),
        ("Kestel", 1.2),
        ("Mudanya", 1.4),
        ("Mustafakemalpaşa", 1.1),
        ("Nilüfer", 1.5),
        ("Orhaneli", 1.1),
        ("Orhangazi", 1.1),
        ("Osmangazi", 1.5),
        ("Yenişehir", 0.9),
        ("Yıldırım", 1.5)
    ]
    cursor.executemany("INSERT INTO districts (name, multiplier) VALUES (%s, %s)", districts)

    # Örnek LİHKAB Büroları (active_district_id kullanılarak)
    # Nilüfer (id:12), Osmangazi (id:15), Mudanya (id:10), Yıldırım (id:17)
    lihkab_data = [
        ("Yıldız LİHKAB", "Ahmet Yılmaz", 12, 0.0),
        ("Ufuk LİHKAB", "Ayşe Demir", 17, 0.0),
        ("Zirve LİHKAB", "Mehmet Kaya", 15, 0.0),
        ("Güven LİHKAB", "Ali Can", 10, 0.0)
    ]
    cursor.executemany("INSERT INTO lihkabs (name, owner, active_district_id, total_revenue) VALUES (%s, %s, %s, %s)", lihkab_data)

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Veritabanı başarıyla güncellendi.")
