from gui import *
import tkinter as tk


def main():
    root = tk.Tk()
    root.wm_title("Drone flight recorder")
    gui = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
