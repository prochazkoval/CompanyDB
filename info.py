try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import variables as var

class InfoPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        header_info = tk.Frame(self, bg=var.dark)
        content_info = tk.Frame(self)
        footer_info = tk.Frame(self)

        header_info.pack(fill="x", expand=False)
        content_info.pack(fill=tk.BOTH, expand=True)
        footer_info.pack(fill="x", expand=False)

        label1 = tk.Label(master=header_info, text="Informace o aplikaci", font=controller.title_header_font, bg=var.dark, fg=var.white)
        label1.pack(side="left", fill="x", pady=10, padx=10)

        label3 = tk.Label(master=content_info, text="Aplikace byla vytvořena na základě zkušeností a požadavků společnosti. Rok výroby 2020-2021.\n\nPěkný den všem, Lenka",
                          font=controller.title_text_font, anchor='nw', justify=tk.LEFT)
        label3.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        label4 = tk.Label(footer_info, text=var.version, font=controller.title_text_font)
        label4.pack(side="left", padx=10)
        label2 = tk.Label(footer_info, text=var.company, font=controller.title_text_font)
        label2.pack(side="right", padx=10)
        return
