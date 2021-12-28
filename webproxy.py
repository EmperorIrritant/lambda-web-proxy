import requests
from bs4 import BeautifulSoup
import zlib

from base64 import b64encode

def lambda_handler(event, context):
    page_url = event["request"]["page_url"]
    useragent = event["request"]["useragent"]
    headers = {'User-Agent': useragent}
    session = requests.Session()
    requested_page = session.get(page_url, headers=headers)
    pagesoup = BeautifulSoup(requested_page.text)
    for img in pagesoup.findAll('img'):
        if img.has_key('src'):
            image = session.get(img['src'], headers=headers)
            img['src'] = f"data:{image.headers['Content-Type']},base64,{b64encode(image)}"
    for link in pagesoup.findAll('link'):
        if link.has_key('href'):
            css = session.get(css['href'], headers=headers)
            pagesoup.head.style.append(css.text)
    for script in pagesoup.findAll('script'):
        if script.has_key('src'):
            js = session.get(script['src'], headers=headers)
            pagesoup.head.script.append(js.text)

    return b64encode(zlib.compress(str(pagesoup)))