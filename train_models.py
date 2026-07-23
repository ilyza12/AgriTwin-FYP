# train_models.py

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib
import os

def train_anomaly_detector():
    """Train Isolation Forest on 100% synthetic data"""
    
    print("\n" + "="*70)
    print("TRAINING ANOMALY DETECTION MODEL")
    print("="*70)
    
    # Load synthetic data
    df = pd.read_csv('training_data_anomaly_detection.csv')
    
    print(f"\n📊 Dataset Info:")
    print(f"   Total samples: {len(df)}")
    print(f"   Normal: {(df['anomaly'] == 0).sum()}")
    print(f"   Anomalies: {(df['anomaly'] == 1).sum()}")
    print(f"   Contamination rate: {df['anomaly'].mean():.2%}")
    
    # AMENDMENT 1: Updated features to match the generated CSV headers exactly
    features = ['temperature', 'humidity', 'soil_moisture', 
               'ph_level', 'salinity', 'light_intensity']
    
    X = df[features]
    y_true = df['anomaly']
    
    # Train Isolation Forest
    # 🎯 DEFENSE: Unsupervised Anomaly Detection. Isolation Forest was chosen because it excels at finding multi-dimensional outliers (e.g., acceptable heat + acceptable drought = lethal combination) without needing perfectly balanced datasets.
    contamination = y_true.sum() / len(y_true)
    
    print(f"\n⚙️  Training Isolation Forest...")
    print(f"   Contamination: {contamination:.2%}")
    print(f"   Features: {', '.join(features)}")
    
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
        max_samples='auto',
        max_features=1.0,
        bootstrap=False
    )
    
    model.fit(X)
    
    # Evaluate
    predictions = model.predict(X)
    predictions_binary = np.where(predictions == -1, 1, 0)
    
    print(f"\n📈 Model Performance:")
    print(classification_report(y_true, predictions_binary, 
                               target_names=['Normal', 'Anomaly'],
                               digits=3, zero_division=0))
    
    print(f"\n📊 Confusion Matrix:")
    cm = confusion_matrix(y_true, predictions_binary)
    print(f"                Predicted")
    print(f"                Normal  Anomaly")
    print(f"Actual Normal   {cm[0][0]:6d}  {cm[0][1]:7d}")
    if len(cm) > 1:
        print(f"       Anomaly  {cm[1][0]:6d}  {cm[1][1]:7d}")
    
    # Feature importance (approximation using decision path length)
    print(f"\n🔍 Anomaly Detection Stats:")
    anomaly_scores = model.score_samples(X)
    print(f"   Score range: {anomaly_scores.min():.3f} to {anomaly_scores.max():.3f}")
    print(f"   Mean score (normal): {anomaly_scores[y_true == 0].mean():.3f}")
    print(f"   Mean score (anomaly): {anomaly_scores[y_true == 1].mean():.3f}")
    
    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)

    # 🎯 DEFENSE: Model Serialization. Saving the trained model state to a .pkl (pickle) file completely decouples the heavy training phase from the lightweight Flask API, ensuring zero-latency inference for the user.
    joblib.dump(model, 'models/anomaly_detector.pkl')
    print(f"\n✅ Model saved: models/anomaly_detector.pkl")
    
    return model

def train_yield_predictors():
    """Train BOTH Classifier and Regression models for yield prediction"""
    
    print("\n" + "="*70)
    print("TRAINING YIELD PREDICTION MODELS (CLASSIFIER & REGRESSION)")
    print("="*70)
    
    # Load synthetic data
    df = pd.read_csv('training_data_yield_prediction.csv')
    
    print(f"\n📊 Dataset Info:")
    print(f"   Total samples: {len(df)}")
    print(f"   Yield range: {df['fruit_count'].min()}-{df['fruit_count'].max()} fruits")
    
    features = ['avg_temperature', 'avg_humidity', 'avg_soil_moisture', 
                'avg_ph_level', 'avg_salinity', 'avg_light_intensity', 'avg_health_score']
    
    X = df[features]
    
    # Define Targets
    y_class = df['yield_class']
    y_count = df['fruit_count']
    if 'total_weight_g' not in df.columns:
         y_weight = df['fruit_count'] * 15 # Backup if missing
    else:
         y_weight = df['total_weight_g']
    
    # Split data for all three models
    # 🎯 DEFENSE: Cross-Validation standard. An 80/20 train-test split ensures the model is evaluated on unseen data, proving it actually learned the biological physics rather than just memorizing the synthetic CSV.
    X_train_c, X_test_c, y_train_class, y_test_class = train_test_split(X, y_class, test_size=0.2, random_state=42)
    X_train_r, X_test_r, y_train_count, y_test_count = train_test_split(X, y_count, test_size=0.2, random_state=42)
    _, _, y_train_weight, y_test_weight = train_test_split(X, y_weight, test_size=0.2, random_state=42)
    
    # ========== YIELD CLASSIFIER MODEL ==========
    print(f"\n⚙️  Training Yield Classifier (High/Medium/Low)...")
    
    # 🎯 DEFENSE: Non-Linear Modeling. Random Forests were chosen over standard Linear Regression because biological growth is highly non-linear (e.g., too much light becomes toxic). Decision trees handle these biological thresholds perfectly.
    model_class = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model_class.fit(X_train_c, y_train_class)
    pred_class = model_class.predict(X_test_c)
    acc_class = accuracy_score(y_test_class, pred_class)
    
    print(f"\n📈 Classifier Model Performance:")
    print(f"   Accuracy: {acc_class * 100:.2f}%")
    print(classification_report(y_test_class, pred_class, zero_division=0))

    # ========== FRUIT COUNT REGRESSOR MODEL ==========
    print(f"\n⚙️  Training Fruit Count Predictor...")
    
    # 🎯 DEFENSE: Hyperparameter Tuning. Limiting max_depth to 12 and requiring min_samples prevents the Random Forest from overfitting to the synthetic noise, forcing it to learn generalized agronomic rules.
    model_count = RandomForestRegressor(
        n_estimators=100, max_depth=12, min_samples_split=5, min_samples_leaf=2, random_state=42, n_jobs=-1
    )
    model_count.fit(X_train_r, y_train_count)
    pred_count = model_count.predict(X_test_r)
    
    print(f"\n📈 Fruit Count Model Performance:")
    # 🎯 DEFENSE: Metric Selection. R-squared (R²) proves how much of the yield variance is successfully explained by the environmental sensors. Root Mean Square Error (RMSE) gives the error margin in actual physical fruits.
    print(f"   MAE:  {mean_absolute_error(y_test_count, pred_count):.2f} fruits")
    print(f"   RMSE: {np.sqrt(mean_squared_error(y_test_count, pred_count)):.2f} fruits")
    print(f"   R²:   {r2_score(y_test_count, pred_count):.4f}")
    
    # ========== TOTAL WEIGHT REGRESSOR MODEL ==========
    print(f"\n⚙️  Training Total Weight Predictor...")
    
    model_weight = RandomForestRegressor(
        n_estimators=100, max_depth=12, min_samples_split=5, min_samples_leaf=2, random_state=42, n_jobs=-1
    )
    model_weight.fit(X_train_r, y_train_weight)
    pred_weight = model_weight.predict(X_test_r)
    
    print(f"\n📈 Total Weight Model Performance:")
    print(f"   MAE:  {mean_absolute_error(y_test_weight, pred_weight):.1f} grams")
    print(f"   RMSE: {np.sqrt(mean_squared_error(y_test_weight, pred_weight)):.1f} grams")
    print(f"   R²:   {r2_score(y_test_weight, pred_weight):.4f}")
    
    # Feature importance
    print(f"\n🔍 Feature Importance (Fruit Count):")

    # 🎯 DEFENSE: Explainable AI (XAI). Random Forests inherently calculate feature importance. This allows us to prove to agronomists *which* sensor data the AI relies on most heavily to make its predictions.
    importances = model_count.feature_importances_
    for feat, imp in sorted(zip(features, importances), key=lambda x: x[1], reverse=True):
        print(f"   {feat:25s}: {imp:.4f} {'█' * int(imp * 50)}")
    
    # Save models
    os.makedirs('models', exist_ok=True)
    joblib.dump(model_class, 'models/yield_classifier.pkl')
    joblib.dump(model_count, 'models/yield_predictor_count.pkl')
    joblib.dump(model_weight, 'models/yield_predictor_weight.pkl')
    
    print(f"\n✅ Models saved:")
    print(f"   - models/yield_classifier.pkl")
    print(f"   - models/yield_predictor_count.pkl")
    print(f"   - models/yield_predictor_weight.pkl")
    
    return model_class, model_count, model_weight

if __name__ == "__main__":
    print("\n🤖 TRAINING ML MODELS ON 100% SYNTHETIC DATA")
    print("Based on Capsicum annuum research parameters\n")
    
    anomaly_model = train_anomaly_detector()
    yield_models = train_yield_predictors()
    
    print("\n" + "="*70)
    print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
    print("="*70)