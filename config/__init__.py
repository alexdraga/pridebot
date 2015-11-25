from os import path, getcwd

CONFIG_FOLDER = 'config'
CONFIG_FILENAME = path.join(getcwd(), CONFIG_FOLDER, 'config.cfg')
DATABASES_CONFIG = path.join(getcwd(), CONFIG_FOLDER, 'databases.cfg')
