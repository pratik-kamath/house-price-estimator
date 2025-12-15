
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '../models')
INPUT_FILE = os.path.join(DATA_DIR, 'training_data.parquet')

os.makedirs(MODELS_DIR, exist_ok=True)

def main():
    print(f"Loading training data from {INPUT_FILE}...")
    if not os.path.exists(INPUT_FILE):
        print("Training data not found. Please run clean_data.py first.")
        return

    df = pd.read_parquet(INPUT_FILE)
    
    # --- Feature Engineering ---
    # CatBoost handles Categorical features natively.
    # We just need to ensure they are Strings (and fill NaNs).
    
    cat_features = ['Suburb', 'PropertyType', 'Postcode', 'DistrictCode', 'Zoning']
    
    # Ensure categorical columns are strings
    for col in cat_features:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna("MISSING")
            
    # Select Features
    # Dropping non-predictive or redundant columns
    drop_cols = ['PurchasePrice', 'PropertyID', 'ValuationNum', 'HouseNumber', 'StreetName', 'SourceFile', 'FullAddress', 'ContractDate', 'AreaUnit']
    
    X = df.drop(columns=drop_cols, errors='ignore')
    y = df['PurchasePrice']
    
    print(f"Features: {X.columns.tolist()}")
    
    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training on {len(X_train):,} samples, Validating on {len(X_test):,} samples.")
    
    # Identify indices of categorical features for CatBoost
    cat_indices = [i for i, col in enumerate(X.columns) if col in cat_features]
    
    # --- Model Training ---
    print("Training CatBoost Regressor...")
    model = CatBoostRegressor(
        iterations=1000,
        learning_rate=0.1,
        depth=6,
        loss_function='RMSE',
        eval_metric='MAE',
        random_seed=42,
        early_stopping_rounds=50,
        allow_writing_files=False
    )
    
    model.fit(
        X_train, y_train,
        cat_features=cat_indices,
        eval_set=(X_test, y_test),
        verbose=100
    )
    
    # --- Evaluation ---
    print("\n--- Evaluation on Test Set ---")
    predictions = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    
    print(f"MAE:  ${mae:,.2f}")
    print(f"RMSE: ${rmse:,.2f}")
    print(f"R2:   {r2:.4f}")
    
    # --- Save Artifacts ---
    model_path = os.path.join(MODELS_DIR, 'catboost_model.cbm')
    print(f"\nSaving model to {model_path}...")
    model.save_model(model_path)
    print("Training Complete.")

if __name__ == "__main__":
    main()
