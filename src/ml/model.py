import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier

from pathlib import Path

# for saving model
import joblib

# quick inference speed check
import time

BASE_DIR = Path.cwd().parent
DATA_DIR = BASE_DIR / "data" / "website_features.csv"

saved_model = joblib.load(BASE_DIR / "src" / "trained_model.pkl")


'''
Logic:
    - load data, preprocess
    - train model - for testing, trainng is adhoc
    - process features using same preporcessing as training
    - run and return pred/confidence

    joblib commented out, but used to save model for run_model func

    NOTE:
    run_model is largely the same -> since le and scaler are not saved, refit
    each time (small dataset so fine for now) hence all 'redundant' repeated code

'''


def run_model_dev(features) -> str:
    start = time.time()
    df = pd.read_csv(DATA_DIR)
    df_processed = df.iloc[:, 1:20]

    target_col = df_processed.columns[0]
    X = df_processed.drop(columns=[target_col])
    y = df_processed[target_col]

    pd.set_option('display.max_columns', None)
    features = pd.DataFrame([features], columns=X.columns)
    print(features)

    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)

    X = pd.get_dummies(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    features = pd.get_dummies(features)
    features_scaled = scaler.transform(features)

    # print(X_scaled[1:2].shape)
    # print(features_scaled.shape)
    
    X_train, _, y_train, _ = train_test_split(X_scaled, y, test_size=0.2, random_state=26, stratify=y)

    model1 = RandomForestClassifier(n_estimators=200, random_state=26, max_depth=20, class_weight='balanced', min_samples_split=5, max_features='sqrt', verbose=False).fit(X_train, y_train)
    prediction = model1.predict(features_scaled)
    prediction_proba = model1.predict_proba(features_scaled)

    # for saving model
    #joblib.dump(model1, 'trained_model.pkl')

    # inference time check
    # end = time.time()
    # print(f"Inf time: {end - start} seconds")

    return (prediction , prediction_proba)

#================================= non-dev function =============================

def run_model(features) -> str:
    df = pd.read_csv(DATA_DIR)
    df_processed = df.iloc[:, 1:20]

    target_col = df_processed.columns[0]
    X = df_processed.drop(columns=[target_col])
    y = df_processed[target_col]

    pd.set_option('display.max_columns', None)
    features = pd.DataFrame([features], columns=X.columns)
    print(features)

    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)

    X = pd.get_dummies(X)
    scaler = StandardScaler()
    _ = scaler.fit_transform(X)

    features = pd.get_dummies(features)
    features_scaled = scaler.transform(features)


    prediction = saved_model.predict(features_scaled)
    prediction_proba = saved_model.predict_proba(features_scaled)
    return (prediction , prediction_proba)

#print(run_model((124, 0.5, 0.25, 0, 0.0, 0, 0, 1 , 0, 0, 5, False, 0, 0, False, False, False, 34)))



