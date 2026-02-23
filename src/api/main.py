from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl, field_validator
from ml import collect_integ


app = FastAPI()

class MyModel(BaseModel):
    url: HttpUrl

    @field_validator("url",mode="before")
    @classmethod
    def clean(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().lower()
            if not v.startswith(("http://", "https://")):
                return f"http://{v}"
        return v

# link = MyModel(url="youtube.com")
# print(link.url)

@app.get("/")
def root():
    return {"Model" : "Hello"}

# for quickl testing
@app.get("/quicklive")
def livefeatures(url: str):
    features = collect_integ.collect_features(url, "NA", False)
    return {url : features}

@app.post("/livefeatures")
def livefeatures(data: MyModel):
    # does not accept model for all websites for some reason - have to convert to string
    features = collect_integ.collect_features(str(data.url), "NA", False)
    return {"response" : features}