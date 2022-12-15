import os
from configparser import ConfigParser
from distutils.util import strtobool

class Config:
    _config: ConfigParser

    def __init__(self, root_path: str):
        self._config = ConfigParser(allow_no_value=True)
        self._config.read(os.path.join(root_path, 'config.ini'))
    
    @property
    def M3U_LOCATION(self):
        return os.getenv('M3U_LOCATION', self._config.get('APP', 'M3U_LOCATION'))

    @property
    def XMLTV_LOCATION(self):
        return os.getenv('XMLTV_LOCATION', self._config.get('APP', 'XMLTV_LOCATION')) or ''

    @property
    def M3U_PORT(self):
        return int(os.getenv('M3U_PORT', self._config.get('APP', 'M3U_PORT')) or 0)

    @property
    def M3U_HOST(self):
        return os.getenv('M3U_HOST', self._config.get('APP', 'M3U_HOST'))

    @property
    def LISTEN_PORT(self):
        return int(os.getenv('LISTEN_PORT', self._config.get('APP', 'LISTEN_PORT')))

    @property
    def USE_HTTPS(self):
        return strtobool(os.getenv('USE_HTTPS', self._config.get('APP', 'USE_HTTPS')) or 'False') == 1

    @property
    def RELOAD_INTERVAL_MIN(self):
        return int(os.getenv('RELOAD_INTERVAL_MIN', self._config.get('APP', 'RELOAD_INTERVAL_MIN')))

    @property
    def GROUPS_FILTER(self):
        return os.getenv('GROUPS_FILTER', self._config.get('APP', 'GROUPS_FILTER')) or ''
