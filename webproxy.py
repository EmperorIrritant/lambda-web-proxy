import requests
from bs4 import BeautifulSoup
import zlib
from urllib.parse import urlparse, urljoin
from base64 import b64encode
from multiprocessing import Pool
from multiprocessing import cpu_count

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

    pool = Pool(cpu_count())

    for form in pagesoup.findAll('form'):
        if form['action'].startswith('/'):
            form['action'] = urljoin(domain, form['action'])

    img_with_srcs = [img for img in pagesoup.findAll('img') if img.has_attr('src')]
    for img in img_with_srcs:
        if img['src'].startswith('/'):
            img['src'] = urljoin(domain, img['src'])

    img_with_srcs_parameters = [(img['src'], session, headers, img) for img in img_with_srcs]
    pool.map(get_url_content, img_with_srcs_parameters)

    link_with_css_hrefs = [link for link in pagesoup.findAll('link') if link['rel'] == "stylesheet" and link.has_attr('href')]
    for link in link_with_css_hrefs:
        if link['href'].startswith('/'):
            link['href'] = urljoin(domain, link['href'])
        else:
            link['href'] = ''

    link_with_css_hrefs_parameters = [(link['href'], session, headers, pagesoup.head.style) for link in link_with_css_hrefs]
    pool.map(get_url_content, link_with_css_hrefs_parameters)

    script_with_srcs = [script for script in pagesoup.findAll('script') if script.has_attr('src')]
    for script in script_with_srcs:
        if script['src'].startswith('/'):
            script['src'] = urljoin(domain, script['src'])

    script_with_srcs_parameters = [(script[src], session, headers, pagesoup.head.script) for script in script_with_srcs]
    pool.map(get_url_content, script_with_srcs_parameters)

    pool.close()
    pool.join()

    session.close()

    return b64encode(zlib.compress(str(pagesoup).encode('utf-8')))