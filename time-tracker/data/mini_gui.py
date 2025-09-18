import os; os.environ["TK_SILENCE_DEPRECATION"] = "1"
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Mini GUI テスト")
ttk.Label(root, text="Mini GUI は表示される？", padding=16).pack()
ttk.Button(root, text="閉じる", command=root.destroy).pack(pady=8)
root.mainloop()