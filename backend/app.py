import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes so Vercel can talk to Render
CORS(app)

# Load Models
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
try:
    model = joblib.load(os.path.join(MODEL_DIR, 'xgboost_model.pkl'))
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
    le = joblib.load(os.path.join(MODEL_DIR, 'label_encoder.pkl'))
    models_loaded = True
except Exception as e:
    print(f"Error loading models: {e}")
    models_loaded = False

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "models_loaded": models_loaded})

@app.route('/predict', methods=['POST'])
def predict():
    if not models_loaded:
        return jsonify({"error": "Models not loaded on server."}), 500

    try:
        data = request.json
        print(f"Received data: {data}")

        # Required raw features from frontend
        required_features = ['pH', 'DO', 'Temperature', 'BOD', 'TSS', 'Fecal_Coliform']
        if not all(feature in data for feature in required_features):
            return jsonify({"error": "Missing required features"}), 400

        # Construct DataFrame
        df = pd.DataFrame([data])
        # Force all columns to float to handle string inputs from frontend
        df = df.astype(float)

        # Feature Engineering (must match training pipeline exactly)
        df['DO_Temp_Ratio'] = df['DO'] / df['Temperature']
        df['pH_Deviation'] = abs(df['pH'] - 7.0)

        # Ensure exact column order as training
        features = ['DO', 'BOD', 'TSS', 'pH', 'Temperature', 'Fecal_Coliform', 'DO_Temp_Ratio', 'pH_Deviation']
        X = df[features]

        # Scale features
        X_scaled = scaler.transform(X)

        # Predict using ML model (Running it for the study's sake, but ignoring its output)
        ml_prediction_encoded = model.predict(X_scaled)
        ml_prediction_label = le.inverse_transform(ml_prediction_encoded)[0]

        # Calculate exact mathematical WQI
        denr_standards = {
            "DO":              {"Si": 5.0,   "ideal": 14.6, "weight": 0.1968},
            "BOD":             {"Si": 7.0,   "ideal": 0.0,  "weight": 0.1311},
            "TSS":             {"Si": 80.0,  "ideal": 0.0,  "weight": 0.0656},
            "pH":              {"Si": 9.0,   "ideal": 7.0,  "weight": 0.1311},
            "Temperature":     {"Si": 31.0,  "ideal": 25.0, "weight": 0.0656},
            "Fecal_Coliform":  {"Si": 200.0, "ideal": 0.0,  "weight": 0.4098},
        }

        wqi_sum = 0
        weight_sum = 0
        for param, values in denr_standards.items():
            val = df[param].iloc[0]
            si = values["Si"]
            ideal = values["ideal"]
            weight = values["weight"]
            
            qi = 100 * (abs(val - ideal) / abs(si - ideal))
            wqi_sum += qi * weight
            weight_sum += weight
            
        exact_wqi = wqi_sum / weight_sum

        if exact_wqi <= 25:
            final_class = "Excellent"
        elif exact_wqi <= 50:
            final_class = "Good"
        elif exact_wqi <= 75:
            final_class = "Fair"
        elif exact_wqi <= 100:
            final_class = "Poor"
        else:
            final_class = "High Risk"

        return jsonify({
            "prediction": final_class,
            "engineered_features": {
                "DO_Temp_Ratio": round(float(df['DO_Temp_Ratio'].iloc[0]), 2),
                "pH_Deviation": round(float(df['pH_Deviation'].iloc[0]), 2)
            }
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
