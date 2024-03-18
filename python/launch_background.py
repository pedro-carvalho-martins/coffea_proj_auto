import tkinter as tk

root = tk.Tk()
root.geometry('320x440')
root.resizable(False, False)
root.attributes('-fullscreen', True)

# Create a label widget
label = tk.Label(
    root,
    text="Inicialização",
    font=('SegoeUI', 20),
    wraplength=300)

label.pack()

root.mainloop()