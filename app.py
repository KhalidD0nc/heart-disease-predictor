from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all domains on all routes

# Load the model
try:
    with open('model.pkl', 'rb') as file:
        model = pickle.load(file)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        with open('index.html', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "index.html not found", 404

@app.route('/style.css')
def style():
    """Serve the CSS file"""
    try:
        with open('style.css', 'r') as file:
            return file.read(), 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        return "style.css not found", 404

@app.route('/script.js')
def script():
    """Serve the JavaScript file"""
    try:
        with open('script.js', 'r') as file:
            return file.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "script.js not found", 404

@app.route('/predict', methods=['POST'])
def predict():
    """Handle heart disease prediction"""
    try:
        if model is None:
            return jsonify({
                'error': 'Model not loaded',
                'riskScore': 50,
                'hasHeartDisease': False,
                'riskFactors': ['Model unavailable - using simulated results']
            }), 500
        
        # Get data from request
        data = request.json
        
        # Feature names (adjust based on your model's expected features)
        feature_names = [
            'age', 'sex', 'cp', 'trestbps', 'chol', 
            'fbs', 'restecg', 'thalach', 'exang', 
            'oldpeak', 'slope', 'ca', 'thal'
        ]
        
        # Extract features in the correct order
        features = []
        for feature in feature_names:
            if feature in data:
                features.append(float(data[feature]))
            else:
                return jsonify({'error': f'Missing feature: {feature}'}), 400
        
        # Convert to numpy array and reshape for prediction
        X = np.array(features).reshape(1, -1)
        
        # Make prediction
        try:
            # Try to get probability if available
            if hasattr(model, 'predict_proba'):
                probability = model.predict_proba(X)[0]
                risk_score = int(probability[1] * 100)  # Probability of having heart disease
                has_heart_disease = probability[1] > 0.5
            else:
                # Fallback to binary prediction
                prediction = model.predict(X)[0]
                has_heart_disease = bool(prediction)
                risk_score = 75 if has_heart_disease else 25
        except Exception as e:
            print(f"Prediction error: {e}")
            # Fallback to simple heuristic
            risk_score = calculate_risk_heuristic(data)
            has_heart_disease = risk_score > 50
        
        # Generate risk factors based on input
        risk_factors = generate_risk_factors(data)
        
        return jsonify({
            'riskScore': risk_score,
            'hasHeartDisease': has_heart_disease,
            'riskFactors': risk_factors,
            'modelUsed': True
        })
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return jsonify({
            'error': str(e),
            'riskScore': 50,
            'hasHeartDisease': False,
            'riskFactors': ['Error occurred during prediction']
        }), 500

def calculate_risk_heuristic(data):
    """Fallback heuristic for risk calculation"""
    risk_score = 0
    
    # Age factor
    age = float(data.get('age', 0))
    if age > 65:
        risk_score += 15
    elif age > 50:
        risk_score += 8
    
    # Sex factor (males generally higher risk)
    if float(data.get('sex', 0)) == 1:
        risk_score += 5
    
    # Chest pain type
    cp = float(data.get('cp', 0))
    if cp == 0:
        risk_score += 20
    elif cp == 1:
        risk_score += 10
    
    # Blood pressure
    trestbps = float(data.get('trestbps', 0))
    if trestbps > 140:
        risk_score += 15
    elif trestbps > 130:
        risk_score += 8
    
    # Cholesterol
    chol = float(data.get('chol', 0))
    if chol > 240:
        risk_score += 15
    elif chol > 200:
        risk_score += 8
    
    # Other factors
    if float(data.get('fbs', 0)) == 1:
        risk_score += 10
    
    if float(data.get('exang', 0)) == 1:
        risk_score += 15
    
    if float(data.get('oldpeak', 0)) > 2:
        risk_score += 15
    elif float(data.get('oldpeak', 0)) > 1:
        risk_score += 8
    
    ca = float(data.get('ca', 0))
    if ca > 0:
        risk_score += ca * 10
    
    return min(risk_score, 100)

def generate_risk_factors(data):
    """Generate list of risk factors based on input data"""
    risk_factors = []
    
    age = float(data.get('age', 0))
    if age > 65:
        risk_factors.append("Advanced age")
    elif age > 50:
        risk_factors.append("Middle age")
    
    if float(data.get('cp', 0)) == 0:
        risk_factors.append("Typical angina symptoms")
    elif float(data.get('cp', 0)) == 1:
        risk_factors.append("Atypical chest pain")
    
    if float(data.get('trestbps', 0)) > 140:
        risk_factors.append("High blood pressure")
    
    if float(data.get('chol', 0)) > 240:
        risk_factors.append("High cholesterol")
    
    if float(data.get('fbs', 0)) == 1:
        risk_factors.append("Elevated fasting blood sugar")
    
    if float(data.get('restecg', 0)) == 1:
        risk_factors.append("ECG abnormalities")
    elif float(data.get('restecg', 0)) == 2:
        risk_factors.append("Left ventricular hypertrophy")
    
    if float(data.get('thalach', 0)) < 100:
        risk_factors.append("Low maximum heart rate")
    
    if float(data.get('exang', 0)) == 1:
        risk_factors.append("Exercise-induced chest pain")
    
    if float(data.get('oldpeak', 0)) > 2:
        risk_factors.append("Significant ST depression")
    
    if float(data.get('slope', 0)) == 2:
        risk_factors.append("Downsloping ST segment")
    
    ca = float(data.get('ca', 0))
    if ca > 0:
        risk_factors.append(f"{int(ca)} major vessel(s) with narrowing")
    
    thal = float(data.get('thal', 0))
    if thal == 1:
        risk_factors.append("Fixed perfusion defect")
    elif thal == 2:
        risk_factors.append("Reversible perfusion defect")
    
    return risk_factors

@app.route('/model-info')
def model_info():
    """Get information about the loaded model"""
    if model is None:
        return jsonify({'error': 'Model not loaded'})
    
    try:
        model_type = type(model).__name__
        has_proba = hasattr(model, 'predict_proba')
        
        # Try to get feature names if available
        feature_names = []
        if hasattr(model, 'feature_names_in_'):
            feature_names = model.feature_names_in_.tolist()
        
        return jsonify({
            'model_type': model_type,
            'has_probability': has_proba,
            'feature_names': feature_names,
            'status': 'loaded'
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("Starting Heart Health Predictor Server...")
    print("Model status:", "Loaded" if model else "Not loaded")
    app.run(debug=True, host='0.0.0.0', port=8080)
