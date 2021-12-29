import requests
from bs4 import BeautifulSoup
import zlib
from urllib.parse import urlparse, urljoin
from base64 import b64encode
from threading import Thread

threads = []

def get_url_content(url, session, headers, htmlelement):
    elementcontent = session.get(url, session, headers=headers)
    if htmlelement.name == 'img':
        htmlelement['src'] = f"data:{image.headers['Content-Type']},base64,{b64encode(elementcontent)}"
    else:
        htmlelement.append(elementcontent)

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
            thread = Thread(target=get_url_content, args=(img['src'], session, headers, img))
            threads.append(thread)
    for link in pagesoup.findAll('link'):
        if link['rel'] == "stylesheet" and link.has_attr('href'):
            if link['href'].startswith('/'):
                link['href'] = urljoin(domain, link['href'])
            thread = Thread(target=get_url_content, args=(link['href'], session, headers, pagesoup.head.style))
            threads.append(thread)
        else:
            link['href'] = ''
    for script in pagesoup.findAll('script'):
        if script.has_attr('src'):
            if script['src'].startswith('/'):
                script['src'] = urljoin(domain, script['src'])
            thread = Thread(target=get_url_content, args=(script['src'], session, headers, pagesoup.head.script))
            threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    session.close()

    return b64encode(zlib.compress(str(pagesoup).encode('utf-8')))