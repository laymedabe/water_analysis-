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

        # Predict
        prediction_encoded = model.predict(X_scaled)
        prediction_label = le.inverse_transform(prediction_encoded)[0]

        return jsonify({
            "wqi_class": prediction_label,
            "status": "success"
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
