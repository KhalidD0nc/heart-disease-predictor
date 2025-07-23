from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Simplified prediction without heavy ML dependencies
def simple_heart_prediction(data):
    """Lightweight prediction algorithm"""
    risk_score = 0
    risk_factors = []
    
    # Age factor
    age = float(data.get('age', 0))
    if age > 65:
        risk_score += 15
        risk_factors.append("Advanced age")
    elif age > 50:
        risk_score += 8
    
    # Sex factor
    if float(data.get('sex', 0)) == 1:
        risk_score += 5
    
    # Chest pain type
    cp = float(data.get('cp', 0))
    if cp == 0:
        risk_score += 20
        risk_factors.append("Typical angina symptoms")
    elif cp == 1:
        risk_score += 10
        risk_factors.append("Atypical chest pain")
    
    # Blood pressure
    trestbps = float(data.get('trestbps', 0))
    if trestbps > 140:
        risk_score += 15
        risk_factors.append("High blood pressure")
    elif trestbps > 130:
        risk_score += 8
    
    # Cholesterol
    chol = float(data.get('chol', 0))
    if chol > 240:
        risk_score += 15
        risk_factors.append("High cholesterol")
    elif chol > 200:
        risk_score += 8
    
    # Other factors
    if float(data.get('fbs', 0)) == 1:
        risk_score += 10
        risk_factors.append("Elevated fasting blood sugar")
    
    if float(data.get('exang', 0)) == 1:
        risk_score += 15
        risk_factors.append("Exercise-induced chest pain")
    
    if float(data.get('oldpeak', 0)) > 2:
        risk_score += 15
        risk_factors.append("Significant ST depression")
    
    ca = float(data.get('ca', 0))
    if ca > 0:
        risk_score += ca * 10
        risk_factors.append(f"{int(ca)} major vessel(s) with narrowing")
    
    return {
        'riskScore': min(risk_score, 100),
        'hasHeartDisease': risk_score > 50,
        'riskFactors': risk_factors,
        'modelUsed': False
    }

@app.route('/')
def index():
    try:
        with open('index.html', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "index.html not found", 404

@app.route('/style.css')
def style():
    try:
        with open('style.css', 'r') as file:
            return file.read(), 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        return "style.css not found", 404

@app.route('/script.js')
def script():
    try:
        with open('script.js', 'r') as file:
            return file.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "script.js not found", 404

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        prediction = simple_heart_prediction(data)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'riskScore': 50,
            'hasHeartDisease': False,
            'riskFactors': ['Error occurred during prediction']
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
