# -*- coding: utf-8 -*-
__author__ = 'a_draga'

import os
import Tkinter
import tkMessageBox
import ConfigParser
import datetime
import itertools
import re
import string
from web.actions import QuestUA
from settings import SETTINGS, section
from web.database import DBDriver
import settings
import random


def center_window(w, h, root):
    # get screen width and height
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # calculate position x, y
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.geometry('+%d+%d' % (x, y))


class SettingsForm(object):
    def get_settings_list(self):
        settings_list = []
        for setting in SETTINGS.keys():
            settings_list.append([setting, SETTINGS[setting][0], SETTINGS[setting][1]])
        settings_list = sorted(settings_list, key=lambda k: k[2])
        return settings_list

    def __init__(self, parent):
        self.parent = parent
        self.root = Tkinter.Tk()
        self.root.title('Настройки')
        self.root.focus_force()
        self.frame = Tkinter.Frame(self.root)
        self.frame.grid(sticky=Tkinter.W + Tkinter.E + Tkinter.S + Tkinter.N)

        self.setting_entry = {}
        i = 0
        for setting in self.get_settings_list():
            label = Tkinter.Label(self.frame, text=setting[0])
            label.grid(row=i, column=0, sticky=Tkinter.W)
            entry = Tkinter.Entry(self.frame, width=50)
            entry.insert(0, setting[1])
            entry.grid(row=i, column=1, sticky=Tkinter.E)
            self.setting_entry.update({setting[0]: entry})
            i += 1
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.save = Tkinter.Button(self.frame, text='Сохранить', command=self.save)
        self.save.grid(row=i + 1, column=1, sticky=Tkinter.E)
        self.cancel = Tkinter.Button(self.frame, text='Отмена', command=self.cancel)
        self.cancel.grid(row=i + 1, column=1, sticky=Tkinter.W)
        self.help = Tkinter.Button(self.frame, text='Помощь', command=self.help)
        self.help.grid(row=i + 1, column=0, sticky=Tkinter.W + Tkinter.E)
        center_window(entry.winfo_reqwidth() + label.winfo_reqwidth(),
                      entry.winfo_reqheight() * len(self.setting_entry) + self.save.winfo_reqheight(),
                      self.root)

        self.root.mainloop()

    def on_close(self):
        self.parent.root.deiconify()
        self.root.destroy()

    def save(self):
        for key in self.setting_entry.keys():
            SETTINGS[key][0] = self.setting_entry[key].get()
        self.parent.write_config()
        self.on_close()

    def cancel(self):
        self.on_close()

    def help(self):
        message = """
        Для локаторов элементов вводите значение в формате:
        %by%=%value%
        Где возможны варианты::
        - id (для quest.ua id=txtLogin - поле логина)
        - name (для play.cq.com.ua name="code" - поле для ввода кода)
        - css
        - class
        - xpath (например: xpath=//*[@id="gbqfq"] )
        - tag
        Если не нужно выполнять логин в систему - login = ''

        Лимит числа генерируемых кодов отсутсвует, если = 0
        Обратите внимание, что генерация кодов с длиной больше 6 -
        забирает невероятно много времени. Оно того не стоит.
        """
        tkMessageBox.showinfo(title="Help", message=message)


class GenerateCodesForm(object):
    upper_latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lower_latin = 'abcdefghijklmnopqrstuvwxyz'
    upper_cyrillic = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    lower_cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    upper_ukranian = 'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'
    lower_ukrainian = 'ґії'
    digits = '0123456789'
    main_printable = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""

    def __init__(self, parent):

        self.parent = parent
        self.root = Tkinter.Tk()
        self.root.title('Генератор кодов')
        self.root.focus_force()
        self.left_frame = Tkinter.Frame(self.root)
        self.left_frame.pack(side=Tkinter.LEFT)

        label = Tkinter.Label(self.left_frame, text=' Набор символов для генерации:')
        label.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.letters_to_generate = Tkinter.Text(self.left_frame, font=("Helvetica", 12), height=10, width=30)
        self.letters_to_generate.pack(side=Tkinter.TOP)
        # self.letters_to_generate.config(size=36)

        label_reg = Tkinter.Label(self.left_frame, text=' Маска:')
        label_reg.pack(side=Tkinter.TOP, fill=Tkinter.X)
        self.regex = Tkinter.Entry(self.left_frame)
        self.regex.insert(0, '.*')
        self.regex.pack(side=Tkinter.TOP, fill=Tkinter.X)

        label_length = Tkinter.Label(self.left_frame, text=' Длина кодов (от ... до ...):')
        label_length.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.length_from = Tkinter.Entry(self.left_frame)
        self.length_from.insert(0, '1')
        self.length_from.pack(side=Tkinter.TOP, fill=Tkinter.X)
        self.length_to = Tkinter.Entry(self.left_frame)
        self.length_to.insert(0, '1')
        self.length_to.pack(side=Tkinter.TOP, fill=Tkinter.X)

        label_preview = Tkinter.Label(self.left_frame, text=' Просмотр:')
        label_preview.grid(row=0, column=0)
        label_preview.pack(side=Tkinter.TOP, fill=Tkinter.X)
        self.preview_box = Tkinter.Text(self.left_frame, font=("Helvetica", 12), height=10, width=30)
        self.preview_box.grid(row=0, column=1)

        self.scroll_bar = Tkinter.Scrollbar(self.left_frame)
        self.scroll_bar.pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH)
        self.scroll_bar.config(command=self.preview_box.yview)
        self.preview_box.config(yscrollcommand=self.scroll_bar.set)
        self.preview_box.pack(side=Tkinter.TOP)

        upper_latin_button = Tkinter.Button(self.root, text='Добавить ЛАТИНИЦУ', command=self.add_upper_latin)
        # lower_latin_button = Tkinter.Button(self.root, text='Add Lower latin', command=self.add_lower_latin)
        upper_cyrillic_button = Tkinter.Button(self.root, text='Добавить КИРИЛЛИЦУ', command=self.add_upper_cyrillic)
        # lower_cyrillic_button = Tkinter.Button(self.root, text='Add Lower cyrillic', command=self.add_lower_cyrillic)
        upper_ukrainian_button = Tkinter.Button(self.root, text='Добавить УКРАИНСКИЕ', command=self.add_upper_ukrainian)
        # lower_ukrainian_button = Tkinter.Button(self.root, text='Add Lower ukrainian', command=self.add_lower_ukrainian)
        digits_button = Tkinter.Button(self.root, text='Добавить ЦИФРЫ', command=self.add_digits)
        punctuation_latin_button = Tkinter.Button(self.root, text='Добавить ПУНКТУАЦИЮ', command=self.add_printable)

        upper_latin_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        # lower_latin_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        upper_cyrillic_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        # lower_cyrillic_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        upper_ukrainian_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        # lower_ukrainian_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        digits_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        punctuation_latin_button.pack(side=Tkinter.TOP, fill=Tkinter.X)

        preview = Tkinter.Button(self.root, text='Просмотр', command=self.preview)
        preview.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        add_button = Tkinter.Button(self.root, text='Добавить коды', command=self.add_codes)
        add_button.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        cancel_button = Tkinter.Button(self.root, text='Отмена', command=self.on_close)
        cancel_button.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)

        total_height = self.letters_to_generate.winfo_reqheight() + self.preview_box.winfo_reqheight() + \
                       self.regex.winfo_reqheight() * 3 + label.winfo_reqheight() * 4

        total_width = self.preview_box.winfo_reqwidth() + add_button.winfo_reqwidth()

        self.root.protocol('WM_DELETE_WINDOW', self.on_close)

        center_window(total_width, total_height, self.root)

        self.root.mainloop()

    def on_close(self):
        self.parent.root.deiconify()
        self.root.destroy()

    def get_all_combinations(self, letters, length):
        def join_elements(elements):
            joined = ''
            for element in elements:
                joined += element
            return joined

        r = itertools.product(letters, repeat=length)
        new_elements = []
        for t in r:
            new_elements.append(join_elements(t))
        return new_elements

    def filter_by_regex(self, codes, regex):
        regular = re.compile(regex)
        return filter(regular.match, codes)

    def add_upper_latin(self):
        self.letters_to_generate.insert(Tkinter.END, self.upper_latin)

    def add_lower_latin(self):
        self.letters_to_generate.insert(Tkinter.END, self.lower_latin)

    def add_upper_cyrillic(self):
        self.letters_to_generate.insert(Tkinter.END, self.upper_cyrillic)

    def add_lower_cyrillic(self):
        self.letters_to_generate.insert(Tkinter.END, self.lower_cyrillic)

    def add_upper_ukrainian(self):
        self.letters_to_generate.insert(Tkinter.END, self.upper_ukranian)

    def add_lower_ukrainian(self):
        self.letters_to_generate.insert(Tkinter.END, self.lower_ukrainian)

    def add_digits(self):
        self.letters_to_generate.insert(Tkinter.END, self.digits)

    def add_printable(self):
        self.letters_to_generate.insert(Tkinter.END, self.main_printable)

    def preview(self):
        letters = self.letters_to_generate.get("0.0", Tkinter.END)
        letters = letters.replace('\n', '')
        if letters:
            try:
                length_from = int(self.length_from.get())
            except:
                print u' Неверное число в поле "длина от"'
            try:
                length_to = int(self.length_to.get())
            except:
                print u' Неверное число в поле "длина до"'
            time_started = datetime.datetime.now()
            codes_generated = 0
            if length_to and length_from:
                if (self.number_of_codes(letters, length_to) < int(SETTINGS['limit_code_number'][0])) or \
                                int(SETTINGS['limit_code_number'][0]) == 0:
                    self.preview_box.delete("0.0", Tkinter.END)
                    for length in range(length_from, length_to + 1):
                        codes = self.get_all_combinations(letters, length)
                        codes_generated += self.number_of_codes(letters, length)
                        regex = self.regex.get()
                        filtered_codes = self.filter_by_regex(codes, regex)
                        for code in filtered_codes:
                            self.preview_box.insert(Tkinter.END, code + '\n')
                    time_finished = datetime.datetime.now()
                    print u' Создано %s кодов за %s секунд' % (
                        codes_generated, str((time_finished - time_started).seconds))
                else:
                    print u' Слишком много комбинаций: %s. На данный момент лимит: %s' % (
                        str(self.number_of_codes(letters, length_to)), SETTINGS['limit_code_number'][0])

    def number_of_codes(self, letters, length):
        symbol_number = len(letters)
        length = int(length)
        return pow(symbol_number, length)

    def add_codes(self):
        generated_codes = self.preview_box.get("0.0", Tkinter.END)
        self.parent.codes.insert(Tkinter.END, generated_codes)
        self.on_close()


class MainForm(object):
    def __init__(self):
        self.read_config()
        self.root = Tkinter.Tk()
        self.root.title('PrideBot')

        self.frame = Tkinter.Frame(self.root)
        self.codes = Tkinter.Text(self.frame, font=("Helvetica", 12))

        self.random = Tkinter.IntVar(self.root)

        random = Tkinter.Checkbutton(self.root, text=' В случайном порядке', variable=self.random)

        self.start_codes = Tkinter.Button(self.root, text='Начать перебор', command=self.start_brute_force)
        self.copy_to_clipboard = Tkinter.Button(self.root, text='Скопировать коды', command=self.copy_to_clipboard)
        self.scroll_bar = Tkinter.Scrollbar(self.frame)
        self.root.winfo_height()
        self.settings = Tkinter.Button(self.root, text='Настройки', command=self.call_settings)

        self.code_generator = Tkinter.Button(self.root, text='Генератор кодов', command=self.call_code_generator)
        self.db_words = Tkinter.Button(self.root, text='Анаграммы', command=self.call_anagrammator)
        self.clear_codes = Tkinter.Button(self.root, text='Очистить', command=self.clear_codes)

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

    def call_settings(self):
        self.root.withdraw()
        settings_form = SettingsForm(self)

    def clear_codes(self):
        self.codes.delete("0.0", Tkinter.END)

    def call_code_generator(self):
        self.root.withdraw()
        code_generator_form = GenerateCodesForm(self)

    def start_brute_force(self):
        codes = self.codes.get("0.0", Tkinter.END).split('\n')
        if codes != ['', ''] and codes != [''] and codes:
            time_started = datetime.datetime.now()
            # Hiding main GUI form
            self.root.withdraw()
            #Starting webdriver and performing login
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
                                #check_code returns False or None only if firefox was closed etc.
                                print u' Возникла ошибка во время ввода кода. Остановка перебора...'
                                break
                    else:
                        for code in codes:
                            if code != '':
                                print u' Пробуем код: %s' % code
                                if quest.check_code(code):
                                    codes_tried += 1
                                else:
                                    #check_code returns False or None only if firefox was closed etc.
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

    def read_config(self, filename='config.cfg'):
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

    def write_config(self, filename='config.cfg'):
        config = ConfigParser.ConfigParser()
        config.add_section(section)
        for key in SETTINGS:
            config.set(section, key, SETTINGS[key][0])
        with open(filename, 'wb') as config_file:
            config.write(config_file)
        self.write_databases_config()

    def call_anagrammator(self):
        self.root.withdraw()
        anagrammator_form = AnagrammForm(self)

    def read_databases_config(self, filename='databases.cfg', section='Bases'):
        config = ConfigParser.ConfigParser()
        config.read(filename)
        options = config.options(section)
        new_databases = []
        for option in options:
            if option == 'bases':
                settings.DATABASES = config.get(section, option).split(';')
            if option == 'names':
                settings.NAMES = config.get(section, option).split(';')
                # for name in settings.NAMES:
                # settings.NAMES[settings.NAMES.index(name)]=name.decode('utf-8')
            if option == 'selected':
                settings.selected = config.get(section, option)

    def write_databases_config(self, filename='databases.cfg', section='Bases'):
        config = ConfigParser.ConfigParser()
        config.add_section(section)
        bases = ''
        for base in settings.DATABASES:
            bases += base + ';'
        bases = bases[0:len(bases) - 1]
        config.set(section, 'bases', bases)
        config.set(section, 'selected', settings.selected)
        names = ''
        for name in settings.NAMES:
            names += name + ';'
        names = names[0:len(names) - 1]
        config.set(section, 'names', names)
        with open(filename, 'wb') as config_file:
            config.write(config_file)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        codes = self.codes.get("0.0", Tkinter.END)
        self.root.clipboard_append(codes)


class AnagrammForm(object):
    def __init__(self, parent):
        self.parent = parent
        self.root = Tkinter.Tk()
        self.root.title('Анаграммы')
        self.root.focus_force()
        self.frame = Tkinter.Frame(self.root)
        self.frame.grid()
        # self.frame.pack()
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)

        label_letters = Tkinter.Label(self.frame, text='Набор букв для анаграммирования:')
        label_letters.grid(row=0, column=0)
        # label_letters.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.letters = Tkinter.Entry(self.frame, width=50)
        self.letters.grid(row=0, column=1)
        # self.letters.insert(0, 'entry')
        # self.letters.pack(side=Tkinter.TOP, fill=Tkinter.X)

        label_length = Tkinter.Label(self.frame, text=' Длина:')
        label_length.grid(row=1, column=0)
        # label_length.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.length = Tkinter.Entry(self.frame, width=10)
        self.length.grid(row=1, column=1, sticky=Tkinter.W)
        # self.letters.insert(0, 'entry')
        # self.length.pack(side=Tkinter.TOP, fill=Tkinter.BOTH)

        label_reg = Tkinter.Label(self.frame, text=' Маска:')
        label_reg.grid(row=2, column=0, sticky=Tkinter.W)
        self.regex = Tkinter.Entry(self.frame)
        self.regex.insert(0, '.*')
        self.regex.grid(row=2, column=1, sticky=Tkinter.W)

        self.use_mask = Tkinter.IntVar(self.root)

        use_mask = Tkinter.Checkbutton(self.frame, text=' Использовать маску', variable=self.use_mask)
        use_mask.grid(row=2, column=1, sticky=Tkinter.E)

        self.strict_order = Tkinter.IntVar(self.root)

        strict_order = Tkinter.Checkbutton(self.frame, text=' Сохранять порядок букв', variable=self.strict_order)
        strict_order.grid(row=1, column=1, sticky=Tkinter.E)
        # strict_order.pack(side=Tkinter.TOP, fill=Tkinter.X)

        label_preview = Tkinter.Label(self.frame, text=' Результат поиска:')
        label_preview.grid(row=3, column=1, sticky=Tkinter.N)
        self.preview_box = Tkinter.Text(self.frame, font=("Helvetica", 12), height=10, width=30)
        self.preview_box.grid(row=4, column=1, sticky=Tkinter.S + Tkinter.W + Tkinter.E + Tkinter.N)
        #
        self.scroll_bar = Tkinter.Scrollbar(self.frame)
        self.scroll_bar.grid(row=4, column=1, sticky=Tkinter.E + Tkinter.S + Tkinter.N)
        # self.scroll_bar.pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH)
        self.scroll_bar.config(command=self.preview_box.yview)
        self.preview_box.config(yscrollcommand=self.scroll_bar.set)
        # self.preview_box.pack(side=Tkinter.BOTTOM)

        label_db = Tkinter.Label(self.frame, text=' Словарь:')
        label_db.grid(row=3, column=0, sticky=Tkinter.W)
        # label_db.pack(side=Tkinter.TOP, fill=Tkinter.X)

        # self.databases = Tkinter.Listbox(self.frame, selectmode=Tkinter.SINGLE)
        # self.databases.grid(row=4, column=0, sticky=Tkinter.S+Tkinter.W+Tkinter.E+Tkinter.N)

        dictionaries_db = settings.DATABASES
        names_db = settings.NAMES

        self.dictionary = Tkinter.StringVar(self.root)
        self.dictionary.set(names_db[dictionaries_db.index(settings.selected)])  # default value

        dictionaries = apply(Tkinter.OptionMenu, (self.frame, self.dictionary) + tuple(names_db))
        # dictionaries = Tkinter.OptionMenu(self.frame, self.dictionary, dictionaries_db)
        dictionaries.grid(row=4, column=0, sticky=Tkinter.W + Tkinter.E + Tkinter.N)

        def trace_dictionary(*args):
            i = 0
            chosen = False
            for name in names_db:
                if name.decode('utf-8') == self.dictionary.get():
                    settings.selected = dictionaries_db[i]
                    chosen = True
                i += 1
            if not chosen:
                settings.selected = dictionaries_db[0]


        self.dictionary.trace('w', trace_dictionary)

        # self.scroll_bar_db = Tkinter.Scrollbar(self.frame)
        # self.scroll_bar_db.grid(row=4, column=0, sticky=Tkinter.E+Tkinter.S+Tkinter.N)
        # self.scroll_bar_db.config(command=self.databases.yview)

        self.preview_box.config(yscrollcommand=self.scroll_bar.set)
        # for database in settings.DATABASES:
        # self.databases.insert(Tkinter.END, database)
        # self.databases.pack(side=Tkinter.TOP)
        # self.databases.selection_set(self.databases.get(0, Tkinter.END).index(settings.selected))

        do_anagramm = Tkinter.Button(self.frame, text='Поиск слов', command=self.preview)
        do_anagramm.grid(row=5, column=1, sticky=Tkinter.E)
        # do_anagramm.pack(side=Tkinter.RIGHT, fill=Tkinter.X)

        add_button = Tkinter.Button(self.frame, text='Добавить коды', command=self.add_codes)
        add_button.grid(row=5, column=1)
        # add_button.pack(side=Tkinter.RIGHT)
        cancel_button = Tkinter.Button(self.frame, text='Отмена', command=self.on_close)
        cancel_button.grid(row=5, column=0, sticky=Tkinter.W)
        # cancel_button.pack(side=Tkinter.LEFT)

        help_button = Tkinter.Button(self.frame, text='Помощь', command=self.help)
        help_button.grid(row=5, column=1, sticky=Tkinter.W)

        width = label_letters.winfo_reqwidth() + self.letters.winfo_reqwidth()
        height = self.length.winfo_reqheight() * 3 + label_db.winfo_reqheight() + self.preview_box.winfo_reqheight() + \
                 add_button.winfo_reqheight()
        center_window(width,
                      height, self.root)

        self.root.mainloop()


    def on_close(self):
        self.parent.root.deiconify()
        self.root.destroy()


    def preview(self):
        letters = self.letters.get()
        letters = letters.replace(' ', '')
        if letters:
            database = settings.selected
            db = DBDriver(database)
            if self.strict_order.get():
                time_started = datetime.datetime.now()
                results = db.perform_strict_order(letters, self.length.get())
                time_finished = datetime.datetime.now()
            else:
                if self.length.get():
                    time_started = datetime.datetime.now()
                    results = db.perform_anagramm(letters, self.length.get())
                    time_finished = datetime.datetime.now()
                else:
                    time_started = datetime.datetime.now()
                    results = db.perform_anagramm(letters)
                    time_finished = datetime.datetime.now()
            self.preview_box.delete("0.0", Tkinter.END)
            if results:
                print u'Найдено кодов в словаре: %s за %s секунд' % (
                    len(results), str((time_finished - time_started).seconds))
                if self.use_mask.get():
                    # Perform filter by regex-mask
                    regex = self.regex.get()
                    results = self.filter_by_regex(results, regex)
                    print u' Отфильтровано слов: %s за %s секунд' % (
                        len(results), str((time_finished - time_started).seconds))
                for result in results:
                    self.preview_box.insert(Tkinter.END, result + '\n')
            else:
                print u'Не найдено слов, удовлетворяющих запрос'

    def add_codes(self):
        generated_codes = self.preview_box.get("0.0", Tkinter.END)
        self.parent.codes.insert(Tkinter.END, generated_codes)
        self.on_close()

    def filter_by_regex(self, codes, regex):
        regular = re.compile(regex)
        return filter(regular.match, codes)

    def help(self):
        message = """
        Чтобы вывести все коды из словаря - укажите только %
        В поле длины можно указать:
            =0 - анаграмма будет делаться только из букв, введеных в поле ввода
            <4, >4 - длина генерируемых слов больше или меньше указанного числа

        Также, можно делать SQL инъекции, например, если ввести:
            <10 AND LEN(word)>5 - в результате будут все слова,
            длина которых между 5 и 10 символами.
         Для инъекции можно использовать имя столбца word - в нем хранятся слова.

        В маске используются регулярные выражения
        Основы:
            . - любая буква один раз
            .* - сколько угодно каких угодно букв
            .+ - 1 и больше каких угодно букв
            ^ - начало строки
            $ - конец строки
            [A-Z] - набор букв
        Поиск с учетом регистра!

        Например, чтобы найти все слова, которые начинаются
        на дра и заканчиваются на га:
            1. В поле "Буквы для анаграммы" вводим %
            2. В поле маска вводим:
                ^дра.*га$
            3. Ставим галочку "Использовать маску"
                ...
            Профит!

            Если надо найти все слова, внутри которых есть дра.*га - можно записать так:
            дра.*га
        """
        tkMessageBox.showinfo(title="Help", message=message)