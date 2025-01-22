import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

def process_dropped_file(event):
    print(f"File dropped: {event.data}")

root = TkinterDnD.Tk()
root.geometry("300x200")
root.title("Drag and Drop Test")

label = tk.Label(root, text="Drag a file here", bg="lightgrey", width=40, height=10)
label.pack(padx=20, pady=20)

# Enable drag and drop
label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', process_dropped_file)

root.mainloop()
