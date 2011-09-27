'''
The configuration for the application. 

We use the config module found here: http://www.red-dove.com/config-doc/

Load the config file we find in REALCHAT_CONFIG_FILE. This file is
required for config imports to work.
'''

import os
from config import Config

class ConfigException(Exception):
    pass

ENV_NAME = 'REALCHAT_ENV'
if ENV_NAME not in os.environ:
    raise ConfigException(
        'Unknown environment (%s environ variable not set)' % ENV_NAME)
BASE_PATH        = os.path.split(os.path.abspath(__file__))[0]
CONF_FILE_COMMON = os.path.join(BASE_PATH, '%s.cfg' % 'common')
CONF_FILE_ENV    = os.path.join(BASE_PATH, '%s.cfg' % os.environ[ENV_NAME])
THE_CONF = None
def load(_reload=False):
    global THE_CONF
    if _reload or THE_CONF is None:
        THE_CONF = Config()
        THE_CONF.load(file(CONF_FILE_COMMON))
        THE_CONF.load(file(CONF_FILE_ENV))
load()

def get(name, default = None):
    if THE_CONF is None:
        raise ConfigException('configuration not loaded')
    return THE_CONF.get(name, default)
