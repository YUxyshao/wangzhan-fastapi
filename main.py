from fastapi import FastAPI
import uvicorn
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def read_root():
    return FileResponse("index.html", media_type="text/html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)