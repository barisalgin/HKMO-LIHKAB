import sqlite3
import json
from database import get_connection
from hkmo_pricing import calculate_price
import urllib.request
import math

DISTRICT_COORDS = {
    "Osmangazi": (40.193298, 29.074202),
    "Nilüfer": (40.213611, 28.956667),
    "Yıldırım": (40.191667, 29.133333),
    "Gürsu": (40.23963, 29.18376),
    "Kestel": (40.198333, 29.213333),
    "Mudanya": (40.376111, 28.882222),
    "Gemlik": (40.432222, 29.1575),
    "Orhangazi": (40.490833, 29.313056),
    "İznik": (40.430000, 29.721667),
    "Yenişehir": (40.264444, 29.654167),
    "İnegöl": (40.081111, 29.510556),
    "Karacabey": (40.212778, 28.324444),
    "Mustafakemalpaşa": (40.038333, 28.406944),
    "Orhaneli": (39.901389, 28.986111),
    "Keles": (39.914167, 29.227222),
    "Büyükorhan": (39.771944, 28.948056),
    "Harmancık": (39.645556, 29.135278)
}

def get_distance_km(dist_a, dist_b):
    if dist_a == dist_b:
        return 0.0
    c1 = DISTRICT_COORDS.get(dist_a)
    c2 = DISTRICT_COORDS.get(dist_b)
    if not c1 or not c2:
        return 30.0 # Default
    R = 6371
    lat1, lon1 = math.radians(c1[0]), math.radians(c1[1])
    lat2, lon2 = math.radians(c2[0]), math.radians(c2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c * 1.3 # 1.3 road multiplier

def get_fuel_price():
    try:
        req = urllib.request.Request(
            'https://api.opet.com.tr/api/fuelprices/prices?ProvinceCode=16&IncludeAllProducts=true',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            for d in data:
                if d.get('districtName') == 'OSMANGAZİ':
                    prices = d.get('prices', [])
                    for p in prices:
                        if p.get('productShortName') == 'MT_ECO':
                            return float(p.get('amount'))
    except Exception as e:
        pass
    return 43.50 # Fallback price


DISTRICT_PROXIMITY = {
    "Osmangazi": ["Yıldırım", "Nilüfer", "Gürsu", "Kestel", "Mudanya", "Gemlik", "Keles", "Orhaneli", "İnegöl", "Yenişehir", "Orhangazi", "İznik", "Karacabey", "Mustafakemalpaşa", "Büyükorhan", "Harmancık"],
    "Nilüfer": ["Osmangazi", "Mudanya", "Yıldırım", "Karacabey", "Mustafakemalpaşa", "Orhaneli", "Gürsu", "Kestel", "Gemlik", "Keles", "İnegöl", "Yenişehir", "Büyükorhan", "Harmancık", "Orhangazi", "İznik"],
    "Yıldırım": ["Osmangazi", "Gürsu", "Kestel", "Nilüfer", "Keles", "İnegöl", "Mudanya", "Gemlik", "Yenişehir", "Orhaneli", "Orhangazi", "İznik", "Karacabey", "Mustafakemalpaşa", "Büyükorhan", "Harmancık"],
    "Gürsu": ["Kestel", "Yıldırım", "Osmangazi", "Nilüfer", "İnegöl", "Gemlik", "Yenişehir", "Mudanya", "Keles", "Orhangazi", "İznik", "Orhaneli", "Karacabey", "Mustafakemalpaşa", "Büyükorhan", "Harmancık"],
    "Kestel": ["Gürsu", "Yıldırım", "Osmangazi", "İnegöl", "Keles", "Nilüfer", "Yenişehir", "Gemlik", "Mudanya", "İznik", "Orhangazi", "Orhaneli", "Karacabey", "Mustafakemalpaşa", "Büyükorhan", "Harmancık"],
    "Mudanya": ["Nilüfer", "Osmangazi", "Gemlik", "Karacabey", "Yıldırım", "Gürsu", "Kestel", "Mustafakemalpaşa", "Orhangazi", "Yenişehir", "İznik", "Orhaneli", "İnegöl", "Keles", "Büyükorhan", "Harmancık"],
    "Gemlik": ["Orhangazi", "Mudanya", "Osmangazi", "Gürsu", "Yıldırım", "Kestel", "İznik", "Nilüfer", "Yenişehir", "Karacabey", "İnegöl", "Mustafakemalpaşa", "Keles", "Orhaneli", "Büyükorhan", "Harmancık"],
    "Orhangazi": ["Gemlik", "İznik", "Yenişehir", "Mudanya", "Osmangazi", "Gürsu", "Yıldırım", "Kestel", "Nilüfer", "Karacabey", "İnegöl", "Mustafakemalpaşa", "Keles", "Orhaneli", "Büyükorhan", "Harmancık"],
    "İznik": ["Orhangazi", "Yenişehir", "Gemlik", "İnegöl", "Kestel", "Gürsu", "Yıldırım", "Osmangazi", "Mudanya", "Nilüfer", "Keles", "Orhaneli", "Karacabey", "Mustafakemalpaşa", "Büyükorhan", "Harmancık"],
    "Yenişehir": ["İznik", "İnegöl", "Kestel", "Gürsu", "Orhangazi", "Yıldırım", "Gemlik", "Osmangazi", "Nilüfer", "Mudanya", "Keles", "Orhaneli", "Karacabey", "Mustafakemalpaşa", "Büyükorhan", "Harmancık"],
    "İnegöl": ["Kestel", "Yenişehir", "Gürsu", "Yıldırım", "Keles", "İznik", "Osmangazi", "Nilüfer", "Gemlik", "Orhangazi", "Orhaneli", "Mudanya", "Büyükorhan", "Karacabey", "Harmancık", "Mustafakemalpaşa"],
    "Karacabey": ["Mustafakemalpaşa", "Nilüfer", "Mudanya", "Osmangazi", "Yıldırım", "Gemlik", "Orhaneli", "Gürsu", "Kestel", "Orhangazi", "Büyükorhan", "Yenişehir", "İnegöl", "İznik", "Keles", "Harmancık"],
    "Mustafakemalpaşa": ["Karacabey", "Nilüfer", "Orhaneli", "Büyükorhan", "Mudanya", "Osmangazi", "Harmancık", "Yıldırım", "Keles", "Gemlik", "Gürsu", "Kestel", "İnegöl", "Yenişehir", "Orhangazi", "İznik"],
    "Orhaneli": ["Keles", "Büyükorhan", "Osmangazi", "Nilüfer", "Harmancık", "Mustafakemalpaşa", "Yıldırım", "Karacabey", "Gürsu", "Kestel", "İnegöl", "Mudanya", "Gemlik", "Yenişehir", "Orhangazi", "İznik"],
    "Keles": ["Orhaneli", "Osmangazi", "Yıldırım", "Kestel", "İnegöl", "Büyükorhan", "Gürsu", "Harmancık", "Nilüfer", "Yenişehir", "Mustafakemalpaşa", "Mudanya", "Gemlik", "Karacabey", "İznik", "Orhangazi"],
    "Büyükorhan": ["Harmancık", "Orhaneli", "Keles", "Mustafakemalpaşa", "Osmangazi", "Nilüfer", "Karacabey", "Yıldırım", "Gürsu", "Kestel", "İnegöl", "Mudanya", "Gemlik", "Yenişehir", "Orhangazi", "İznik"],
    "Harmancık": ["Büyükorhan", "Orhaneli", "Keles", "Mustafakemalpaşa", "Osmangazi", "Nilüfer", "Yıldırım", "Gürsu", "Kestel", "İnegöl", "Karacabey", "Mudanya", "Gemlik", "Yenişehir", "Orhangazi", "İznik"]
}

def get_districts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, multiplier FROM districts ORDER BY name")
    districts = cursor.fetchall()
    conn.close()
    return districts

def get_lihkabs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, owner, active_district_id, total_revenue, is_active, address, registry_number, university, total_transport_revenue FROM lihkabs WHERE is_deleted = 0 ORDER BY total_revenue ASC")
    lihkabs = cursor.fetchall()
    conn.close()
    return lihkabs

def get_jobs_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT j.id, j.job_name, d.name, l.name, j.price, j.assigned_at, j.parameters_json, j.created_by, j.transport_price
        FROM jobs j
        JOIN districts d ON j.district_id = d.id
        JOIN lihkabs l ON j.lihkab_id = l.id
        ORDER BY j.assigned_at DESC
    ''')
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def assign_job(job_name, district_id, params, username="Sistem"):
    """
    Havuzdan iş ataması yapar (LİHKAB Doygunluk ve Yakınlık algoritması ile).
    1. İlçedeki LİHKAB'lara bakılır.
    2. Doygunluğa (Yıllık Ortalama + 50.000 TL) ulaşmamış, kazancı en düşük olana verilir.
    3. Hepsi doygunsa veya ilçede ofis yoksa, mesafeye göre en yakın komşu ilçeye geçilir.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. İşin ilçesi ve çarpanı
    cursor.execute("SELECT name, multiplier FROM districts WHERE id = %s", (district_id,))
    target_dist_info = cursor.fetchone()
    target_dist_name = target_dist_info[0]
    multiplier = target_dist_info[1]
    
    # Fiyat hesaplama (Sadece İş Bedeli)
    price = calculate_price(job_name, params, multiplier)
    
    # 2. Tüm ilçeleri id -> name eşleştirmesi için çek
    cursor.execute("SELECT id, name FROM districts")
    dist_map = {row[1]: row[0] for row in cursor.fetchall()}
    reverse_dist_map = {row[0]: row[1] for row in cursor.fetchall()}
    # fix the reverse_dist_map since cursor was exhausted
    cursor.execute("SELECT id, name FROM districts")
    reverse_dist_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 3. Aktif tüm LİHKAB'ları çek
    cursor.execute("SELECT id, active_district_id, total_revenue FROM lihkabs WHERE is_active = 1 AND is_deleted = 0")
    all_lihkabs = cursor.fetchall()
    
    if not all_lihkabs:
        conn.close()
        return None, price, 0.0 # Sistemde hiç LİHKAB yoksa
        
    # 4. Genel Ortalama Kazancı hesapla
    avg_revenue = sum(l[2] for l in all_lihkabs) / len(all_lihkabs)
    saturation_limit = avg_revenue + 50000.0 # Yıllık ortalama + 50.000 TL
    
    # Yardımcı Fonksiyon: Bir ilçedeki uygun (doygun olmayan) ve kazancı en düşük LİHKAB'ı bul
    def find_unsaturated_lihkab(d_id):
        candidates = [l for l in all_lihkabs if l[1] == d_id]
        if not candidates:
            return None
        unsaturated = [c for c in candidates if c[2] <= saturation_limit]
        if unsaturated:
            unsaturated.sort(key=lambda x: x[2])
            return unsaturated[0] # Return the full tuple
        return None

    chosen_lihkab = None
    
    # A) Önce işin kendi ilçesine bak
    chosen_lihkab = find_unsaturated_lihkab(district_id)
    
    # B) Eğer kendi ilçesi doygunsa veya LİHKAB yoksa, komşulara bak
    if chosen_lihkab is None:
        neighbors = DISTRICT_PROXIMITY.get(target_dist_name, [])
        for neighbor_name in neighbors:
            n_id = dist_map.get(neighbor_name)
            if n_id:
                chosen_lihkab = find_unsaturated_lihkab(n_id)
                if chosen_lihkab is not None:
                    break
    
    # C) Tüm ilçelerde herkes doygunsa veya doygun olmayan hiç LİHKAB kalmamışsa
    if chosen_lihkab is None:
        own_candidates = [l for l in all_lihkabs if l[1] == district_id]
        if own_candidates:
            own_candidates.sort(key=lambda x: x[2])
            chosen_lihkab = own_candidates[0]
        else:
            neighbors = DISTRICT_PROXIMITY.get(target_dist_name, [])
            for neighbor_name in neighbors:
                n_id = dist_map.get(neighbor_name)
                n_cands = [l for l in all_lihkabs if l[1] == n_id]
                if n_cands:
                    n_cands.sort(key=lambda x: x[2])
                    chosen_lihkab = n_cands[0]
                    break

    params_json = json.dumps(params, ensure_ascii=False)
    transport_price = 0.0
    
    if chosen_lihkab is not None:
        chosen_lihkab_id = chosen_lihkab[0]
        chosen_lihkab_dist_id = chosen_lihkab[1]
        chosen_lihkab_dist_name = reverse_dist_map.get(chosen_lihkab_dist_id)
        
        # Ulaşım Bedeli Hesaplama
        fuel_price = get_fuel_price()
        km_distance = get_distance_km(chosen_lihkab_dist_name, target_dist_name)
        transport_price = max(1000.0, fuel_price * 0.09 * km_distance)
        
        cursor.execute('''
            INSERT INTO jobs (job_name, district_id, lihkab_id, price, transport_price, parameters_json, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (job_name, district_id, chosen_lihkab_id, price, transport_price, params_json, username))
        
        cursor.execute('''
            UPDATE lihkabs 
            SET total_revenue = total_revenue + ?, 
                total_transport_revenue = total_transport_revenue + ? 
            WHERE id = %s
        ''', (price, transport_price, chosen_lihkab_id))
        
        conn.commit()
    else:
        chosen_lihkab_id = None
        
    conn.close()
    
    return chosen_lihkab_id, price, transport_price
def add_lihkab(name, owner, active_district_id, address="", registry_number="", university=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT AVG(total_revenue) FROM lihkabs")
    avg_revenue = cursor.fetchone()[0]
    if avg_revenue is None:
        avg_revenue = 0.0
        
    cursor.execute('''
        INSERT INTO lihkabs (name, owner, active_district_id, total_revenue, address, registry_number, university)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (name, owner, active_district_id, avg_revenue, address, registry_number, university))
    
    conn.commit()
    conn.close()

def update_lihkab(lihkab_id, new_name, new_owner, new_active_district_id, new_address="", new_registry_number="", new_university=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE lihkabs SET name = ?, owner = ?, active_district_id = ?, address = ?, registry_number = ?, university = ?
        WHERE id = %s
    ''', (new_name, new_owner, new_active_district_id, new_address, new_registry_number, new_university, lihkab_id))
    conn.commit()
    conn.close()

def delete_lihkab(lihkab_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE lihkabs SET is_deleted = 1 WHERE id = %s", (lihkab_id,))
    conn.commit()
    conn.close()

def toggle_lihkab_status(lihkab_id, current_status):
    conn = get_connection()
    cursor = conn.cursor()
    new_status = 0 if current_status == 1 else 1
    cursor.execute("UPDATE lihkabs SET is_active = %s WHERE id = %s", (new_status, lihkab_id))
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get job info first
    cursor.execute("SELECT lihkab_id, price FROM jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    
    if job:
        lihkab_id, price = job
        # Delete the job
        cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
        # Reduce the revenue of the LİHKAB
        cursor.execute("UPDATE lihkabs SET total_revenue = total_revenue - %s WHERE id = %s", (price, lihkab_id))
        
    conn.commit()
    conn.close()

def clear_all_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    # Delete all jobs
    cursor.execute("DELETE FROM jobs")
    # Reset all LİHKAB revenues to 0
    cursor.execute("UPDATE lihkabs SET total_revenue = 0")
    
    conn.commit()
    conn.close()

# --- User Auth Functions ---
import bcrypt

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    # If the migration hasn't run yet, we might get an error selecting new columns.
    # We will try to fetch them, fallback if not exist.
    try:
        cursor.execute("SELECT password_hash, can_assign_job, can_add_office, can_manage_office, can_fix_errors FROM users WHERE username = %s AND is_active = 1", (username,))
        row = cursor.fetchone()
    except sqlite3.OperationalError:
        cursor.execute("SELECT password_hash FROM users WHERE username = %s AND is_active = 1", (username,))
        row = cursor.fetchone()
        if row:
            row = (row[0], 0, 0, 0, 0)
            
    conn.close()
    if row:
        stored_hash = row[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return {
                "can_assign_job": bool(row[1]),
                "can_add_office": bool(row[2]),
                "can_manage_office": bool(row[3]),
                "can_fix_errors": bool(row[4])
            }
    return None

def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, is_active, can_assign_job, can_add_office, can_manage_office, can_fix_errors FROM users")
    except sqlite3.OperationalError:
        cursor.execute("SELECT id, username, is_active, 0, 0, 0, 0 FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def add_user_db(username, password, can_assign_job=0, can_add_office=0, can_manage_office=0, can_fix_errors=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False
        
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, can_assign_job, can_add_office, can_manage_office, can_fix_errors) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, hashed, can_assign_job, can_add_office, can_manage_office, can_fix_errors))
    except sqlite3.OperationalError:
        # Fallback if DB not migrated
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
    conn.commit()
    conn.close()
    return True

def delete_user_db(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()

def change_password_db(user_id, new_password):
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id))
    conn.commit()
    conn.close()

def update_user_permissions_db(user_id, can_assign_job, can_add_office, can_manage_office, can_fix_errors):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE users 
            SET can_assign_job = ?, can_add_office = ?, can_manage_office = ?, can_fix_errors = ? 
            WHERE id = %s
        ''', (can_assign_job, can_add_office, can_manage_office, can_fix_errors, user_id))
        conn.commit()
    except sqlite3.OperationalError:
        pass # Ignore if not migrated
    conn.close()
