# CS310 3YP
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
