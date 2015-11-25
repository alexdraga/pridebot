from os import path, getcwd

CONFIG_FOLDER = path.join(getcwd(), 'config')
CONFIG_FILENAME = path.join(CONFIG_FOLDER, 'config.cfg')
DATABASES_FOLDER = path.join(getcwd(), 'databases')
DATABASES_CONFIG = path.join(getcwd(), CONFIG_FOLDER, 'databases.cfg')
