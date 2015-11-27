# -*- coding: utf-8 -*-
import pyodbc
from config import DB_DRIVER


class DBDriver(object):
    def __init__(self, filename='rus1.mdb'):
        connection_string = DB_DRIVER % filename
        self.connection = pyodbc.connect(connection_string)
        self.cursor = self.connection.cursor()

    def perform_search(self, script):
        self.cursor.execute(script)
        results = self.cursor.fetchall()
        results_tuple = []
        for result in results:
            results_tuple.append(result[0])

        return results_tuple

    @staticmethod
    def split_letters(letters):
        splitted_letters = {}
        for letter in letters:
            if letter in splitted_letters.keys():
                splitted_letters[letter] += 1
            else:
                splitted_letters.update({letter: 1})
        return splitted_letters

    @staticmethod
    def prepare_multi_letter(letter, number):
        if letter and number > 0:
            low_level = '%' + letter + '%'
            for i in range(1, number, 1):
                low_level += letter + '%'
            return low_level

    @staticmethod
    def prepare_strict_order(letters):
        if letters:
            low_level = '%' + letters[0] + '%'
            for letter in range(1, len(letters), 1):
                low_level += letters[letter] + '%'
            return low_level

    def perform_anagramm(self, letters, length=None, table='words', field='word'):
        if letters:
            splitted_letters = self.split_letters(letters)
            low_level_script = \
                u"SELECT {field} FROM {table} WHERE {field} LIKE '{letters}'".format(
                    field=field,
                    table=table,
                    letters=self.prepare_multi_letter(
                        splitted_letters.keys()[0],
                        splitted_letters[splitted_letters.keys()[0]]))
            keys = splitted_letters.keys()
            for key in range(1, len(keys)):
                low_level_script = \
                u"SELECT {field} FROM ({low_level_script}) WHERE {field} LIKE'{letters}'".format(
                    field=field,
                    low_level_script=low_level_script,
                    letters=self.prepare_multi_letter(
                        splitted_letters.keys()[key],
                        splitted_letters[splitted_letters.keys()[key]]))
            if length is not None:
                if length == '0' or length == '=0':
                    low_level_script += " AND LEN(word)=%s" % str(len(letters))
                else:
                    low_level_script += " AND LEN(word)%s" % length
            return self.perform_search(low_level_script)

    def perform_strict_order(self, letters, length=None, table='words', field='word'):
        if letters:
            low_level_script = \
                "SELECT {field} FROM {table} WHERE {field} like'{letters}'".format(
                    field=field,
                    table=table,
                    letters=self.prepare_strict_order(letters))
            if length is not None:
                if length == '0' or length == '=0':
                    low_level_script += " AND LEN(word)=%s" % str(len(letters))
                else:
                    low_level_script += " AND LEN(word)%s" % length
            return self.perform_search(low_level_script)
