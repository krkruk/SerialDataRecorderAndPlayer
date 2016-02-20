from tkinter import ttk
from tkinter import *
import tkinter.filedialog as tkd
from pandas.core.ops import _TimeOp

import serial_server as ss
import multiprocessing as mp


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

    def serial_connect_button_label(self, state):
        try:
            label = self._connect_btn_label[state]
        except IndexError:
            return
        self.connect_button_text.set(label)


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

        self.set_button_play_enable(False)
        self.set_button_record_enable(False)

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

    def button_play_label(self, state):
        try:
            label = self._play_btn_label[state]
        except IndexError:
            return
        self.play_button_text.set(label)


class MainWindow(ttk.Frame, CommandRunnable):
    def __init__(self, master=None, sendTimeInterval=1):
        ttk.Frame.__init__(self, master)
        CommandRunnable.__init__(self)
        self.recv_data = mp.Queue()
        self.load_data = []
        self.isPlaying = False
        self.sendTimeInterval = 20#sendTimeInterval
        self.server = ss.SerialServer(queue=self.recv_data, baudrate=115200)
        self.status_bar = StatusBar(master)
        self.serial_widget = SerialSelectWidget(master=self, label="Serial Select")
        self.record_play_widget = RecordPlayDataWidget(master=self, label="Data interaction")
        self.master = master
        self.master.option_add('*tearOff', False)
        self.server.start()

        self._init_menu_bar()
        self._init_widget_body()
        self.pack(fill=BOTH, padx=5, pady=5)

    def _init_menu_bar(self):
        top_menu = Menu(self.master)
        self.master["menu"] = top_menu
        file_menu = Menu(top_menu)
        data_menu = Menu(top_menu)
        help_menu = Menu(top_menu)

        top_menu.add_cascade(menu=file_menu, label="File")
        top_menu.add_cascade(menu=data_menu, label="Data")
        top_menu.add_cascade(menu=help_menu, label="Help")

        file_menu.add_command(label="Open data", command=self.menu_open)
        file_menu.add_command(label="Save data", command=self.menu_save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=exit)

        data_menu.add_command(label="Clear recorded data", command=self.menu_clear_recv_data)
        data_menu.add_command(label="Clear loaded data", command=self.menu_clear_load_data)

        help_menu.add_command(label="About", command=self.menu_about)

        self.commands["menu_open"] = self._load_data

    def _init_widget_body(self):
        self.serial_widget.commands["serial_refresh"] = lambda: (l.device for l in ss.SerialServer.list_ports())
        self.serial_widget.commands["serial_connect"] = self._connect_serial
        self.serial_widget.pack(fill=X)
        self.record_play_widget.commands["button_record"] = self._record_data
        self.record_play_widget.commands["button_play"] = self._play_data
        self.record_play_widget.pack(fill=X)

    def _connect_serial(self, port):
        if not self.server.is_server_pending():
            self.server.set_port(port)
            self.server.start_recv()
            self.record_play_widget.set_button_record_enable(True)
            self.record_play_widget.set_button_play_enable(True)
            self.after(50, lambda: True if self.server.is_server_pending() else self._connection_close(1))
            return self.server.is_server_pending()
        else:
            self._connection_close()
            return self.server.is_server_pending()

    def _connection_close(self, case=0):
        if case == 1:
            self.status_bar.set_text("Could not establish the connection...", 2000)
        self.server.stop_recv()
        self.serial_widget.serial_connect_button_label(0)
        self.record_play_widget.set_button_record_enable(False)
        self.record_play_widget.set_button_play_enable(False)

    def _load_data(self):
        self.load_data.clear()
        load = tkd.askopenfile()
        if not load:
            return False

        for line in load:
            self.load_data.append(line.rstrip())
        load.close()

    def _record_data(self):
        if self.server.is_server_pending():
            if self.server.is_recording_data():
                self.server.record_data_stop()
                return False
            else:
                self.server.record_data_start()
                return True
        return False

    def _play_data_send_method(self):

        if self.server.is_server_pending() and not self.server.is_recording_data():
            print("In sending func")
            if self.load_data and self.isPlaying:
                send_data = self.load_data.pop(1)
                self.server.send_data(send_data)
                self.after(self.sendTimeInterval, self._play_data_send_method)
                return True
        print("Nothing to play")
        self.record_play_widget.button_play_label(0)
        self.isPlaying = False
        return False

    def _play_data(self):
        if self.isPlaying:
            self.isPlaying = False
            return False
        else:
            self.isPlaying = True
            return self._play_data_send_method()

    def menu_open(self):
        self.exec_command(key="menu_open")

    def menu_save(self):
        self.exec_command(key="menu_save")
        data_list = ss.to_list(self.recv_data)
        file = tkd.asksaveasfile(mode="w")
        if not file:
            return False
        file.writelines(data_list)
        file.close()

    def menu_about(self):
        self.exec_command(key="menu_about")

    def menu_clear_recv_data(self):
        with mp.Lock():
            while not self.recv_data.empty():
                self.recv_data.get()

    def menu_clear_load_data(self):
        self.load_data.clear()

    def __del__(self):
        self.server.join()
        self.server.terminate()

