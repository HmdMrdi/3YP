from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl, field_validator
from ml import collect_integ, model


app = FastAPI()

class MyModel(BaseModel):
    url: HttpUrl

    @field_validator("url",mode="before")
    @classmethod
    def clean(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v.startswith(("http://", "https://")):
                return f"http://{v}"
        return v

# link = MyModel(url="youtube.com")
# print(link.url)

@app.get("/api")
def root():
    return {"Model" : "Hello"}

# for quickl testing
@app.get("/api/quicklive")
def livefeatures(url: str):
    features = collect_integ.collect_features(url, "NA", False)
    return {url : features}

@app.post("/api/livefeatures", response_class=HTMLResponse)
async def livefeatures(data: str = Form(...)):
    # does not accept model for all websites for some reason - have to convert to string
    data = MyModel(url=data)
    features = collect_integ.collect_features(str(data.url), "NA", False)
    #return {"response" : features}
    #print(features)
    if features == -1:
        prediction = "Unable to fetch URL - cloudflare or similar protection"
    else:
        prediction = model.run_model(features)
    return f"<div class='text-xl font-bold'> Features for {str(data.url)} </div> <br> <div class='text-lg'> {prediction} </div>"

app.mount("/", StaticFiles(directory="frontend", html=True), name = "frontend")