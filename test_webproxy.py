import unittest
import webproxy
import zlib
from base64 import b64decode
from bs4 import BeautifulSoup

lambda_handler = webproxy.lambda_handler
gstart = None

class TestLambdaServer(unittest.TestCase):

    def proxyresponse_parse(self, lambda_handler_response):
        html = zlib.decompress(b64decode(lambda_handler_response)).decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        global gstart
        gstart = soup
        return bool(soup.find())

    def test_lambda_handler(self):
        test_event = {
            "request": {
                "page_url": "https://startpage.com",
                "headers": {
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0'
                }
            }
        }
        test_context = {}
        self.assertIs(self.proxyresponse_parse(lambda_handler(test_event, test_context)), True, "Test failed")

if __name__ == '__main__':
    unittest.main()