from http import HTTPStatus
import parser
import os
import re
import requests

class Xmltv:
    def fetch_xmltv(self, xmltv_location: str, host:str, port: int, use_https: bool, output_path: str):
        """
        Get the xmltv from either a file location or through a web request.
        The xmltv file will be saved as /static/epg.xml so your IPTV player can access it.
        """

        content = str()
        url_parser = parser.Parser()
        
        if url_parser.is_url(xmltv_location):
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(xmltv_location, headers=headers)

            if response.status_code != HTTPStatus.OK:
                raise Exception(response.text)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            content = response.text
        else:
            with open(xmltv_location, 'r') as input:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                content = input.read()

        with open(str(output_path), 'w') as output:

            port_str = f':{str(port)}' if port != 0 else ''
            
            # Prefix all URLs in the xml file with the proxy endpoints.
            content = re.sub(r'(http|https)', rf'http://{host}{port_str}/proxy/data/\1', content, flags=re.M)
            if use_https == True:
                content = re.sub(rf'(http://{host})',rf'https://{host}', content, flags=re.M)        
            output.write(content)
