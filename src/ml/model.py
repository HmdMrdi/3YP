import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier

from pathlib import Path

BASE_DIR = Path.cwd().parent
DATA_DIR = BASE_DIR / "data" / "website_features.csv"

def run_model(features) -> str:
    df = pd.read_csv(DATA_DIR)
    df_processed = df.iloc[:, 1:20]

    target_col = df_processed.columns[0]
    X = df_processed.drop(columns=[target_col])
    y = df_processed[target_col]

    #print(X[1:2])
    # print(y[0:5])
    #print(X.shape)
    features = pd.DataFrame([features], columns=X.columns)
    #print(features)

    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)

    X = pd.get_dummies(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    features = pd.get_dummies(features)
    features = features.reindex(columns=X.columns, fill_value=0)
    features_scaled = scaler.transform(features)

    print(X_scaled[1:2].shape)
    print(features_scaled.shape)
    
    X_train, _, y_train, _ = train_test_split(X_scaled, y, test_size=0.2, random_state=20, stratify=y)
    target_names = ['benign' ,'gpt generated',  'malicious']

    #print(X_train[0:5])

    model1 = RandomForestClassifier(n_estimators=50, random_state=20, max_depth=10, class_weight='balanced', min_samples_split=2, max_features='sqrt', verbose=False).fit(X_train, y_train)
    prediction = model1.predict(features_scaled)
    print(prediction)
    return prediction

print(run_model((4, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 7, 0, False, 0, 0, False, False, False, 12)))



