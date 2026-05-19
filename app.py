from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import random
from model import train_model, generate_sample_data

app = FastAPI(title="Predictive Maintenance Agent")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Data models
class SensorData(BaseModel):
    temperature: float
    vibration: float
    pressure: float
    rotation_speed: float
    tool_wear: float

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    status: str
    timestamp: str

# Global variables
MODEL_FILE = "model.pkl"
DATA_FILE = "sensor_data.csv"
model = None
data_file = DATA_FILE

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    global model, data_file
    
    # Generate sample data if it doesn't exist
    if not os.path.exists(DATA_FILE):
        generate_sample_data(DATA_FILE, 1000)
    
    # Train or load model
    if os.path.exists(MODEL_FILE):
        model = joblib.load(MODEL_FILE)
        print("✅ Model loaded successfully")
    else:
        model = train_model(DATA_FILE, MODEL_FILE)
        print("✅ Model trained and saved successfully")

@app.get("/")
async def read_index():
    return FileResponse("templates/index.html")

@app.post("/predict", response_model=PredictionResponse)
async def predict(sensor_data: SensorData):
    """Predict machine status based on sensor data"""
    global model
    
    try:
        # Prepare features for prediction
        features = np.array([[
            sensor_data.temperature,
            sensor_data.vibration,
            sensor_data.pressure,
            sensor_data.rotation_speed,
            sensor_data.tool_wear
        ]])
        
        # Make prediction
        prediction_proba = model.predict_proba(features)[0]
        prediction = model.predict(features)[0]
        
        # Map prediction to status
        status_map = {0: "Normal", 1: "Warning", 2: "Failure Risk"}
        status = status_map.get(prediction, "Unknown")
        
        # Get confidence score
        confidence = float(max(prediction_proba))
        
        # Log high-risk predictions
        if status == "Failure Risk" and confidence > 0.7:
            print(f"⚠️ ALERT: Machine maintenance required! Confidence: {confidence:.2f}")
        
        return PredictionResponse(
            prediction=status,
            confidence=confidence,
            status=status,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/train")
async def train():
    """Retrain the model"""
    global model
    
    try:
        model = train_model(DATA_FILE, MODEL_FILE)
        return {"message": "Model retrained successfully", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@app.get("/sensor-data")
async def get_sensor_data():
    """Get latest sensor data for visualization"""
    # Generate simulated real-time data
    data = {
        "temperature": round(random.uniform(60, 95), 2),
        "vibration": round(random.uniform(2, 8), 2),
        "pressure": round(random.uniform(80, 120), 2),
        "rotation_speed": round(random.uniform(2000, 3000), 2),
        "tool_wear": round(random.uniform(0, 200), 2),
        "timestamp": datetime.now().isoformat()
    }
    return data

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)