from os import path
import datetime
import re

import Tkinter
import tkMessageBox

from config import default_settings, DATABASES_FOLDER
from config.localization import BUTTONS, LANGUAGE, LABELS, HELPERS, LOGS, HEADERS
from gui.helpers.gui_helpers import center_window
from web.database import DBDriver


class AnagramForm(object):
    def __init__(self, parent):
        self.parent = parent
        self.root = Tkinter.Tk()
        self.root.title(HEADERS['anagrams'][LANGUAGE])
        self.root.focus_force()

        self.frame = Tkinter.Frame(self.root)
        self.frame.grid()
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)

        label_letters = Tkinter.Label(self.frame, text=LABELS['anagrams_letters'][LANGUAGE])
        label_letters.grid(row=0, column=0)
        self.letters = Tkinter.Entry(self.frame, width=50)
        self.letters.grid(row=0, column=1)

        label_length = Tkinter.Label(self.frame, text=LABELS['length'][LANGUAGE])
        label_length.grid(row=1, column=0)
        self.length = Tkinter.Entry(self.frame, width=10)
        self.length.grid(row=1, column=1, sticky=Tkinter.W)

        label_reg = Tkinter.Label(self.frame, text=LABELS['mask'][LANGUAGE])
        label_reg.grid(row=2, column=0, sticky=Tkinter.W)
        self.regex = Tkinter.Entry(self.frame)
        self.regex.insert(0, '.*')
        self.regex.grid(row=2, column=1, sticky=Tkinter.W)

        self.use_mask = Tkinter.IntVar(self.root)
        use_mask = Tkinter.Checkbutton(self.frame, text=LABELS['use_mask'][LANGUAGE], variable=self.use_mask)
        use_mask.grid(row=2, column=1, sticky=Tkinter.E)

        self.strict_order = Tkinter.IntVar(self.root)
        strict_order = Tkinter.Checkbutton(self.frame, text=LABELS['leave_order'][LANGUAGE], variable=self.strict_order)
        strict_order.grid(row=1, column=1, sticky=Tkinter.E)

        label_preview = Tkinter.Label(self.frame, text=LABELS['search_result'][LANGUAGE])
        label_preview.grid(row=3, column=1, sticky=Tkinter.N)
        self.preview_box = Tkinter.Text(self.frame, font=("Helvetica", 12), height=10, width=30)
        self.preview_box.grid(row=4, column=1, sticky=Tkinter.S + Tkinter.W + Tkinter.E + Tkinter.N)
        self.scroll_bar = Tkinter.Scrollbar(self.frame)
        self.scroll_bar.grid(row=4, column=1, sticky=Tkinter.E + Tkinter.S + Tkinter.N)
        self.scroll_bar.config(command=self.preview_box.yview)
        self.preview_box.config(yscrollcommand=self.scroll_bar.set)

        label_db = Tkinter.Label(self.frame, text=LABELS['dictionary'][LANGUAGE])
        label_db.grid(row=3, column=0, sticky=Tkinter.W)

        dictionaries_db = default_settings.DATABASES
        names_db = default_settings.NAMES

        self.dictionary = Tkinter.StringVar(self.root)
        self.dictionary.set(names_db[dictionaries_db.index(default_settings.selected)])  # default value

        dictionaries = apply(Tkinter.OptionMenu, (self.frame, self.dictionary) + tuple(names_db))
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

        self.preview_box.config(yscrollcommand=self.scroll_bar.set)

        do_anagram = Tkinter.Button(self.frame,
                                    text=BUTTONS['search_words'][LANGUAGE],
                                    command=self.preview)
        do_anagram.grid(row=5, column=1, sticky=Tkinter.E)

        add_button = Tkinter.Button(self.frame,
                                    text=BUTTONS['add_codes'][LANGUAGE],
                                    command=self.add_codes)
        add_button.grid(row=5, column=1)
        cancel_button = Tkinter.Button(self.frame,
                                       text=BUTTONS['cancel'][LANGUAGE],
                                       command=self.on_close)
        cancel_button.grid(row=5, column=0, sticky=Tkinter.W)

        help_button = Tkinter.Button(self.frame,
                                     text=BUTTONS['help'][LANGUAGE],
                                     command=self.help)
        help_button.grid(row=5, column=1, sticky=Tkinter.W)

        width = label_letters.winfo_reqwidth() + self.letters.winfo_reqwidth()
        height = self.length.winfo_reqheight() * 3 + label_db.winfo_reqheight() + \
            self.preview_box.winfo_reqheight() + add_button.winfo_reqheight()
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
            database = path.join(DATABASES_FOLDER, default_settings.selected)
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
                print LOGS["codes_found"][LANGUAGE] % (
                    len(results), str((time_finished - time_started).seconds))
                if self.use_mask.get():
                    # Perform filter by regex-mask
                    regex = self.regex.get()
                    results = self.filter_by_regex(results, regex)
                    print LOGS["words_filtered"][LANGUAGE] % (
                        len(results), str((time_finished - time_started).seconds))
                for result in results:
                    self.preview_box.insert(Tkinter.END, result + '\n')
            else:
                print LOGS["no_words_found"][LANGUAGE]

    def add_codes(self):
        generated_codes = self.preview_box.get("0.0", Tkinter.END)
        self.parent.codes.insert(Tkinter.END, generated_codes)
        self.on_close()

    def filter_by_regex(self, codes, regex):
        regular = re.compile(regex)
        return filter(regular.match, codes)

    def help(self):
        message = HELPERS['anagram'][LANGUAGE]
        tkMessageBox.showinfo(title="Help", message=message)
