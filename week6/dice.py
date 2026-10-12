import tkinter as tk
from tkinter import Frame, Label, Button
from tkinter.constants import TRUE
#from number_entry import IntEntry
import random

def main():
    root=tk.Tk()
    frm_main = Frame(root)
    frm_main.master.title("Dice")
    frm_main.pack(padx=3, pady=3, fill=tk.BOTH, expand=True)
    setup_main(frm_main)
    frm_main.mainloop()

def setup_main(frm):
    lbl_sides=Label(frm, text="Enter the number of sides on the dice 2-20")
    



if __name__ ==  "__main__":
    main()