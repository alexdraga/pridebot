# -*- coding: utf-8 -*-
import pyodbc

from config import DB_DRIVER


class DBDriver(object):
    def __init__(self, filename):
        connection_string = DB_DRIVER % filename
        self.connection = pyodbc.connect(connection_string)
        self.cursor = self.connection.cursor()

    def perform_search(self, script):
        self.cursor.execute(script)
        results = self.cursor.fetchall()
        return [word[0] for word in results]

    @staticmethod
    def split_letters(letters):
        split_letters = {}
        for letter in letters:
            split_letters.setdefault(letter, 0)
            split_letters[letter] += 1
        return split_letters

    @staticmethod
    def prepare_multi_letter(letter, number):
        if len(letter) and number:
            low_level = '%'
            for i in range(0, number):
                low_level += letter + '%'
            return low_level

    @staticmethod
    def prepare_strict_order(letters):
        if letters:
            low_level = '%'
            for letter in letters:
                low_level += letter + '%'
            return low_level

    def do_anagram(self, letters, length=None, table='words', field='word'):
        """
        Prepare SQL query for searching word with specified letters, e.g
        if we want to anagram letters " D A D " query will be like:
        SELECT word from (SELECT word FROM words WHERE word LIKE '%D%D%') WHERE
        SELECT word FROM words WHERE word LIKE '%A%'
        :param letters:
        :param length:
        :param table:
        :param field:
        :return:
        """
        if letters:
            letters_split = self.split_letters(letters)
            low_level_script = \
                u"SELECT {field} FROM {table} WHERE {field} LIKE '{letters}'".format(
                    field=field,
                    table=table,
                    letters=self.prepare_multi_letter(
                        letters_split.keys()[0],
                        letters_split[letters_split.keys()[0]]))
            keys = letters_split.keys()
            for key in range(1, len(keys)):
                low_level_script = \
                u"SELECT {field} FROM ({low_level_script}) WHERE {field} LIKE'{letters}'".format(
                    field=field,
                    low_level_script=low_level_script,
                    letters=self.prepare_multi_letter(
                        letters_split.keys()[key],
                        letters_split[letters_split.keys()[key]]))
            if length in ['0', '=0', '=']:
                low_level_script += " AND LEN(word)=%s" % str(len(letters))
            elif length is not None:
                low_level_script += " AND LEN(word)%s" % length
            return self.perform_search(low_level_script)

    def do_anagram_strict_order(self, letters, length=None, table='words', field='word'):
        if letters:
            low_level_script = \
                u"SELECT {field} FROM {table} WHERE {field} like'{letters}'".format(
                    field=field,
                    table=table,
                    letters=self.prepare_strict_order(letters))
            if length in ['0', '=0', '=']:
                low_level_script += " AND LEN(word)=%s" % str(len(letters))
            elif length is not None:
                low_level_script += " AND LEN(word)%s" % length
            return self.perform_search(low_level_script)
