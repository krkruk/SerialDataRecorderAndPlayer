from gui import *
import tkinter as tk

flag = False


def flagFunc():
    global flag
    print("In func")
    flag = not flag
    return flag


def main():
    root = tk.Tk()
    gui = MainWindow(root)
    gui.commands["open"] = lambda: print("This is lambda")
    gui.serial_widget.commands["serial_start"] = flagFunc

    gui.status_bar.set_text("Hello")
    root.mainloop()


if __name__ == "__main__":
    main()
