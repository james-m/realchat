'''
The configuration for the application. 

We use the config module found here: http://www.red-dove.com/config-doc/

Load the config file we find in REALCHAT_CONFIG_FILE. This file is
required for config imports to work.
'''

import os
from config import Config, ConfigMerger

class ConfigException(Exception):
    pass

ENV_NAME = 'REALCHAT_ENV'
if ENV_NAME not in os.environ:
    raise ConfigException(
        'Unknown environment (%s environ variable not set)' % ENV_NAME)
BASE_PATH        = os.path.split(os.path.abspath(__file__))[0]
CONF_FILE_COMMON = os.path.join(BASE_PATH, '%s.cfg' % 'common')
CONF_FILE_ENV    = os.path.join(BASE_PATH, '%s.cfg' % os.environ[ENV_NAME])
CONF_FILE_LOCAL  = os.path.join(BASE_PATH, '%s.cfg' % 'local')
if not os.path.exists(CONF_FILE_LOCAL):
    CONF_FILE_LOCAL = None
THE_CONF = None
def _local_resolver(map1, map2, key):
    return 'overwrite'

def load(_reload=False):
    global THE_CONF
    if _reload or THE_CONF is None:
        THE_CONF = Config()
        THE_CONF.load(file(CONF_FILE_COMMON))
        THE_CONF.load(file(CONF_FILE_ENV))
        if CONF_FILE_LOCAL is not None:
            local_conf = Config()
            merger = ConfigMerger(_local_resolver)
            local_conf.load(file(CONF_FILE_LOCAL))
            merger.merge(THE_CONF, local_conf)

load()

def get(name, default = None):
    if THE_CONF is None:
        raise ConfigException('configuration not loaded')
    return THE_CONF.get(name, default)
