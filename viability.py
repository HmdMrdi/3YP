import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.decomposition import PCA
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

#for pca approaches
pca = PCA(n_components=12)
X_pca = pca.fit_transform(X_scaled)
X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.2, random_state=None)
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
print(f"Cumulative variance: {sum(pca.explained_variance_ratio_):.4f}")

#X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=None)

# --- kNN or GNB or RandomForest ---
# model = MLPClassifier(solver='lbfgs', alpha=0.7,hidden_layer_sizes=(100,50), max_iter=200) #this config is about 0.6+ maybe use xgboost idk
# model = KNeighborsClassifier(n_neighbors=3, weights='uniform')
model = RandomForestClassifier (n_estimators=50, random_state=None)
# model = GaussianNB()
# model = LogisticRegression(max_iter=100, random_state=None, class_weight='balanced')
# NOTE: GNB is terrible - accuracy = 0.0447 - can investigate, but at present suspect 'naive' assumption is grossly violated (heavy feature correlation) 

# cross validation
kf = KFold(n_splits=5, shuffle=True, random_state=67)
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

# 797 benign, 523 malicious, 83 gpt_generated samples in dataset