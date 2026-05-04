from fastapi import FastAPI
import uvicorn
from fastapi.responses import FileResponse
import os
import uuid
from pydantic import BaseModel

class DownloadRequest(BaseModel):
    url: str


app = FastAPI()

save_path = "downloads"
os.makedirs(save_path, exist_ok=True)

@app.post("/api/download")
def download(item: DownloadRequest):
    url = item.url
    return {"url": url}

@app.get("/")
def read_root():
    return FileResponse("index.html", media_type="text/html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)