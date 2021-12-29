import requests
from bs4 import BeautifulSoup
import zlib
from urllib.parse import urlparse, urljoin
from base64 import b64encode

def lambda_handler(event, context):
    page_url = event["request"]["page_url"]
    headers = event["request"]["headers"]
    session = requests.Session()
    requested_page = session.get(page_url, headers=headers)
    pagesoup = BeautifulSoup(requested_page.text, "lxml")
    parsed_uri = urlparse(page_url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    for form in pagesoup.findAll('form'):
        if form['action'].startswith('/'):
            form['action'] = urljoin(domain, form['action'])
    for img in pagesoup.findAll('img'):
        if img.has_attr('src'):
            if img['src'].startswith('/'):
                img['src'] = urljoin(domain, img['src'])
            image = session.get(img['src'], headers=headers)
            img['src'] = f"data:{image.headers['Content-Type']},base64,{b64encode(image)}"
    for link in pagesoup.findAll('link'):
        if link['rel'] == "stylesheet" and link.has_attr('href'):
            if link['href'].startswith('/'):
                link['href'] = urljoin(domain, link['href'])
            css = session.get(link['href'], headers=headers)
            pagesoup.head.style.append(css.text)
        else:
            link['href'] = ''
    for script in pagesoup.findAll('script'):
        if script.has_attr('src'):
            if script['src'].startswith('/'):
                script['src'] = urljoin(domain, script['src'])
            js = session.get(script['src'], headers=headers)
            pagesoup.head.script.append(js.text)
    session.close()

    return b64encode(zlib.compress(str(pagesoup).encode('utf-8')))