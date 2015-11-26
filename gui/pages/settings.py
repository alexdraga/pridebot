# -*- coding: utf-8 -*-
import Tkinter
import tkMessageBox

from config.default_settings import SETTINGS
from config.localization import BUTTONS, LANGUAGE
from gui.helpers.gui_helpers import center_window


__author__ = 'a_draga'


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
        self.save = Tkinter.Button(self.frame, text=BUTTONS['save'][LANGUAGE], command=self.save)
        self.save.grid(row=i + 1, column=1, sticky=Tkinter.E)
        self.cancel = Tkinter.Button(self.frame, text=BUTTONS['cancel'][LANGUAGE], command=self.cancel)
        self.cancel.grid(row=i + 1, column=1, sticky=Tkinter.W)
        self.help = Tkinter.Button(self.frame, text=BUTTONS['help'][LANGUAGE], command=self.help)
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
