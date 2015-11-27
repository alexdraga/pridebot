import os
import datetime
import random

import Tkinter
import ConfigParser

from config import CONFIG_FILENAME, DATABASES_CONFIG, default_settings
from config.default_settings import SETTINGS, section
from config.localization import BUTTONS, LANGUAGE, LOGS, HEADERS
from gui.pages.anagrams import AnagramForm
from gui.pages.code_generator import GenerateCodesForm
from gui.pages.settings import SettingsForm
from gui.helpers.gui_helpers import center_window
from web.actions import Quest


class MainForm(object):
    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.title(HEADERS['main'][LANGUAGE])

        self.frame = Tkinter.Frame(self.root)
        self.codes = Tkinter.Text(self.frame, font=("Helvetica", 12))
        self.scroll_bar = Tkinter.Scrollbar(self.frame)

        # Buttons for open windows
        self.settings = Tkinter.Button(self.root,
                                       text=BUTTONS['settings'][LANGUAGE],
                                       command=self.call_settings)
        self.code_generator = Tkinter.Button(self.root,
                                             text=BUTTONS['code_generator'][LANGUAGE],
                                             command=self.call_code_generator)
        self.anagrams = Tkinter.Button(self.root,
                                       text=BUTTONS['anagrams'][LANGUAGE],
                                       command=self.call_anagrams)

        # Operating with codes buttons
        self.enter_codes_randomly = Tkinter.IntVar(self.root)
        self.random_check_box = Tkinter.Checkbutton(self.root,
                                                    text=BUTTONS['enter_in_random_order'][LANGUAGE],
                                                    variable=self.enter_codes_randomly)
        self.copy_to_clipboard = Tkinter.Button(self.root,
                                                text=BUTTONS['copy_codes'][LANGUAGE],
                                                command=self.copy_to_clipboard)
        self.clear_codes = Tkinter.Button(self.root,
                                          text=BUTTONS['clear'][LANGUAGE],
                                          command=self.clear_codes)
        self.start_brute_force = Tkinter.Button(self.root,
                                                text=BUTTONS['start_brute_force'][LANGUAGE],
                                                command=self.start_brute_force)
        # Packing elements
        self.frame.pack(fill=Tkinter.BOTH, expand=Tkinter.YES)
        self.start_brute_force.pack(side=Tkinter.RIGHT)
        self.random_check_box.pack(side=Tkinter.RIGHT)
        self.copy_to_clipboard.pack(side=Tkinter.RIGHT)
        self.settings.pack(side=Tkinter.LEFT)
        self.code_generator.pack(side=Tkinter.LEFT)
        self.anagrams.pack(side=Tkinter.LEFT)
        self.clear_codes.pack(side=Tkinter.RIGHT)
        self.scroll_bar.pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH)
        self.codes.pack(fill=Tkinter.BOTH, expand=Tkinter.YES)

        self.scroll_bar.config(command=self.codes.yview)
        self.codes.config(yscrollcommand=self.scroll_bar.set)
        center_window(self.codes.winfo_reqwidth() + self.scroll_bar.winfo_reqwidth(),
                      self.codes.winfo_reqheight() + self.settings.winfo_reqheight(), self.root)

        self.read_config()
        self.root.mainloop()
        self.write_config()

    # region Windows callers

    def call_anagrams(self):
        self.root.withdraw()
        AnagramForm(self)

    def call_code_generator(self):
        self.root.withdraw()
        GenerateCodesForm(self)

    def call_settings(self):
        self.root.withdraw()
        SettingsForm(self)

    # endregion

    # region Config operations

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

    # endregion

    # region Operations with codes

    def clear_codes(self):
        self.codes.delete("0.0", Tkinter.END)

    def copy_to_clipboard(self):
        self.codes.insert(Tkinter.END, self.root.clipboard_get())
        self.root.clipboard_clear()
        codes = self.codes.get("0.0", Tkinter.END)
        self.root.clipboard_append(codes)

    def copy_from_clipboard(self):
        self.codes.insert(Tkinter.END, self.root.clipboard_get())

    # endregion

    def start_brute_force(self):
        codes = self.codes.get("0.0", Tkinter.END).split('\n')
        if codes != ['', ''] and codes != [''] and codes:
            time_started = datetime.datetime.now()
            # Hiding main GUI form
            self.root.withdraw()
            # Starting webdriver and performing login
            quest = Quest()
            if quest.is_url_opened:
                if quest.is_login_performed:
                    codes_tried = 0

                    if self.enter_codes_randomly.get():
                        random.shuffle(codes)
                    for code in codes:
                        if code != '':
                            print LOGS["trying_code"][LANGUAGE] % code
                            if quest.check_code(code):
                                codes_tried += 1
                            else:
                                # check_code returns False or None only if firefox was closed etc.
                                print LOGS["error_occurred_stopping"][LANGUAGE]
                                break
                    time_finished = datetime.datetime.now()
                    print LOGS["codes_tried"][LANGUAGE] % (
                        codes_tried, str((time_finished - time_started).seconds))
                else:
                    print LOGS["error_during_login"][LANGUAGE]
            else:
                print LOGS["error_during_opening_url"][LANGUAGE]
            try:
                quest.driver.close()
            except:
                print LOGS["unknown_error"][LANGUAGE]
            self.root.deiconify()
        else:
            print LOGS["no_codes_for_bruteforce"][LANGUAGE]
