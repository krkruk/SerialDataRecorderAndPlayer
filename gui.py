from tkinter import ttk
from tkinter import *
import serial_server as ss

class CommandRunnable:
    def __init__(self):
        self.commands = {}

    def exec_command(self, key, *args, **kwargs):
        try: return self.commands[key](*args, **kwargs)
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
        CommandRunnable.__init__(self)
        self._connect_btn_label = ("Connect", "Disconnect")
        self.connect_button_text = StringVar()
        self._serial_select_current_elem = StringVar()
        self._serial_select_current_elem.set("---Select---")
        self.serial_select_combo_box = ttk.Combobox(self, textvariable=self._serial_select_current_elem)
        self.serial_select_combo_box.grid(column=0, row=0, columnspan=2, padx=10, pady=5)

        self._init_buttons()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _init_buttons(self):
        refresh_button = ttk.Button(self, text="Refresh", command=self.serial_refresh)
        self.connect_button_text.set("Connect")
        connect_button = ttk.Button(self, textvariable=self.connect_button_text, command=self.serial_connect)

        refresh_button.grid(column=0, row=1, padx=5, pady=5)
        connect_button.grid(column=1, row=1, padx=5, pady=5)

    def set_combo_values(self, values):
        self._serial_select_current_elem.set("---Select---")
        self.serial_select_combo_box["values"] = tuple(values)

    def serial_refresh(self):
        serial_coms = self.exec_command("serial_refresh")
        self.set_combo_values(serial_coms)

    def serial_connect(self):
        if self.exec_command("serial_connect", port=self._serial_select_current_elem.get()):
            self.connect_button_text.set(self._connect_btn_label[1])
        else:
            self.connect_button_text.set(self._connect_btn_label[0])


class RecordPlayDataWidget(ttk.Labelframe, CommandRunnable):
    def __init__(self, master, label: str = ""):
        ttk.Labelframe.__init__(self, master=master, text=label)
        CommandRunnable.__init__(self)
        self._record_btn_label = ("Record", "Stop recording")
        self._play_btn_label = ("Play", "Stop playing")
        self.master = master
        self.record_button_text = StringVar()
        self.play_button_text = StringVar()

        self._init_buttons()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def _init_buttons(self):
        self.record_button = ttk.Button(self, textvariable=self.record_button_text, command=self.button_record)
        self.play_button = ttk.Button(self, textvariable=self.play_button_text, command=self.button_play)

        self.record_button_text.set(self._record_btn_label[0])
        self.play_button_text.set(self._play_btn_label[0])
        self.record_button.grid(column=0, row=0, padx=5, pady=5)
        self.play_button.grid(column=1, row=0, padx=5, pady=5)

    def button_record(self):
        if self.exec_command("button_record"):
            self.record_button_text.set(self._record_btn_label[1])
        else:
            self.record_button_text.set(self._record_btn_label[0])

    def button_play(self):
        if self.exec_command("button_play"):
            self.play_button_text.set(self._play_btn_label[1])
        else:
            self.play_button_text.set(self._play_btn_label[0])

    def set_button_record_enable(self, state: bool = True):
        if state:
            self.record_button["state"] = NORMAL
        else:
            self.record_button["state"] = DISABLED

    def set_button_play_enable(self, state: bool = True):
        if state:
            self.play_button["state"] = NORMAL
        else:
            self.play_button["state"] = DISABLED


class MainWindow(ttk.Frame, CommandRunnable):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        CommandRunnable.__init__(self)
        self.status_bar = StatusBar(master)
        self.serial_widget = SerialSelectWidget(master=self, label="Serial Select")
        self.record_play_widget = RecordPlayDataWidget(master=self, label="Data interaction")
        self.master = master
        self.master.option_add('*tearOff', False)
        self.serial_widget.commands["serial_refresh"] = lambda: (l.device for l in ss.SerialServer.list_ports())

        self._init_menu_bar()
        self._init_widget_body()
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

    def _init_widget_body(self):
        self.serial_widget.pack(fill=X)
        self.record_play_widget.pack(fill=X)

    def menu_open(self):
        self.exec_command(key="menu_open")

    def menu_save(self):
        self.exec_command(key="menu_save")

    def menu_about(self):
        self.exec_command(key="menu_about")
