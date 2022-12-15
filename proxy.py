import os
import logging
from config import Config
import parser
import xmltv
from http import HTTPStatus
from threading import Timer
from flask import Flask, Response
from requests import get
from urllib.parse import urlparse

app = Flask(__name__)
config = Config(app.root_path)
m3u_parser = parser.Parser()
xmltv = xmltv.Xmltv()

@app.route('/proxy/stream/<path:path>')
def stream(path):
    """
    Returns a stream of data from the proxied stream.

    For example a call to, http://0.0.0.0:8080/proxy/stream/http://iptv-provider.com/stream/token
    will make a proxied call to http://iptv-provider.com/stream/token.
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Accept': '/',
        'Connection': 'Keep-Alive'
    }
    stream = get(path, headers=headers, stream=True, allow_redirects=True, timeout=3.0)

    try:
        app.logger.info(f'STREAMING: {path}')
        stream = get(path, headers=headers, stream=True, allow_redirects=True, timeout=3.0)
        app.logger.info(f'STREAMING END: {path}')
    except Exception as err:
        app.logger.exception('STREAMING: Error streaming {path}', err)
        return Response(response='', headers='', status=HTTPStatus.NOT_FOUND)    

    response = Response(stream.raw, content_type=stream.headers['Content-Type'])
    response.call_on_close(lambda: stream.close())

    return response

@app.route('/proxy/data/<path:path>')
def data(path):
    """
    Used for fetching logo and EPG data through the proxy.
    Unlike stream(), this does not return a streamed response.
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Accept': '/'
    }

    app.logger.info(f'BEGIN: Fetching {path}')

    try:
        response = get(path, headers=headers, timeout=3.0)
        app.logger.info(f'END: Fetched {path}')
    except Exception as err:
        app.logger.exception('END: Error fetching {path}', err)
        return Response(response='', headers='', status=HTTPStatus.NOT_FOUND)

    return_headers = {
        'Content-Type': response.headers['Content-Type'],
        'Content-Disposition': f'attachment; filename="{os.path.basename(urlparse(path).path)}"'
    }

    return Response(response=response.content, headers=return_headers, status=HTTPStatus.OK)

@app.route('/proxy/reload', methods=['GET'])
def reload():
    """
    By default, the m3u file will be reloaded every 60 minutes.
    This is used to reload the m3u on an ad-hoc basis.
    """

    try:
        app.logger.info('BEGIN: Force-reloading m3u file')
        reload(config)
        app.logger.info('END: Force-reloaded m3u file')
        return Response(status=HTTPStatus.OK)
    except Exception as err:
        app.logger.exception('END: Error force-reloading m3u file', err)
        return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

def reload_timer():
    """
    This will reload the m3u and then subsequently reload it every [by default] 60 minutes afterwards.
    """

    try:
        app.logger.info('BEGIN: Reloading m3u file')
        reload(config)
        app.logger.info('END: Reloaded m3u file')
    except Exception as err:
        app.logger.exception('END: Error reloading m3u file', err)

    Timer(60 * config.RELOAD_INTERVAL_MIN, lambda: reload_timer(config)).start()

def reload(config: Config):
    m3u_parser.parse_m3u(
        config.M3U_LOCATION,
        config.M3U_HOST,
        config.M3U_PORT,
        config.USE_HTTPS,
        config.GROUPS_FILTER,
        os.path.join(app.static_folder, 'iptv.m3u')
    )

    xmltv.fetch_xmltv(
        config.XMLTV_LOCATION,
        config.M3U_HOST,
        config.M3U_PORT,
        config.USE_HTTPS,
        os.path.join(app.static_folder, 'epg.xml')
    )

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    reload_timer()

if __name__ == '__main__':
    host = config.M3U_HOST
    
    reload_timer()

    app.run(host='0.0.0.0', port=config.LISTEN_PORT)
