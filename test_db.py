import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

print(f"Connecting to Supabase at: {url}")
try:
    supabase = create_client(url, key)
    res = supabase.table("zone_state").select("*").limit(5).execute()
    print("Database connection successful!")
    print(f"Retrieved {len(res.data)} records from zone_state:")
    for row in res.data:
        print(row)
except Exception as e:
    print(f"Error querying table: {e}")
