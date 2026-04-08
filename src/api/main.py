from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl, field_validator
from ml import collect_integ, model


app = FastAPI()

class UrlModel(BaseModel):
    url: HttpUrl

    @field_validator("url",mode="before")
    @classmethod
    def clean(cls, input: str) -> str:
        if isinstance(input, str):
            input_stripped = input.strip()
            if not input_stripped.startswith(("http://", "https://")):
                return f"http://{input_stripped}"
        return input

# link = UrlModel(url="youtube.com")
# print(link.url)

@app.get("/api")
def root():
    return {"Response" : "Root endpoint - see /docs for API documentation"}

# for quickl testing
@app.get("/api/quicklive")
def livefeatures(url: str):
    features = collect_integ.collect_features(url, "NA", False)
    return {url : features}

@app.post("/api/livefeatures", response_class=HTMLResponse)
async def livefeatures(data: str = Form(...)):
    # does not accept model for all websites for some reason - have to convert to string
    try:
        data = UrlModel(url=data)
        features = collect_integ.collect_features(str(data.url), "NA", False)
        #return {"response" : features}
        #print(features)
        if features == -1:
            prediction = "Unable to fetch URL - cloudflare or similar protection"
        else:
            predictions = model.run_model(features)
            prediction, prediction_proba = predictions
            prediction = "Benign" if prediction[0] == 0 else "GPT" if prediction[0] == 1 else "Phishing/Malicious"
        return f"<div class='text-xl font-bold'> Features for {str(data.url)} </div> <br> <div class='text-lg'> {prediction} ({prediction_proba.max()*100:.2f}%)</div>"
    # Very wide net -> some cases like protected content or just non existent URLs can cause errors
    except Exception as e:
        print(f"Could not processs - {e}")
        return f"<div class='text-xl font-bold'> URL Invalid </div>"



# for quick testing
@app.get("/api/quickmanual")
def livefeatures(url: str):
    features = collect_integ.collect_features(url, "NA", True)
    return {url : features}

@app.post("/api/manualfeatures", response_class=HTMLResponse)
async def livefeatures(data: str = Form(...)):
    features = collect_integ.collect_features(str(data), "NA", True)
    if features == -1:
        prediction = "Unable to process content"
    else:
        predictions = model.run_model(features)
        prediction, prediction_proba = predictions
        prediction = "Benign" if prediction[0] == 0 else "GPT" if prediction[0] == 1 else "Phishing/Malicious"

    # Fun accidental injection: str(data) is source html code, which is rendered in the frontend
    #return f"<div class='text-xl font-bold'> Features for {str(data)} </div> <br> <div class='text-lg'> {prediction} </div>"
    
    return f"<div class='text-xl font-bold'> Features for this website </div> <br> <div class='text-lg'> {prediction} ({prediction_proba.max()*100:.2f}%) </div>"


app.mount("/", StaticFiles(directory="frontend", html=True), name = "frontend")