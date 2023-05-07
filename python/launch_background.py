import tkinter as tk

root = tk.Tk()
root.geometry('320x480')
root.resizable(False, False)
root.attributes('-fullscreen', True)

# Create a label widget
label = tk.Label(
    root,
    text="Background_test.",
    font=('SegoeUI', 20),
    wraplength=300)

label.pack()

root.mainloop()