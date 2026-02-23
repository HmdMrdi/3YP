import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict, KFold, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.utils.class_weight import compute_sample_weight

from sklearn.ensemble import StackingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score, classification_report

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "website_features.csv"

# load and preprocess data
df = pd.read_csv(DATA_DIR)
df_processed = df.iloc[:, 1:20]

# print(df_processed)

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
X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.2, random_state=None, stratify=y)
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
print(f"Cumulative variance: {sum(pca.explained_variance_ratio_):.4f}")

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=20, stratify=y)

# --- kNN or GNB or RandomForest ---
# model2 = MLPClassifier(solver='lbfgs', alpha=0.7,hidden_layer_sizes=(400,200), max_iter=500) #this config is about 0.6+ maybe use xgboost idk
# model = MLPClassifier(solver='lbfgs', alpha=0.7,hidden_layer_sizes=(100,50), max_iter=50, random_state=20)
modelP = KNeighborsClassifier(n_neighbors=30, weights='distance')
# model = AdaBoostClassifier(n_estimators=50, random_state=None)
model = RandomForestClassifier (n_estimators=50, random_state=20, class_weight='balanced', max_depth=30)
# model = SVC(kernel='rbf', C=1.0, gamma='scale', class_weight='balanced')
# model = GaussianNB()
modelR = LogisticRegression(max_iter=100, random_state=None, class_weight='balanced')
# NOTE: GNB is terrible - accuracy = 0.0447 - can investigate, but at present suspect 'naive' assumption is grossly violated (heavy feature correlation) 


estimators = [
    ('RF', RandomForestClassifier (n_estimators=50, random_state=20, max_depth=10, class_weight='balanced', min_samples_split=2)),
    ('LR', SVC(kernel='rbf', C=1.0, gamma='scale', class_weight='balanced', verbose=True)),
    ('kNN', KNeighborsClassifier(n_neighbors=5, weights='distance'))
]


def cascade_ensemble(X, threshold):
    #modelR and modelP not always initialized
    try:
        recall_probs = modelR.predict_proba(X)[:, 1] # probability of positive class
        suspicious_cases = recall_probs >=  threshold

        result = np.zeros(len(X))

        if len(suspicious_cases) > 0:
            X_suspicious = X[suspicious_cases]
            second_iteration_preds = modelP.predict(X_suspicious)
            result[suspicious_cases] = second_iteration_preds
    except Exception as e:
        pass
    
    return result


# cross validation
# kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=20)
kf = KFold(n_splits=5, shuffle=True, random_state=20)
cv_scores = cross_val_score(model, X_train, y_train, cv=kf)
target_names = ['benign' ,'gpt generated',  'malicious'] #same order as they show up - who would have thought

# cv_predict = cross_val_predict(model, X_train, y_train, cv=kf)
# print('Classification Report CV:')
# print(f'{classification_report(y_train, cv_predict, target_names=target_names)}')
# print(f"Average Cross-Validation Accuracy: {cv_scores.mean():.4f} with std: {cv_scores.std():.4f}")



# #================================================== fit and predict #==================================================
# model.fit(X_train, y_train)
# predictions = model.predict(X_test)

stacking_model = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression(class_weight={0:1, 1:4, 2:1}))
modelS = stacking_model.fit(X_train, y_train)
predictions = modelS.predict(X_test)

#================================================== vote - in case of 3 way tie, prefer random forest ==================================================

# model.fit(X_train, y_train)
# model2.fit(X_train, y_train)
# modelP.fit(X_train, y_train)
# modelR.fit(X_train, y_train)

# predictions_cascade = cascade_ensemble(X_test, threshold=0.1)
# predictions2 = model2.predict(X_test)
# predictions1 = model.predict(X_test)



# def vote(a, b, c):
#     if len(a) != len(b) or len(b) != len(c):
#         raise ValueError("mismatch")

#     predictions = []
#     for i in range(len(a)):
#         if a[i] == b[i]:
#             predictions.append(a[i])
#         elif a[i] == c[i]:
#             predictions.append(a[i])
#         elif b[i] == c[i]:
#             predictions.append(b[i])
#         else:
#             predictions.append(a[i])
#     return predictions

# predictions = vote(predictions1, predictions2, predictions_cascade)

# if len(predictions) != len(predictions1):
#     print("length mismatch")
#     print(f'len pred1: {len(predictions1)} len pred2: {len(predictions2)} len pred_cascade: {len(predictions_cascade)} len final: {len(predictions)}')

#======================================================================================================================================================


# evaluate
print("\n--- Test Set Performance ---")
print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, predictions, target_names=target_names))

# 797 benign, 523 malicious, 83 gpt_generated samples in dataset