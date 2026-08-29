import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception as e:
        print(f"Supabase init error: {e}")

CSV_PATH = "sensor_data_rows (3).csv"
df_local = None
if os.path.exists(CSV_PATH):
    try:
        df_local = pd.read_csv(CSV_PATH)
        if "timestamp" in df_local.columns:
            df_local["timestamp"] = pd.to_datetime(df_local["timestamp"])
    except Exception as e:
        print(f"Local CSV loading error: {e}")


def get_live_slope(event_type: str, fallback_rate: float) -> tuple[float, float]:
    """
    1. Try live Supabase sensor_data table.
    2. Fallback to local CSV if table is empty.
    3. Fallback to request rate.
    """
    if supabase:
        try:
            res = (
                supabase.table("sensor_data")
                .select("value, timestamp")
                .eq("sensor_type", event_type.upper())
                .order("timestamp", desc=True)
                .limit(20)
                .execute()
            )
            records = res.data
            if records and len(records) >= 2:
                values = [float(r["value"]) for r in reversed(records)]
                count = len(values)
                calculated_slope = abs(values[-1] - values[0]) / max(1, count)
                confidence = min(0.95, round(0.70 + (count * 0.0125), 2))
                effective_rate = calculated_slope if calculated_slope > 0 else fallback_rate
                return effective_rate, confidence
        except Exception as e:
            print(f"Supabase query error: {e}")

    if df_local is not None and not df_local.empty:
        try:
            subset = df_local[df_local["sensor_type"].str.upper() == event_type.upper()]
            subset = subset.sort_values(by="timestamp").tail(20)
            if len(subset) >= 2:
                values = subset["value"].astype(float).values
                count = len(values)
                calculated_slope = abs(values[-1] - values[0]) / max(1, count)
                confidence = min(0.95, round(0.70 + (count * 0.0125), 2))
                effective_rate = calculated_slope if calculated_slope > 0 else fallback_rate
                return effective_rate, confidence
        except Exception as e:
            print(f"Local CSV slope calculation error: {e}")

    return float(fallback_rate), 0.70


def predict_crowd(current_value: float, rate: float):
    eff_rate, conf = get_live_slope("CROWD", rate)
    horizon_min = 30
    horizon_sec = horizon_min * 60
    predicted_val = current_value + (eff_rate * horizon_min)
    return round(float(predicted_val), 2), horizon_sec, conf


def predict_waste(current_value: float, rate: float):
    eff_rate, conf = get_live_slope("WASTE", rate)
    horizon_min = 30
    horizon_sec = horizon_min * 60
    predicted_val = min(100.0, current_value + (eff_rate * horizon_min))
    return round(float(predicted_val), 2), horizon_sec, conf


def predict_water(current_value: float, rate: float):
    eff_rate, conf = get_live_slope("WATER", rate)
    horizon_min = 60
    horizon_sec = horizon_min * 60
    predicted_val = max(0.0, current_value - (eff_rate * horizon_min))
    return round(float(predicted_val), 2), horizon_sec, conf


def predict_energy(current_value: float, rate: float):
    eff_rate, conf = get_live_slope("ENERGY", rate)
    horizon_min = 30
    horizon_sec = horizon_min * 60
    predicted_val = current_value + (eff_rate * horizon_min)
    return round(float(predicted_val), 2), horizon_sec, conf
