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

ENV_NAME = 'REALCHAT_CONFIG_FILE'
if ENV_NAME not in os.environ:
    raise ConfigException(
        'Unknown environment (%s environ variable not set)' % ENV_NAME)
CONF_FILENAME = os.environ[ENV_NAME]
THE_CONF = None
def load(_reload=False):
    global THE_CONF
    if _reload or THE_CONF is None:
        THE_CONF = Config(CONF_FILENAME) 
load()

def get(name, default = None):
    if THE_CONF is None:
        raise ConfigException('configuration not loaded')
    return THE_CONF.get(name, default)
