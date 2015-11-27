# -*- coding: utf-8 -*-
from os import path, getcwd

CONFIG_FOLDER = path.join(getcwd(), 'config')
CONFIG_FILENAME = path.join(CONFIG_FOLDER, 'config.cfg')
DATABASES_FOLDER = path.join(getcwd(), 'databases')
DATABASES_CONFIG = path.join(getcwd(), CONFIG_FOLDER, 'databases.cfg')

DB_DRIVER = 'Driver={Microsoft Access Driver (*.mdb)};DBQ=%s'

UPPER_LATIN = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOWER_LATIN = 'abcdefghijklmnopqrstuvwxyz'
UPPER_CYRILLIC = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
LOWER_CYRILLIC = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
UPPER_UKRANIAN = 'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'
LOWER_UKRAINIAN = 'ґії'
DIGITS = '0123456789'
MAIN_PRINTABLE = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
