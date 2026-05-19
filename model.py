import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import random
from datetime import datetime, timedelta

def generate_sample_data(filename, num_samples=1000):
    """Generate synthetic sensor data for predictive maintenance"""
    
    data = []
    start_time = datetime.now() - timedelta(days=30)
    
    for i in range(num_samples):
        # Base values
        temperature = random.uniform(60, 95)
        vibration = random.uniform(2, 8)
        pressure = random.uniform(80, 120)
        rotation_speed = random.uniform(2000, 3000)
        tool_wear = random.uniform(0, 200)
        
        # Introduce failure patterns
        failure_risk = 0  # 0: Normal, 1: Warning, 2: Failure Risk
        
        # Failure condition 1: High temperature + high vibration
        if temperature > 85 and vibration > 6:
            failure_risk = 2
        # Warning condition 1: High temperature OR high vibration
        elif temperature > 80 or vibration > 5:
            failure_risk = 1
        # Failure condition 2: Low pressure + high rotation speed
        elif pressure < 85 and rotation_speed > 2800:
            failure_risk = 2
        # Warning condition 2: High tool wear
        elif tool_wear > 150:
            failure_risk = 1
        # Failure condition 3: Multiple warning signs
        elif (temperature > 75 and vibration > 4.5 and tool_wear > 120):
            failure_risk = 2
        
        # Add some randomness
        if random.random() < 0.05:  # 5% chance of random failure
            failure_risk = 2
        elif random.random() < 0.1:  # 10% chance of random warning
            failure_risk = 1
        
        timestamp = start_time + timedelta(hours=i)
        
        data.append({
            'timestamp': timestamp,
            'temperature': round(temperature, 2),
            'vibration': round(vibration, 2),
            'pressure': round(pressure, 2),
            'rotation_speed': round(rotation_speed, 2),
            'tool_wear': round(tool_wear, 2),
            'failure_risk': failure_risk
        })
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"✅ Generated {num_samples} sample records in {filename}")
    return df

def train_model(data_file, model_file):
    """Train the predictive maintenance model"""
    
    # Load data
    df = pd.read_csv(data_file)
    
    # Prepare features and target
    features = ['temperature', 'vibration', 'pressure', 'rotation_speed', 'tool_wear']
    X = df[features]
    y = df['failure_risk']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✅ Model trained with accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                              target_names=['Normal', 'Warning', 'Failure Risk']))
    
    # Save model
    joblib.dump(model, model_file)
    print(f"✅ Model saved as {model_file}")
    
    return model

if __name__ == "__main__":
    # Generate sample data and train model
    generate_sample_data("sensor_data.csv", 1500)
    train_model("sensor_data.csv", "model.pkl")