import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import numpy as np

# Load the dataset
df = pd.read_csv('creditcard_sample.zip')

# --- Supervised Learning Approach ---
# This dataset is already labeled. The 'Class' column indicates if a transaction is fraudulent (1) or not (0).

# Select features (X) and the target (y)
# We will use all columns except 'Class' and 'Time' as features.
features = [col for col in df.columns if col not in ['Class', 'Time']]
X = df[features]
y = df['Class']

# Because the dataset is very large and to speed up the process for this example,
# we will use a smaller sample of the data.
X_sample, _, y_sample, _ = train_test_split(X, y, train_size=0.1, random_state=42, stratify=y)


# Split the sampled data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_sample, y_sample, test_size=0.3, random_state=42, stratify=y_sample)

print("Data prepared for supervised learning.")
print(f"Number of anomalies (frauds) in training set: {y_train.sum()}")
print(f"Number of anomalies (frauds) in test set: {y_test.sum()}")

# Initialize and train the RandomForestClassifier
# `class_weight='balanced'` is crucial for this highly imbalanced dataset.
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
print("\n--- Model Evaluation ---")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Fraud']))

# Visualize the results using two of the PCA components
plt.figure(figsize=(10, 8))
# Plot normal transactions
plt.scatter(X_test[y_test == 0]['V1'], X_test[y_test == 0]['V2'], label='Normal', alpha=0.5, c='blue', s=10)
# Plot fraudulent transactions
plt.scatter(X_test[y_test == 1]['V1'], X_test[y_test == 1]['V2'], label='Fraud', alpha=0.9, c='red', s=20)
# Plot model's predictions
predicted_frauds = (y_pred == 1)
plt.scatter(X_test[predicted_frauds]['V1'], X_test[predicted_frauds]['V2'],
            label='Predicted Fraud', marker='x', s=50, c='yellow')


plt.title('Supervised Anomaly Detection on Credit Card Fraud Dataset')
plt.xlabel('V1 (PCA Feature)')
plt.ylabel('V2 (PCA Feature)')
plt.legend()
plt.grid(True)
plt.savefig('supervised_fraud_detection_plot.png')
plt.show()

print("\nSupervised fraud detection complete. Plot saved to supervised_fraud_detection_plot.png")
