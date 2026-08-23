from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from predictor import predict_crowd, predict_waste, predict_water, predict_energy

app = FastAPI(title="SIH Prediction Service")

class SensorRequest(BaseModel):
    zone_id: int
    event_type: str
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
def home():
    return {"message": "SIH Server is up and running!"}


@app.post("/predict", response_model=SensorResponse)
def predict_universal(req: SensorRequest):
    event = req.event_type.upper()
    if event == "CROWD":
        val, horizon, conf = predict_crowd(req.current_value, req.rate)
    elif event == "WASTE":
        val, horizon, conf = predict_waste(req.current_value, req.rate)
    elif event == "WATER":
        val, horizon, conf = predict_water(req.current_value, req.rate)
    elif event == "ENERGY":
        val, horizon, conf = predict_energy(req.current_value, req.rate)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported event_type: {req.event_type}")

    return {
        "predicted_value": val,
        "confidence": conf,
        "prediction_horizon": horizon,
        "critical": False,
        "generated_at": req.timestamp
    }


@app.post("/predict/crowd", response_model=SensorResponse)
def predict_crowd_endpoint(req: SensorRequest):
    val, horizon, conf = predict_crowd(req.current_value, req.rate)
    return {"predicted_value": val, "confidence": conf, "prediction_horizon": horizon, "critical": False, "generated_at": req.timestamp}


@app.post("/predict/waste", response_model=SensorResponse)
def predict_waste_endpoint(req: SensorRequest):
    val, horizon, conf = predict_waste(req.current_value, req.rate)
    return {"predicted_value": val, "confidence": conf, "prediction_horizon": horizon, "critical": False, "generated_at": req.timestamp}


@app.post("/predict/water", response_model=SensorResponse)
def predict_water_endpoint(req: SensorRequest):
    val, horizon, conf = predict_water(req.current_value, req.rate)
    return {"predicted_value": val, "confidence": conf, "prediction_horizon": horizon, "critical": False, "generated_at": req.timestamp}


@app.post("/predict/energy", response_model=SensorResponse)
def predict_energy_endpoint(req: SensorRequest):
    val, horizon, conf = predict_energy(req.current_value, req.rate)
    return {"predicted_value": val, "confidence": conf, "prediction_horizon": horizon, "critical": False, "generated_at": req.timestamp}
