# CS310 3YP
## Web Security Evaluation Via Dom Analysis
### Public Preface
This was my final-year dissertation project, exploring whether DOM-based features could be used to distinguish between benign, phishing, and AI-generated websites. A large part of the project was confirming the tractability of detecting AI-generated
websites (code-wise).
I built the project in Python (Jupyter Notebook) as an end to end pipeline: collecting and processing website data, extracting DOM features, training and evaluating several ML models, and deploying the resulting classifier through a FastAPI web app.
The project achieved 90% cross validation accuracy with the final random forest model, with a macro F1-score of 0.80. Full details on the methodology, limitations and results in dissertation.

### Introduction
The application is designed to run as a web app that takes either html source code, or the URL as input, processes it using collect_integ (slightly modified version of collect.py)
Collected features are passed into the joblib saved model before being passed to the frontend


## Installation
Once installed and CD into repo create venv:
```
python -m venv venv
```
and activate venv

Install dependencies (use requirements_ext if requirements does not work):

```
pip install -r requirements.txt
```
or
```
python -m pip install -r requirements.txt
```

## Run
```
cd src
uvicorn api.main:app --reload
```
(--reload optional -> restarts on all code changes)

Application runs on http://127.0.0.1:8000
## Project Structure

AI_html_ground_truth - this directory contains all the AI-generated source code

data - a collection of .txt lists of the websites crawled and the csv fiiles they have been saved to (website_features.csv is the main file)

notebook - includes both primary notebooks and the initial viability.py file that the feasibility was confirmed on

src - includes all files relevant to running (with the exception of website_features.csv - used for adhoc scaling and le -> can save these like the model but trivial cost)

collect.py - reads URLs from data/_.txt and stores in .csv file
