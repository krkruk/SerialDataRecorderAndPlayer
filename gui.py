from tkinter import ttk
from tkinter import *

class CommandRunnable:
    def __init__(self):
        pass

    def exec_command(self, key):
        try: return self.commands[key]()
        except KeyError: print("No key '{}' detected".format(key))


class StatusBar(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.pack(side=BOTTOM, fill=X)
        self.master = master
        self.status_bar_label = StringVar()

        self.label = ttk.Label(self, textvariable=self.status_bar_label,
                               relief=SUNKEN, anchor=W)

        self.label.pack(fill=X)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    def set_text(self, text, timeout=0):
        self.status_bar_label.set(text)
        if timeout:
            self.after(ms=timeout, func=self.clear_text)

    def clear_text(self):
        self.status_bar_label.set("")


class SerialSelectWidget(ttk.Labelframe, CommandRunnable):
    def __init__(self, master=None, label: str = ""):
        ttk.Labelframe.__init__(self, master, text=label)
        self.commands = {}
        self.start_button_text = StringVar()
        self.serial_select_combo_box = ttk.Combobox(self)
        self.serial_select_combo_box.grid(column=0, row=0, columnspan=2, padx=10, pady=5)

        self._init_buttons()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _init_buttons(self):
        refresh_button = ttk.Button(self, text="Refresh", command=self.serial_refresh)
        self.start_button_text.set("Start")
        connect_button = ttk.Button(self, textvariable=self.start_button_text, command=self.serial_start)

        refresh_button.grid(column=0, row=1, padx=5, pady=5)
        connect_button.grid(column=1, row=1, padx=5, pady=5)

    def set_combo_values(self, values):
        self.serial_select_combo_box["values"] = tuple(values)

    def serial_refresh(self):
        self.exec_command("serial_refresh")

    def serial_start(self):
        if self.exec_command("serial_start"):
            self.start_button_text.set("Stop")
        else:
            self.start_button_text.set("Start")


class MainWindow(ttk.Frame, CommandRunnable):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.commands = {}
        self.status_bar = StatusBar(master)
        self.serial_widget = SerialSelectWidget(master=self, label="Serial Select")
        self.master = master
        self.master.option_add('*tearOff', False)

        self._init_menu_bar()
        self._init_buttons()
        self.pack(fill=BOTH, padx=5, pady=5)

    def _init_menu_bar(self):
        top_menu = Menu(self.master)
        self.master["menu"] = top_menu
        file_menu = Menu(top_menu)
        help_menu = Menu(top_menu)

        top_menu.add_cascade(menu=file_menu, label="File")
        top_menu.add_cascade(menu=help_menu, label="Help")

        file_menu.add_command(label="Open", command=self.menu_open)
        file_menu.add_command(label="Save current data", command=self.menu_save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=exit)

        help_menu.add_command(label="About", command=self.menu_about)

    def _init_buttons(self):
        self.serial_widget.pack(fill=X)

    def menu_open(self):
        self.exec_command(key="menu_open")

    def menu_save(self):
        self.exec_command(key="menu_save")

    def menu_about(self):
        self.exec_command(key="menu_about")
