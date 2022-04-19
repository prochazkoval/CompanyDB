try:
    # Python2
    import Tkinter as tk
    import ttk
except ImportError:
    # Python3
    import tkinter as tk
    import tkinter.ttk as ttk
import variables as var
import company_DB as company
import lesson, lector, student, payment


class MenuPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        center_menu = tk.Frame(self)
        center_menu.pack(fill=tk.BOTH, expand=True)
        footer_menu = tk.Frame(self)
        footer_menu.pack(fill="x", expand=False)

        center_menu_left = tk.Frame(center_menu)
        center_menu_left.pack(fill=tk.BOTH, expand=True, side="left")
        center_menu_right = tk.Frame(center_menu)
        center_menu_right.pack(fill=tk.BOTH, expand=True, side="right")

        button_style = ttk.Style()
        button_style.configure("menu.TButton", font=("DejaVu Sans", 18, "bold"), background=var.light, foreground=var.dark)

        global button1
        """button1 = ttk.Button(center_menu_left, text="\nLektoři\n", font=self.controller.title_header_font, command=lambda: [self.controller.raise_frame("LectorPage"), company.Main.resize(
            self.controller), lector.LectorPage.show_lectors(self.parent), lector.LectorPage.show_lectors_money(self.parent)])"""
        button1 = ttk.Button(center_menu_left, text="\nLektoři\n", style="menu.TButton",
                            command=lambda: [self.controller.raise_frame("LectorPage"), company.Main.resize(self.controller), lector.LectorPage.show_lectors(
                                self.parent), lector.LectorPage.show_lectors_money(self.parent)])
        button1.pack(side="top", fill=tk.BOTH, pady=10, padx=10, expand="YES")
        # button1.bind("<Enter>", self.entered1)
        # button1.bind("<Leave>", self.left1)

        global button2
        button2 = ttk.Button(center_menu_right, text="\nStudenti\n", style="menu.TButton",
                            command=lambda: [self.controller.raise_frame("StudentPage"), company.Main.resize(self.controller),
                                             student.StudentPage.show_students(self.parent), student.StudentPage.show_students_money(self.parent)])
        button2.pack(side="top", fill=tk.BOTH, pady=10, padx=10, expand="YES")
        # button2.bind("<Enter>", self.entered2)
        # button2.bind("<Leave>", self.left2)

        global button3
        button3 = ttk.Button(center_menu_right, text="\nPlatby\n", style="menu.TButton",
                            command=lambda: [self.controller.raise_frame("PaymentPage"), company.Main.resize(self.controller),
                                             payment.PaymentPage.show_payment(self.parent)])
        button3.pack(side="bottom", fill=tk.BOTH, pady=10, padx=10, expand="YES")
        # button3.bind("<Enter>", self.entered3)
        # button3.bind("<Leave>", self.left3)

        global button4
        button4 = ttk.Button(center_menu_left, text="\nLekce\n", style="menu.TButton",
                            command=lambda: [self.controller.raise_frame("LessonPage"), company.Main.resize(self.controller), lesson.LessonPage.show_lesson(
                                self.parent)])
        button4.pack(side="bottom", fill=tk.BOTH, pady=10, padx=10, expand="YES")
        # button4.bind("<Enter>", self.entered4)
        # button4.bind("<Leave>", self.left4)

        label_brand = tk.Label(footer_menu, text=var.company, font=controller.title_text_font)
        label_brand.pack(side="right", padx=10)

        label2 = tk.Label(footer_menu, text=var.version, font=controller.title_text_font)
        label2.pack(side="left", padx=10)
        return
