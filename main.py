from fastapi import FastAPI
import uvicorn
from fastapi.responses import FileResponse
import os
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import httpx
from bs4 import BeautifulSoup 
from urllib.parse import urljoin
from urllib.parse import urlparse
from fastapi.responses import Response
import io
import zipfile
import base64




class DownloadRequest(BaseModel):
    url: str

class FetchRequest(BaseModel):
    imgurl_list: list[str]

def  get_image_name(imgurl: str)->str:
    if imgurl.startswith("data:image"):
        uro = imgurl.split(';')[0].split('/')[1] 
        ext = "."+uro
        return ext

    if imgurl.startswith(("http://", "https://")):
        imgurl_parsed = urlparse(imgurl)
        file_name = imgurl_parsed.path.split("/")[-1]
        return file_name
    return ".png"





app = FastAPI()
app.mount("/static",StaticFiles(directory="static"))

client = httpx.AsyncClient()


@app.post("/api/download/img")
async def download(item: DownloadRequest):
    try:
        url = item.url
        #获取图片连接
        
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        src_img_url_list = []
        #获取所有图片的src属性
        for img_url in soup.find_all('img'):                    
                    src_img = img_url.get('src')
                    if not src_img:
                        continue
                    if src_img.startswith("data:image"):
                        src_img_url_list.append(src_img)
                    elif not src_img.startswith("http") and not src_img.startswith("https"):
                        src_img_url_list.append(urljoin(url, src_img))
                    
                    else:
                         src_img_url_list.append(src_img)
        if not src_img_url_list:
            return {"message": "没有找到图片", "imgs": "none"}

        return {"imgs": src_img_url_list,"message": "成功"}

    except :
        return {"message": "错误"}

@app.post("/api/fetch/img")
async def fetch_img(item: FetchRequest):
    if not item.imgurl_list:
        return {"message": "没有找到图片"}
    bio= io.BytesIO()
    with zipfile.ZipFile(bio,'w') as zip:
        for idx,imgurl in enumerate(item.imgurl_list):
            try:
                if imgurl.startswith("data:image"):                  
                    img_bytes = base64.b64decode(imgurl.split(",")[1])
                   
                    zip.writestr(f"img{idx}{get_image_name(imgurl)}",img_bytes)
                else:                  
                    response = await client.get(imgurl)
                    
                    zip.writestr(get_image_name(imgurl),response.content)
            except:
                continue
    bio.seek(0)
     
    return Response(content=bio.read(),media_type="application/zip")


@app.get("/")
def read_root():
    return FileResponse("static/index.html", media_type="text/html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)