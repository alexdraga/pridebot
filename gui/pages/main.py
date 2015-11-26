# -*- coding: utf-8 -*-

__author__ = 'a_draga'

import os
import datetime
import random
import Tkinter
import ConfigParser

from config import CONFIG_FILENAME, DATABASES_CONFIG, default_settings

from web.actions import QuestUA
from config.default_settings import SETTINGS, section
from gui.pages.anagrammator import AnagrammForm
from gui.pages.code_generator import GenerateCodesForm
from gui.pages.settings import SettingsForm
from config.localization import BUTTONS, LANGUAGE
from gui.helpers.gui_helpers import center_window

class MainForm(object):
    def __init__(self):
        self.read_config()
        self.root = Tkinter.Tk()
        self.root.title('PrideBot')

        self.frame = Tkinter.Frame(self.root)
        self.codes = Tkinter.Text(self.frame, font=("Helvetica", 12))

        self.random = Tkinter.IntVar(self.root)

        random = Tkinter.Checkbutton(self.root, text=BUTTONS['enter_in_random_order'][LANGUAGE], variable=self.random)

        self.start_codes = Tkinter.Button(self.root, text=BUTTONS['start_brute_force'][LANGUAGE], command=self.start_brute_force)
        self.copy_to_clipboard = Tkinter.Button(self.root, text=BUTTONS['copy_codes'][LANGUAGE], command=self.copy_to_clipboard)
        self.scroll_bar = Tkinter.Scrollbar(self.frame)
        self.root.winfo_height()
        self.settings = Tkinter.Button(self.root, text=BUTTONS['settings'][LANGUAGE], command=self.call_settings)

        self.code_generator = Tkinter.Button(self.root, text=BUTTONS['code_generator'][LANGUAGE], command=self.call_code_generator)
        self.db_words = Tkinter.Button(self.root, text=BUTTONS['anagrams'][LANGUAGE], command=self.call_anagrammator)
        self.clear_codes = Tkinter.Button(self.root, text=BUTTONS['clear'][LANGUAGE], command=self.clear_codes)

        self.frame.pack(fill=Tkinter.BOTH, expand=Tkinter.YES)
        self.start_codes.pack(side=Tkinter.RIGHT)
        random.pack(side=Tkinter.RIGHT)
        self.copy_to_clipboard.pack(side=Tkinter.RIGHT)
        self.settings.pack(side=Tkinter.LEFT)
        self.code_generator.pack(side=Tkinter.LEFT)
        self.db_words.pack(side=Tkinter.LEFT)
        self.clear_codes.pack(side=Tkinter.RIGHT)

        self.scroll_bar.pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH)
        self.codes.pack(fill=Tkinter.BOTH, expand=Tkinter.YES)

        self.scroll_bar.config(command=self.codes.yview)
        self.codes.config(yscrollcommand=self.scroll_bar.set)
        center_window(self.codes.winfo_reqwidth() + self.scroll_bar.winfo_reqwidth(),
                      self.codes.winfo_reqheight() + self.settings.winfo_reqheight(), self.root)

        self.root.mainloop()
        self.write_config()

    def call_settings(self):
        self.root.withdraw()
        SettingsForm(self)

    def clear_codes(self):
        self.codes.delete("0.0", Tkinter.END)

    def call_code_generator(self):
        self.root.withdraw()
        GenerateCodesForm(self)

    def start_brute_force(self):
        codes = self.codes.get("0.0", Tkinter.END).split('\n')
        if codes != ['', ''] and codes != [''] and codes:
            time_started = datetime.datetime.now()
            # Hiding main GUI form
            self.root.withdraw()
            # Starting webdriver and performing login
            quest = QuestUA()
            if quest.is_url_opened:
                if quest.is_login_performed:
                    codes_tried = 0

                    if self.random.get():
                        number_not_tried = range(0, len(codes) - 1)
                        while number_not_tried:
                            code_to_try = random.choice(number_not_tried)
                            number_not_tried.remove(code_to_try)
                            code = codes[code_to_try]
                            print u' Пробуем код: %s' % code
                            if quest.check_code(code):
                                codes_tried += 1
                            else:
                                # check_code returns False or None only if firefox was closed etc.
                                print u' Возникла ошибка во время ввода кода. Остановка перебора...'
                                break
                    else:
                        for code in codes:
                            if code != '':
                                print u' Пробуем код: %s' % code
                                if quest.check_code(code):
                                    codes_tried += 1
                                else:
                                    # check_code returns False or None only if firefox was closed etc.
                                    print u' Возникла ошибка во время ввода кода. Остановка перебора...'
                                    break
                    time_finished = datetime.datetime.now()
                    print u' Перебрано кодов: %s за %s секунд' % (
                        codes_tried, str((time_finished - time_started).seconds))
                else:
                    print u' Ошибка во время логина. Остановка...'
            else:
                print u' Ошибка во время открытия адреса. Остановка...'
            try:
                quest.driver.close()
            except:
                print u' Неизвестная ошибка. Остановка...'
            self.root.deiconify()
        else:
            print u' Не задан набор кодов для перебора'

    def read_config(self, filename=CONFIG_FILENAME):
        config = ConfigParser.ConfigParser()
        if os.path.isfile(filename):
            config.read(filename)
            options = config.options(section)
            for option in options:
                SETTINGS[option][0] = config.get(section, option)
            self.read_databases_config()
        else:
            self.write_config(filename)
            self.read_config(filename)

    def write_config(self, filename=CONFIG_FILENAME):
        config = ConfigParser.ConfigParser()
        config.add_section(section)
        for key in SETTINGS:
            config.set(section, key, SETTINGS[key][0])
        with open(filename, 'wb') as config_file:
            config.write(config_file)
        self.write_databases_config()

    def call_anagrammator(self):
        self.root.withdraw()
        AnagrammForm(self)

    def read_databases_config(self, filename=DATABASES_CONFIG, section='Bases'):
        config = ConfigParser.ConfigParser()
        config.read(filename)
        options = config.options(section)
        for option in options:
            if option == 'bases':
                default_settings.DATABASES = config.get(section, option).split(';')
            if option == 'names':
                default_settings.NAMES = config.get(section, option).split(';')
            if option == 'selected':
                default_settings.selected = config.get(section, option)

    def write_databases_config(self, filename=DATABASES_CONFIG, section='Bases'):
        config = ConfigParser.ConfigParser()
        config.add_section(section)
        bases = ''
        for base in default_settings.DATABASES:
            bases += base + ';'
        bases = bases[0:len(bases) - 1]
        config.set(section, 'bases', bases)
        config.set(section, 'selected', default_settings.selected)
        names = ''
        for name in default_settings.NAMES:
            names += name + ';'
        names = names[0:len(names) - 1]
        config.set(section, 'names', names)
        with open(filename, 'wb') as config_file:
            config.write(config_file)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        codes = self.codes.get("0.0", Tkinter.END)
        self.root.clipboard_append(codes)
