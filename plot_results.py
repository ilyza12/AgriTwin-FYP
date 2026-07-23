import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# 1. Load your generated data
print("Loading synthetic yield data...")
df = pd.read_csv('training_data_yield_prediction.csv')

# 2. Separate Features (X) and Target (y)
X = df[['avg_temperature', 'avg_humidity', 'avg_soil_moisture', 'avg_ph_level', 'avg_salinity', 'avg_light_intensity']]
y = df['yield_class']

# 3. Split into Training and Testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train the Random Forest
print("Training Random Forest Classifier...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# 5. Make predictions and calculate Accuracy
predictions = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"\n✅ Model Accuracy: {accuracy * 100:.2f}%")

# 6. Generate the Confusion Matrix Graphic
cm = confusion_matrix(y_test, predictions, labels=['High', 'Medium', 'Low'])

plt.figure(figsize=(8, 6))
# Create a beautiful heatmap (Blues color scheme looks highly professional)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['High', 'Medium', 'Low'], 
            yticklabels=['High', 'Medium', 'Low'],
            annot_kws={"size": 14}) # Make numbers big enough for a slide

plt.title(f'Random Forest Yield Prediction\nAccuracy: {accuracy * 100:.2f}%', fontsize=16, pad=15)
plt.ylabel('Actual Yield Class', fontsize=12)
plt.xlabel('Predicted Yield Class', fontsize=12)

# Save the image for your slides!
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=300)
print("📸 Saved 'confusion_matrix.png' to your folder. Ready for PowerPoint!")