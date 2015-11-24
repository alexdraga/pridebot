# -*- coding: utf-8 -*-
import Tkinter
import datetime
import re
import tkMessageBox

import default_settings
from gui.helpers.gui_helpers import center_window
from web.database import DBDriver


__author__ = 'a_draga'


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

        dictionaries_db = default_settings.DATABASES
        names_db = default_settings.NAMES

        self.dictionary = Tkinter.StringVar(self.root)
        self.dictionary.set(names_db[dictionaries_db.index(default_settings.selected)])  # default value

        dictionaries = apply(Tkinter.OptionMenu, (self.frame, self.dictionary) + tuple(names_db))
        # dictionaries = Tkinter.OptionMenu(self.frame, self.dictionary, dictionaries_db)
        dictionaries.grid(row=4, column=0, sticky=Tkinter.W + Tkinter.E + Tkinter.N)

        def trace_dictionary(*args):
            i = 0
            chosen = False
            for name in names_db:
                if name.decode('utf-8') == self.dictionary.get():
                    default_settings.selected = dictionaries_db[i]
                    chosen = True
                i += 1
            if not chosen:
                default_settings.selected = dictionaries_db[0]


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
            database = default_settings.selected
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
