import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

candidate_tables = [
    "sensor_data",
    "sensor_readings",
    "sensors",
    "zone_states",
    "readings",
    "events",
    "zones"
]

for tbl in candidate_tables:
    try:
        res = supabase.table(tbl).select("*").limit(1).execute()
        print(f"Found table: '{tbl}' with {len(res.data)} sample rows!")
    except Exception as e:
        print(f"Table '{tbl}' not found.")
