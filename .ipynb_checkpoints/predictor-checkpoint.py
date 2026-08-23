def predict_crowd(current_value: float, rate: float):
    horizon_min = 30
    horizon_sec = horizon_min * 60  # 1800 seconds
    predicted_value = current_value + (rate * horizon_min)
    confidence = 0.90
    return round(float(predicted_value), 2), horizon_sec, confidence


def predict_waste(current_value: float, rate: float):
    if rate <= 0:
        return 100.0, 0, 0.50
    
    minutes_to_full = max(0.0, (100.0 - current_value) / rate)
    horizon_sec = int(round(minutes_to_full * 60))
    return 100.0, horizon_sec, 0.90


def predict_water(current_value: float, rate: float):
    horizon_min = 60
    horizon_sec = horizon_min * 60  # 3600 seconds
    predicted_value = max(0.0, current_value - (rate * horizon_min))
    confidence = 0.75
    return round(float(predicted_value), 2), horizon_sec, confidence


def predict_energy(current_value: float, rate: float):
    horizon_min = 30
    horizon_sec = horizon_min * 60  # 1800 seconds
    predicted_value = current_value + (rate * horizon_min)
    confidence = 0.75
    return round(float(predicted_value), 2), horizon_sec, confidence