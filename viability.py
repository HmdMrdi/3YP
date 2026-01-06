import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report

# load and preprocess data
df = pd.read_csv('website_features.csv')
df_processed = df.iloc[:, 1:20]

target_col = df_processed.columns[0]
X = df_processed.drop(columns=[target_col])
y = df_processed[target_col]

# encode target: convert categorical to numbers
if y.dtype == 'object':
    le = LabelEncoder()
    y = le.fit_transform(y)

X = pd.get_dummies(X)

# scaling because kNN is distance based
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=67)

# --- kNN or GNB ---
model = KNeighborsClassifier(n_neighbors=5)

# model = GaussianNB()
# NOTE: GNB is terrible - accuracy = 0.0447 - can investigate, but at present suspect 'naive' assumption is grossly violated (heavy feature correlation) 

# cross validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train, y_train, cv=kf)

print(f"Average Cross-Validation Accuracy: {cv_scores.mean():.4f}")

# fit and predict
model.fit(X_train, y_train)
predictions = model.predict(X_test)

# evaluate
target_names = [str(cls) for cls in le.classes_]
print("\n--- Test Set Performance ---")
print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, predictions, target_names=target_names))