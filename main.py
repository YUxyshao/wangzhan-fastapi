from fastapi import FastAPI
import uvicorn
from fastapi.responses import FileResponse
import os
import uuid
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import httpx
from bs4 import BeautifulSoup 
from urllib.parse import urljoin
from fastapi.responses import Response


class DownloadRequest(BaseModel):
    url: str

class FetchRequest(BaseModel):
    imgurl: str


app = FastAPI()
app.mount("/static",StaticFiles(directory="static"))

save_path = "downloads"
os.makedirs(save_path, exist_ok=True)

client = httpx.AsyncClient()

@app.post("/api/download/img")
async def download(item: DownloadRequest):
    try:
        url = item.url
        #获取图片连接
        
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_url = soup.find_all('img')
        src_img_url_list = []
        for img_url in soup_url:
            src_img = img_url.get('src')
            if src_img:
                src_img_url_list.append(urljoin(url, src_img))

        return {"imgs": src_img_url_list,"message": "成功"}
    except :
        return {"message": "错误"}

@app.post("/api/fetch/img")
async def fetch_img(item: FetchRequest):
    response = await client.get(item.imgurl)
    return Response(content=response.content)


@app.get("/")
def read_root():
    return FileResponse("static/index.html", media_type="text/html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)