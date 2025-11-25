"""
Train a simple Random Forest model for threat detection.
This creates a basic model for demonstration purposes.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os


def generate_synthetic_data(n_samples=10000):
    """Generate synthetic network traffic data for training."""
    np.random.seed(42)
    
    # Normal traffic (70%)
    n_normal = int(n_samples * 0.7)
    normal_bytes = np.random.normal(5000, 2000, n_normal)
    normal_pkts = np.random.normal(50, 20, n_normal)
    normal_iat = np.random.normal(0.1, 0.05, n_normal)
    normal_labels = np.zeros(n_normal)
    
    # Suspicious traffic (20%)
    n_suspicious = int(n_samples * 0.2)
    suspicious_bytes = np.random.normal(12000, 3000, n_suspicious)
    suspicious_pkts = np.random.normal(120, 30, n_suspicious)
    suspicious_iat = np.random.normal(0.05, 0.02, n_suspicious)
    suspicious_labels = np.ones(n_suspicious) * 0.5
    
    # Malicious traffic (10%)
    n_malicious = n_samples - n_normal - n_suspicious
    malicious_bytes = np.random.normal(20000, 5000, n_malicious)
    malicious_pkts = np.random.normal(200, 50, n_malicious)
    malicious_iat = np.random.normal(0.01, 0.005, n_malicious)
    malicious_labels = np.ones(n_malicious)
    
    # Combine all data
    X = np.vstack([
        np.column_stack([normal_bytes, normal_pkts, normal_iat]),
        np.column_stack([suspicious_bytes, suspicious_pkts, suspicious_iat]),
        np.column_stack([malicious_bytes, malicious_pkts, malicious_iat])
    ])
    
    y = np.concatenate([normal_labels, suspicious_labels, malicious_labels])
    
    # Ensure positive values
    X = np.abs(X)
    
    return X, y


def train_model():
    """Train and save the Random Forest model."""
    print("🛡️  Training Autonomous Cyber Sentinel Detection Model")
    print("=" * 60)
    
    # Generate data
    print("\n📊 Generating synthetic training data...")
    X, y = generate_synthetic_data(n_samples=10000)
    print(f"   Generated {len(X)} samples")
    print(f"   Features: bytes, packets, inter-arrival time")
    print(f"   Classes: 0=normal, 0.5=suspicious, 1=malicious")
    
    # Split data
    print("\n✂️  Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    print("\n🎓 Training Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("   ✓ Training complete")
    
    # Evaluate
    print("\n📈 Evaluating model performance...")
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"   Training accuracy: {train_score:.2%}")
    print(f"   Testing accuracy:  {test_score:.2%}")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Convert to binary for classification report
    y_test_binary = (y_test >= 0.5).astype(int)
    y_pred_binary = (y_pred >= 0.5).astype(int)
    
    print("\n📊 Classification Report:")
    print(classification_report(
        y_test_binary, 
        y_pred_binary,
        target_names=['Normal', 'Threat']
    ))
    
    print("\n🎯 Confusion Matrix:")
    cm = confusion_matrix(y_test_binary, y_pred_binary)
    print(f"   True Negatives:  {cm[0][0]}")
    print(f"   False Positives: {cm[0][1]}")
    print(f"   False Negatives: {cm[1][0]}")
    print(f"   True Positives:  {cm[1][1]}")
    
    # Feature importance
    print("\n🔍 Feature Importance:")
    features = ['bytes', 'packets', 'iat_avg']
    for feat, imp in zip(features, model.feature_importances_):
        print(f"   {feat:12s}: {imp:.3f}")
    
    # Save model
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "threat_detector.joblib")
    
    print(f"\n💾 Saving model to {model_path}...")
    joblib.dump(model, model_path)
    print("   ✓ Model saved successfully")
    
    # Update settings
    print("\n⚙️  To use this model, update your .env or settings.yml:")
    print(f"   MODEL_PATH={model_path}")
    
    print("\n✅ Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    train_model()
