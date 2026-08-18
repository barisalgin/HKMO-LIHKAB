import psycopg2

SUPABASE_URL = "postgresql://postgres.dmpbiioazwdrutyqxqzq:barisalginHKMO@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"

try:
    conn = psycopg2.connect(SUPABASE_URL)
    print("SUCCESS")
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
