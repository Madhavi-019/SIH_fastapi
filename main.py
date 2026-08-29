from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from predictor import predict_crowd, predict_waste, predict_water, predict_energy

app = FastAPI(title="SIH ML Prediction Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Critical thresholds for each metric
THRESHOLDS = {
    "CROWD": 300.0,   # Crowd count > 300 triggers critical
    "WASTE": 80.0,    # Fill percentage > 80% triggers critical
    "WATER": 85.0,    # Usage / tank level % > 85% triggers critical
    "ENERGY": 400.0   # kWh / power load > 400 triggers critical
}

def is_metric_critical(event_type: str, predicted_val: float) -> bool:
    limit = THRESHOLDS.get(event_type.upper(), 100.0)
    return bool(predicted_val >= limit)

class SensorRequest(BaseModel):
    zone_id: int = 1
    event_type: str = "CROWD"
    current_value: float
    rate: float
    timestamp: int

class SensorResponse(BaseModel):
    predicted_value: float
    confidence: float
    prediction_horizon: int
    critical: bool
    generated_at: int

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is healthy"}

@app.get("/")
def root():
    return {"status": "ok", "message": "SIH FastAPI ML service running"}

@app.post("/predict", response_model=SensorResponse)
def predict_universal(req: SensorRequest):
    etype = req.event_type.upper()
    if etype == "CROWD":
        val, horizon, conf = predict_crowd(req.current_value, req.rate)
    elif etype == "WASTE":
        val, horizon, conf = predict_waste(req.current_value, req.rate)
    elif etype == "WATER":
        val, horizon, conf = predict_water(req.current_value, req.rate)
    elif etype == "ENERGY":
        val, horizon, conf = predict_energy(req.current_value, req.rate)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported event_type: {req.event_type}")

    return {
        "predicted_value": round(val, 2),
        "confidence": round(conf, 2),
        "prediction_horizon": horizon,
        "critical": is_metric_critical(etype, val),
        "generated_at": req.timestamp
    }

@app.post("/predict/crowd", response_model=SensorResponse)
def predict_crowd_endpoint(req: SensorRequest):
    val, horizon, conf = predict_crowd(req.current_value, req.rate)
    return {
        "predicted_value": round(val, 2),
        "confidence": round(conf, 2),
        "prediction_horizon": horizon,
        "critical": is_metric_critical("CROWD", val),
        "generated_at": req.timestamp
    }

@app.post("/predict/waste", response_model=SensorResponse)
def predict_waste_endpoint(req: SensorRequest):
    val, horizon, conf = predict_waste(req.current_value, req.rate)
    return {
        "predicted_value": round(val, 2),
        "confidence": round(conf, 2),
        "prediction_horizon": horizon,
        "critical": is_metric_critical("WASTE", val),
        "generated_at": req.timestamp
    }

@app.post("/predict/water", response_model=SensorResponse)
def predict_water_endpoint(req: SensorRequest):
    val, horizon, conf = predict_water(req.current_value, req.rate)
    return {
        "predicted_value": round(val, 2),
        "confidence": round(conf, 2),
        "prediction_horizon": horizon,
        "critical": is_metric_critical("WATER", val),
        "generated_at": req.timestamp
    }

@app.post("/predict/energy", response_model=SensorResponse)
def predict_energy_endpoint(req: SensorRequest):
    val, horizon, conf = predict_energy(req.current_value, req.rate)
    return {
        "predicted_value": round(val, 2),
        "confidence": round(conf, 2),
        "prediction_horizon": horizon,
        "critical": is_metric_critical("ENERGY", val),
        "generated_at": req.timestamp
    }
