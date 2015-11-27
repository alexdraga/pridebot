# -*- coding: utf-8 -*-
import Tkinter
import datetime
import itertools
import re

from config.default_settings import SETTINGS
from gui.helpers.gui_helpers import center_window
from config.localization import BUTTONS, LANGUAGE, LABELS, LOGS

__author__ = 'a_draga'


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
        self.root.title(LABELS['code_generator'][LANGUAGE])
        self.root.focus_force()
        self.left_frame = Tkinter.Frame(self.root)
        self.left_frame.pack(side=Tkinter.LEFT)

        label = Tkinter.Label(self.left_frame, text=LABELS['symbols_to_generate'][LANGUAGE])
        label.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.letters_to_generate = Tkinter.Text(self.left_frame, font=("Helvetica", 12), height=10, width=30)
        self.letters_to_generate.pack(side=Tkinter.TOP)
        # self.letters_to_generate.config(size=36)

        label_reg = Tkinter.Label(self.left_frame, text=LABELS['mask'][LANGUAGE])
        label_reg.pack(side=Tkinter.TOP, fill=Tkinter.X)
        self.regex = Tkinter.Entry(self.left_frame)
        self.regex.insert(0, '.*')
        self.regex.pack(side=Tkinter.TOP, fill=Tkinter.X)

        label_length = Tkinter.Label(self.left_frame, text=LABELS['codes_length'][LANGUAGE])
        label_length.pack(side=Tkinter.TOP, fill=Tkinter.X)

        self.length_from = Tkinter.Entry(self.left_frame)
        self.length_from.insert(0, '1')
        self.length_from.pack(side=Tkinter.TOP, fill=Tkinter.X)
        self.length_to = Tkinter.Entry(self.left_frame)
        self.length_to.insert(0, '1')
        self.length_to.pack(side=Tkinter.TOP, fill=Tkinter.X)

        label_preview = Tkinter.Label(self.left_frame, text=LABELS['preview'][LANGUAGE])
        label_preview.grid(row=0, column=0)
        label_preview.pack(side=Tkinter.TOP, fill=Tkinter.X)
        self.preview_box = Tkinter.Text(self.left_frame, font=("Helvetica", 12), height=10, width=30)
        self.preview_box.grid(row=0, column=1)

        self.scroll_bar = Tkinter.Scrollbar(self.left_frame)
        self.scroll_bar.pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH)
        self.scroll_bar.config(command=self.preview_box.yview)
        self.preview_box.config(yscrollcommand=self.scroll_bar.set)
        self.preview_box.pack(side=Tkinter.TOP)

        upper_latin_button = Tkinter.Button(self.root, text=BUTTONS['add_latin'][LANGUAGE],
                                            command=self.add_upper_latin)
        # lower_latin_button = Tkinter.Button(self.root, text='Add Lower latin', command=self.add_lower_latin)
        upper_cyrillic_button = Tkinter.Button(self.root, text=BUTTONS['add_cyrillic'][LANGUAGE],
                                               command=self.add_upper_cyrillic)
        # lower_cyrillic_button = Tkinter.Button(self.root, text='Add Lower cyrillic', command=self.add_lower_cyrillic)
        upper_ukrainian_button = Tkinter.Button(self.root, text=BUTTONS['add_ukrainian'][LANGUAGE],
                                                command=self.add_upper_ukrainian)
        # lower_ukrainian_button = Tkinter.Button(self.root, text='Add Lower ukrainian', command=self.add_lower_ukrainian)
        digits_button = Tkinter.Button(self.root, text=BUTTONS['add_digits'][LANGUAGE], command=self.add_digits)
        punctuation_latin_button = Tkinter.Button(self.root, text=BUTTONS['add_symbols'][LANGUAGE],
                                                  command=self.add_printable)

        upper_latin_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        # lower_latin_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        upper_cyrillic_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        # lower_cyrillic_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        upper_ukrainian_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        # lower_ukrainian_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        digits_button.pack(side=Tkinter.TOP, fill=Tkinter.X)
        punctuation_latin_button.pack(side=Tkinter.TOP, fill=Tkinter.X)

        preview = Tkinter.Button(self.root, text=BUTTONS['preview'][LANGUAGE], command=self.preview)
        preview.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        add_button = Tkinter.Button(self.root, text=BUTTONS['add_codes'][LANGUAGE], command=self.add_codes)
        add_button.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        cancel_button = Tkinter.Button(self.root, text=BUTTONS['cancel'][LANGUAGE], command=self.on_close)
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
            except ValueError:
                print LOGS["wrong_field_length_from"][LANGUAGE]
                return
            try:
                length_to = int(self.length_to.get())
            except ValueError:
                print LOGS["wrong_field_length_to"][LANGUAGE]
                return
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
                    print LOGS["created_codes"][LANGUAGE] % (
                        codes_generated, str((time_finished - time_started).seconds))
                else:
                    print LOGS["limit_exceeded"][LANGUAGE] % (
                        str(self.number_of_codes(letters, length_to)), SETTINGS['limit_code_number'][0])

    def number_of_codes(self, letters, length):
        symbol_number = len(letters)
        length = int(length)
        return pow(symbol_number, length)

    def add_codes(self):
        generated_codes = self.preview_box.get("0.0", Tkinter.END)
        self.parent.codes.insert(Tkinter.END, generated_codes)
        self.on_close()
