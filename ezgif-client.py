import os
import re
import shutil
import requests
from bs4 import BeautifulSoup

BASE_DIR="C:\\Users\\nikolay\\NSFW-2"
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0"

def ezgif_convert(root, fname):
    fpath = os.path.join(root, os.path.splitext(fname)[0] + ".mp4")
    if os.path.exists(fpath):
        return

    # stage 1 - acquire identifier from form action
    r = requests.post("https://ezgif.com/webp-to-mp4", files = {
        "new-image": open(os.path.join(root, fname), "rb")
    }, headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://ezgif.com"
    }, allow_redirects=True)
    print(r.url)
    for r in r.history:
        print(r.status_code, r.url, str(r.headers))

    soup = BeautifulSoup(r.content, "html5lib")
    form = soup.find("form", {
        "action": re.compile(r'^\/webp-to-mp4\/')
    })
    if not form:
        with open("ezgif-1.html", "wb") as out:
            out.write(r.content)
        raise Exception("form with specified action url not found")
        
    url = form["action"]
    # stage 2 - post "convert", in a result we should get img tag with id "target"
    # and download request url in src
    r = requests.post("https://ezgif.com" + url, allow_redirects = True,
        data = {"convert": "Convert WebP To MP4!"},
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": "https://ezgif.com/webp-to-mp4"
        })
    if r.status_code != 200:
        raise Exception("stage 2 ezgif failed")
    soup = BeautifulSoup(r.content, "html5lib")
    target = soup.find("img", {
        "id": "target"
    })
    if not target:
        with open("ezgif-2.html", "wb") as out:
            out.write(r.content)
        raise Exception("img 'target' not found!")
    download = "https:" + target["src"]
    
    # stage 3 - download output file using url gathered from src attribute
    with requests.get(download, stream=True) as r:
        with open(fpath, "wb") as f:
            shutil.copyfileobj(r.raw, f)
            print(f"webp2mp4 [{fname}] success => ${fpath}")
    

if __name__ == "__main__":
    for r, _, files in os.walk(BASE_DIR):
        for fname in files:
            if os.path.splitext(fname)[-1] == ".webp":
                ezgif_convert(r, fname)