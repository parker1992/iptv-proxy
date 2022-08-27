# TODO: Clean this entire thing up. There's a lot of duplicate code here.

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
m3u_parser = parser.Parser()

@app.route('/proxy/<path:path>')
def proxy(path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Accept': '/',
        'Connection': 'Keep-Alive'
    }
    response = get(path, headers=headers, stream=True, timeout=5, allow_redirects=True)

    return response.raw

@app.route('/proxy/reload', methods=['GET'])
def reload():
    try:
        app.logger.info('BEGIN: Force-reloading m3u file')

        m3u_parser.parse_m3u(
            get_variable(config, 'M3U_LOCATION'),
            get_variable(config, 'M3U_HOST'),
            int(get_variable(config, 'M3U_PORT') or 0),
            os.path.join(app.static_folder, 'iptv.m3u')
        )

        app.logger.info('END: Force-reloaded m3u file')
        return Response(status=HTTPStatus.OK)
    except Exception as err:
        app.logger.exception('END: Error force-reloading m3u file', err)
        return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

def reload_timer(m3u_location: str, host: str, port: int, reload_interval: int, output_path: str):
    try:
        app.logger.info('BEGIN: Reloading m3u file')
        m3u_parser.parse_m3u(m3u_location, host, port, output_path)
        app.logger.info('END: Reloaded m3u file')
    except Exception as err:
        app.logger.exception('END: Error reloading m3u file', err)

    Timer(60 * reload_interval, lambda: reload_timer(m3u_location, host, port, reload_interval, output_path)).start()

def get_variable(config: ConfigParser, var: str):
    return os.getenv(var, config.get('APP', var))

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    config.read(os.path.join(app.root_path, 'config.ini'))

    reload_timer(
        get_variable(config, 'M3U_LOCATION'),
        get_variable(config, 'M3U_HOST'),
        int(get_variable(config, 'M3U_PORT') or 0),
        int(get_variable(config, 'RELOAD_INTERVAL_MIN')),
        os.path.join(app.static_folder, 'iptv.m3u')
    )

if __name__ == '__main__':
    config.read(os.path.join(app.root_path, 'config.ini'))

    host = get_variable(config, 'M3U_HOST')
    
    reload_timer(
        get_variable(config, 'M3U_LOCATION'),
        host,
        int(get_variable(config, 'M3U_PORT') or 0),
        int(get_variable(config, 'RELOAD_INTERVAL_MIN')),
        os.path.join(app.static_folder, 'iptv.m3u')
    )

    app.run(host='0.0.0.0', port=int(get_variable(config, 'LISTEN_PORT')))