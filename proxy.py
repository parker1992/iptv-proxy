import os
import logging
import parser
from http import HTTPStatus
from configparser import ConfigParser
from threading import Timer
from flask import Flask, Response
from requests import get

app = Flask(__name__)
config = ConfigParser(allow_no_value=True)
config.read(os.path.join(app.root_path, 'config.ini'))
m3u_parser = parser.Parser()

@app.route('/proxy/stream/<path:path>')
def stream(path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Accept': '/',
        'Connection': 'Keep-Alive'
    }
    stream = get(path, headers=headers, stream=True, allow_redirects=True)

    response = Response(stream.raw, content_type=stream.headers['Content-Type'])
    response.call_on_close(lambda: stream.close())

    return response

@app.route('/proxy/data/<path:path>')
def data(path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Accept': '/'
    }

    app.logger.info(f'BEGIN: Fetching {path}')

    try:
        response = get(path, headers=headers)
        app.logger.info(f'END: Fetched {path}')
    except Exception as err:
        app.logger.exception('END: Error fetching {path}', err)

    return Response(response=response.content, headers=response.headers, status=HTTPStatus.OK)

@app.route('/proxy/reload', methods=['GET'])
def reload():
    try:
        app.logger.info('BEGIN: Force-reloading m3u file')
        reload(config)
        app.logger.info('END: Force-reloaded m3u file')
        return Response(status=HTTPStatus.OK)
    except Exception as err:
        app.logger.exception('END: Error force-reloading m3u file', err)
        return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

def reload_timer():
    try:
        app.logger.info('BEGIN: Reloading m3u file')
        reload(config)
        app.logger.info('END: Reloaded m3u file')
    except Exception as err:
        app.logger.exception('END: Error reloading m3u file', err)

    Timer(60 * int(get_variable(config, 'RELOAD_INTERVAL_MIN')), lambda: reload_timer(config)).start()

def reload(config: ConfigParser):
    m3u_parser.parse_m3u(
        get_variable(config, 'M3U_LOCATION'),
        get_variable(config, 'M3U_HOST'),
        int(get_variable(config, 'M3U_PORT') or 0),
        os.path.join(app.static_folder, 'iptv.m3u')
    )

def get_variable(config: ConfigParser, var: str):
    return os.getenv(var, config.get('APP', var))

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    reload_timer()

if __name__ == '__main__':
    host = get_variable(config, 'M3U_HOST')
    
    reload_timer()

    app.run(host='0.0.0.0', port=int(get_variable(config, 'LISTEN_PORT')))
