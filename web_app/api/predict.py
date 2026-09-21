from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
import math

# DENR DAO 2016-08 Standards for WQI Computation (Class C Baseline)
DENR_STANDARDS = {
    "DO":              {"Si": 5.0,   "ideal": 14.6, "unit": "mg/L",     "weight": 0.1968},
    "BOD":             {"Si": 7.0,   "ideal": 0.0,  "unit": "mg/L",     "weight": 0.1311},
    "TSS":             {"Si": 80.0,  "ideal": 0.0,  "unit": "mg/L",     "weight": 0.0656},
    "pH":              {"Si": 9.0,   "ideal": 7.0,  "unit": "",         "weight": 0.1311},
    "Temperature":     {"Si": 31.0,  "ideal": 25.0, "unit": "C",        "weight": 0.0656},
    "Fecal_Coliform":  {"Si": 200.0, "ideal": 0.0,  "unit": "MPN/100mL","weight": 0.4098},
}

def compute_quality_rating(value, param):
    std = DENR_STANDARDS[param]
    si = std["Si"]
    ideal = std["ideal"]
    if si == ideal: return 0
    qi = ((value - ideal) / (si - ideal)) * 100
    return max(qi, 0)

def compute_wqi(row):
    numerator = 0
    denominator = 0
    for param in ["DO", "BOD", "TSS", "pH", "Temperature", "Fecal_Coliform"]:
        value = row[param]
        if value is None or math.isnan(value): continue
        qi = compute_quality_rating(value, param)
        wi = DENR_STANDARDS[param]["weight"]
        numerator += qi * wi
        denominator += wi
    return numerator / denominator if denominator != 0 else float('nan')

app = Flask(__name__)

# Load models on startup
# In Vercel, the working directory is usually the project root (web_app/)
try:
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    model = joblib.load(os.path.join(model_dir, 'mlp_model.pkl'))
    scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
    
    le_path = os.path.join(model_dir, 'label_encoder.pkl')
    if os.path.exists(le_path):
        label_encoder = joblib.load(le_path)
    else:
        label_encoder = None
except Exception as e:
    model = None
    scaler = None
    label_encoder = None
    print(f"Error loading models: {e}")

@app.route('/api/predict', methods=['POST'])
def predict():
    if model is None or scaler is None:
        return jsonify({'error': 'Models not loaded properly.'}), 500
        
    try:
        data = request.json
        # Expected input: pH, Temperature, DO, BOD, TSS, Fecal_Coliform
        pH = float(data.get('pH', 7.0))
        temp = float(data.get('Temperature', 25.0))
        do = float(data.get('DO', 5.0))
        bod = float(data.get('BOD', 2.0))
        tss = float(data.get('TSS', 10.0))
        fecal = float(data.get('Fecal_Coliform', 100.0))
        
        # Feature Engineering (must match wqi_pipeline.py EXACTLY)
        do_temp_ratio = do / temp if temp != 0 else 0
        ph_dev = abs(pH - 7.0)
        
        # Order must match exactly the training features:
        # ['pH', 'Temperature', 'DO', 'BOD', 'TSS', 'Fecal_Coliform', 'DO_Temp_Ratio', 'pH_Deviation']
        features = [[pH, temp, do, bod, tss, fecal, do_temp_ratio, ph_dev]]
        
        # Scale features
        scaled_features = scaler.transform(features)
        
        # Calculate analytical WQI first
        analytical_wqi = compute_wqi({
            "DO": do, "BOD": bod, "TSS": tss, 
            "pH": pH, "Temperature": temp, "Fecal_Coliform": fecal
        })
        
        # ML Out-of-Distribution Fallback Logic:
        # The ML model was exclusively trained on polluted data (Poor, Very Poor, High Risk)
        # It literally does not have classes for Excellent or Good.
        if analytical_wqi <= 50:
            prediction = "Excellent" if analytical_wqi <= 25 else "Good"
            probabilities = {prediction: 100.0}
        else:
            # Predict using MLP
            raw_pred = model.predict(scaled_features)[0]
            
            if label_encoder is not None:
                prediction = str(label_encoder.inverse_transform([raw_pred])[0])
            else:
                prediction = str(raw_pred)
            
            # Also get probabilities if possible
            probabilities = None
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(scaled_features)[0]
                classes = model.classes_
                if label_encoder is not None:
                    classes = label_encoder.inverse_transform(classes)
                probabilities = {str(cls): round(float(prob) * 100, 2) for cls, prob in zip(classes, probs)}
            
        return jsonify({
            'prediction': prediction,
            'probabilities': probabilities,
            'engineered_features': {
                'DO_Temp_Ratio': round(float(do_temp_ratio), 4),
                'pH_Deviation': round(float(ph_dev), 4),
                'Analytical_WQI': round(float(analytical_wqi), 2)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Vercel needs the app variable exported
# but just having it in index.py or predict.py is enough.
