import os
import re
import requests
from urllib.parse import urlparse

class Parser:
    def is_url(self, url):
        url_parsed = urlparse(url)
        return url_parsed.scheme in ('http', 'https')

    def parse_m3u(self, m3u_location: str, port: int, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        content = str()

        if self.is_url(m3u_location):
            # TODO: Move to config in case anyone wants to change this for whatever reason
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            # TODO: Throw an exception if the response isn't 200
            content = requests.get(m3u_location, headers=headers).text
        else:
            with open(m3u_location, 'r') as input:
                content = input.read()

        with open(output_path, 'w') as output:
            port_str = f':{str(port)}' if port != 0 else ''
            output.write(re.sub('http', f'http://0.0.0.0{port_str}/proxy/http', content, flags=re.M))
