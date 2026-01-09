import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def train_and_save_model():
    print("Loading dataset...")
    df = pd.read_csv('data/mindx test dataset.csv')

    # Define columns
    categorical_cols = ['ship_type', 'route_id', 'month', 'fuel_type', 'weather_conditions']
    numerical_cols = ['distance', 'fuel_consumption', 'engine_efficiency']
    target_col = 'CO2_emissions'

    print("Preprocessing data...")
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col + '_encoded'] = le.fit_transform(df[col])
        label_encoders[col] = le

    # Define feature columns
    feature_cols = numerical_cols + [col + '_encoded' for col in categorical_cols]

    X = df[feature_cols]
    y = df[target_col]

    print("Training Random Forest model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Create models directory
    os.makedirs('models', exist_ok=True)

    print("Saving artifacts...")
    joblib.dump(model, 'models/co2_emission_model.pkl')
    joblib.dump(label_encoders, 'models/label_encoders.pkl')
    joblib.dump(feature_cols, 'models/feature_columns.pkl')
    # No scaler needed for Random Forest, but ComplianceEngine expects it or None
    # Creating a dummy or skipping based on ComplianceEngine logic (it handles None)
    # Based on ComplianceEngine.py line 27: self.scaler = joblib.load(scaler_path) if scaler_path else None
    # However, it might error if we don't provide a path at all in the constructor but it's hardcoded.
    # Constructor: def __init__(self, model_path='models/co2_emission_model.pkl', scaler_path='models/scaler.pkl', ...)
    # If scaler.pkl doesn't exist, it prints a warning and sets model_loaded = False.
    # To be safe, I'll save None or a dummy if Linear Regression wasn't used, 
    # but ComplianceEngine.py line 31: except FileNotFoundError: self.model_loaded = False
    # So I MUST provide something for scaler.pkl if I want model_loaded to be True.
    # Actually, ComplianceEngine.py line 27: self.scaler = joblib.load(scaler_path) if scaler_path else None
    # If I pass scaler_path=None it works, but it's hardcoded in the constructor.
    # Let me check ComplianceEngine.py again.
    
    # Line 20: def __init__(self, model_path: str = 'models/co2_emission_model.pkl',
    #              scaler_path: str = 'models/scaler.pkl',
    # ...
    # Line 25: try:
    #             self.model = joblib.load(model_path)
    #             self.scaler = joblib.load(scaler_path) if scaler_path else None
    
    # If scaler_path is 'models/scaler.pkl' and it doesn't exist, joblib.load will fail and go to except.
    # To avoid this, I'll just save a None value to models/scaler.pkl.
    joblib.dump(None, 'models/scaler.pkl')

    print("Model training complete and artifacts saved!")

if __name__ == "__main__":
    train_and_save_model()
