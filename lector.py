import os
import re
from builtins import print

try:
    # Python2
    import Tkinter as tk
    import ttk
except ImportError:
    # Python3
    import tkinter as tk
    import tkinter.ttk as ttk
from tkinter import messagebox

import sqlite3
import variables as var
import utils as utils

from reportlab.lib.units import mm
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, TableStyle, Image, Spacer, Paragraph, Frame
from reportlab.platypus.tables import Table
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics


# TODO: pro import do PDF je potreba nainstalovat ReportLab
# pip install reportlab

class LectorPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        global content_lector_notebook
        header_lector = tk.Frame(self, bg=var.dark)
        content_lector_notebook = ttk.Notebook(self)
        footer_lector = tk.Frame(self)

        header_lector.pack(fill="x", expand=False)
        content_lector_notebook.pack(fill=tk.BOTH, expand=True)
        content_lector_notebook.bind('<Button-1>', self.notebook_on_click)
        footer_lector.pack(fill="x", expand=False)

        content_lector = tk.Frame(content_lector_notebook)
        content_lector.pack(fill=tk.BOTH, expand=True)

        money_lector = tk.Frame(content_lector_notebook, bg=var.orange)
        money_lector.pack(fill=tk.BOTH, expand=True)

        content_lector_notebook.add(content_lector, text=" Přehled lektorů ")
        content_lector_notebook.add(money_lector, text=" Přehled zisku lektorů ", state="normal")

        label1 = tk.Label(master=header_lector, text="Lektoři", font=controller.title_header_font, fg=var.white, bg=var.dark)
        label1.pack(side="left", fill="x", pady=10, padx=10)

        b3 = ttk.Button(header_lector, text="Filtrovat", command=lambda: self.filter_lectors(entry.get("1.0", 'end-1c')))
        b3.pack(side="right", pady=10, padx=10)

        global entry
        entry = tk.Text(header_lector, width=16, height=1)
        entry.insert(tk.END, "Jméno lektora")
        entry.pack(side="right", pady=10, padx=10)
        entry.bind("<FocusIn>", self.default_text_entry)
        entry.bind("<FocusOut>", self.default_text_entry)
        entry.bind("<Return>", self.filter_lectors_entry)

        global year_option_money
        year_option_money = ttk.Combobox(header_lector, value=var.year, state="disabled", width=5)
        year_option_money.current(var.year.index(var.year_date))
        year_option_money.pack(side="right", pady=10, padx=1)
        year_option_money.bind("<<ComboboxSelected>>", self.combobox_year_month_selected_money)

        global month_option_money
        month_option_money = ttk.Combobox(header_lector, value=var.month, state="disabled", width=10)
        month_option_money.current(var.month_index)
        month_option_money.pack(side="right", pady=10, padx=1)
        month_option_money.bind("<<ComboboxSelected>>", self.combobox_year_month_selected_money)

        label3 = tk.Label(master=header_lector, text="\t", bg=var.dark)
        label3.pack(side="right", fill="x")

        b1 = ttk.Button(header_lector, text="Přidat lektora", command=lambda: self.open_add_lector())
        b1.pack(side="left", pady=10, padx=10)

        b2 = ttk.Button(header_lector, text="Hodinová sazba", command=lambda: self.show_rate_frame())
        b2.pack(side="left", pady=10, padx=10)

        global t_tree
        t_scrollbar = ttk.Scrollbar(content_lector)
        t_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        t_scrollbar_x = tk.Scrollbar(content_lector, orient=tk.HORIZONTAL)
        t_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        t_tree = ttk.Treeview(content_lector, columns=("name", "mail", "phone", "birth", "info"), yscrollcommand=t_scrollbar.set,
                              xscrollcommand=t_scrollbar_x.set)
        t_scrollbar_x.config(command=t_tree.xview)
        t_scrollbar.config(command=t_tree.yview)

        t_tree.bind("<Double-1>", self.lector_detail_tree)
        t_tree.column("#0", width=45, minwidth=15, anchor="w", stretch="NO")
        t_tree.column("name", width=200, minwidth=150, anchor="w", stretch="NO")
        t_tree.column("mail", width=200, minwidth=100, anchor="w", stretch="NO")
        t_tree.column("phone", width=130, minwidth=100, anchor="w", stretch="NO")
        t_tree.column("birth", width=100, minwidth=100, anchor="w", stretch="NO")
        t_tree.column("info", width=200, minwidth=100, anchor="w", stretch="YES")

        t_tree.heading("#0", text="ID", anchor="w")
        t_tree.heading("name", text="Jméno a příjmení", anchor="w")
        t_tree.heading("mail", text="Mail", anchor="w")
        t_tree.heading("phone", text="Telefonní číslo", anchor="w")
        t_tree.heading("birth", text="Datum narození", anchor="w")
        t_tree.heading("info", text="Dodatečné informace", anchor="w")

        t_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        global t_tree_money
        t_scrollbar_money = ttk.Scrollbar(money_lector)
        t_scrollbar_money.pack(side=tk.RIGHT, fill=tk.Y)
        t_scrollbar_x_money = tk.Scrollbar(money_lector, orient=tk.HORIZONTAL)
        t_scrollbar_x_money.pack(side=tk.BOTTOM, fill=tk.X)
        t_tree_money = ttk.Treeview(money_lector, columns=("name", "money"), yscrollcommand=t_scrollbar_money.set,
                                    xscrollcommand=t_scrollbar_x_money.set)
        t_scrollbar_x_money.config(command=t_tree_money.xview)
        t_scrollbar_money.config(command=t_tree_money.yview)

        # t_tree_money.bind("<Double-1>", self.lector_detail_tree)
        t_tree_money.column("#0", width=45, minwidth=15, anchor="w", stretch="NO")
        t_tree_money.column("name", width=100, minwidth=100, anchor="w", stretch="YES")
        t_tree_money.column("money", width=100, minwidth=100, anchor="w", stretch="YES")

        t_tree_money.heading("#0", text="ID", anchor="w")
        t_tree_money.heading("name", text="Jméno a příjmení", anchor="w")
        t_tree_money.heading("money", text="Zisk", anchor="w")

        t_tree_money.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        label4 = tk.Label(footer_lector, text=var.version, font=controller.title_text_font)
        label4.pack(side="left", padx=10)
        label2 = tk.Label(footer_lector, text=var.company, font=controller.title_text_font)
        label2.pack(side="right", padx=10)
        return

    def show_lectors(self, lector_name: str = ""):
        """
            Update lector list in t_tree
        """
        t_tree.delete(*t_tree.get_children())
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM teacher WHERE teacher_name LIKE '%" + lector_name + "%' ORDER BY teacher_name")
        # WHERE lesson.lesson_date LIKE '%2020-08%'

        rows = c.fetchall()
        for row in rows:
            t_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def show_lectors_money(self, lector_name: str = ""):
        """
            Update lector list in t_tree_money
        """
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        t_tree_money.delete(*t_tree_money.get_children())

        month = month_option_money.get()
        month_number = ""
        if not month == "vše":
            month_number = str(var.month.index(month) + 1)
            if len(month_number) == 1:
                month_number = "0" + month_number

        c.execute("SELECT teacher.teacher_id, teacher.teacher_name, SUM(lesson.lesson_teacher_price) FROM teacher INNER JOIN lesson ON "
                  "lesson.lesson_teacher=teacher.teacher_name WHERE teacher.teacher_name LIKE '%" + lector_name + "%'AND lesson.lesson_date LIKE '%" + str(
            year_option_money.get()) +
                  "-" + month_number + "%' GROUP BY teacher.teacher_name ORDER BY teacher.teacher_name")

        rows_money = c.fetchall()
        for row_money in rows_money:
            t_tree_money.insert("", tk.END, text=row_money[0], values=(row_money[1], row_money[2]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def open_add_lector(self):
        """
            Open new window to add new lector
        """
        global add_lector
        add_lector = tk.Toplevel()
        # add_lector.geometry("600x250")
        add_lector.resizable(False, False)
        add_lector.title("Lektor")
        add_lector.iconbitmap(var.icon)

        header_lector_add = tk.Frame(add_lector, bg=var.dark)
        header_lector_add.pack(fill="x", expand=False)
        content_lector_add = tk.Frame(add_lector)
        content_lector_add.pack(fill=tk.BOTH, expand=True)

        my_label = tk.Label(header_lector_add, text="Vyplňte údaje nového lektora.", font=("DejaVu Sans", 10, "bold"), bg=var.dark, fg=var.white)
        my_label.grid(row=0, column=0, padx=10, pady=10, sticky="W")
        my_label2 = tk.Label(header_lector_add, text="(* povinná pole)", font=("DejaVu Sans", 8), bg=var.dark, fg=var.white)
        my_label2.grid(row=0, column=1, padx=10, pady=10, sticky="E")

        global t_name
        t_name = tk.Text(content_lector_add, width=50, height=1)
        t_name.grid(row=2, column=1, padx=20)
        t_name.bind("<Tab>", self.jump_to_next_window)
        t_name_label = tk.Label(content_lector_add, text="Jméno a příjmení  ⃰⃰ ")
        t_name_label.grid(padx=10, row=2, column=0, sticky="W", pady=3)

        global t_mail
        t_mail = tk.Text(content_lector_add, width=50, height=1)
        t_mail.grid(row=3, column=1, padx=20)
        t_mail.bind("<Tab>", self.jump_to_next_window)
        t_mail_label = tk.Label(content_lector_add, text="Mail  ⃰⃰⃰ ")
        t_mail_label.grid(padx=10, row=3, column=0, sticky="W")

        global t_phone
        t_phone = tk.Text(content_lector_add, width=50, height=1)
        t_phone.grid(row=4, column=1, padx=20)
        t_phone.bind("<Tab>", self.jump_to_next_window)
        t_phone_label = tk.Label(content_lector_add, text="Telefonní číslo  ⃰⃰⃰ ")
        t_phone_label.grid(padx=10, row=4, column=0, sticky="W", pady=3)

        global t_birthday
        t_birthday = tk.Text(content_lector_add, width=50, height=1)
        t_birthday.grid(row=5, column=1, padx=20)
        t_birthday.bind("<Tab>", self.jump_to_next_window)
        t_birthday_label = tk.Label(content_lector_add, text="Datum narození")
        t_birthday_label.grid(padx=10, row=5, column=0, sticky="W")

        global t_info
        t_info = tk.Text(content_lector_add, width=50, height=5, wrap=tk.WORD)
        t_info.grid(row=6, column=1, padx=20)
        t_info.bind("<Tab>", self.jump_to_next_window)
        t_info_label = tk.Label(content_lector_add, text="Dodatečné informace")
        t_info_label.grid(padx=10, row=6, column=0, sticky="W", pady=3)

        submit_btn = ttk.Button(content_lector_add, text="Přidat lektora do databáze", command=self.submit_lector)
        submit_btn.grid(row=7, column=0, columnspan=2, pady=10, padx=10, ipadx=100)
        submit_btn.bind("<Return>", self.submit_lector_enter)

    def submit_lector_enter(self, event):
        self.submit_lector()

    def submit_lector(self):
        """
            Add new lector to DB
        """
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        # ("1.0",'end-1c') - from line one, character 0 to the end-\n
        tName = t_name.get("1.0", 'end-1c')
        tMail = t_mail.get("1.0", 'end-1c')
        tPhone = t_phone.get("1.0", 'end-1c')
        tBirth = t_birthday.get("1.0", 'end-1c')
        tInfo = t_info.get("1.0", 'end-1c')

        if (tName or tMail or tPhone) == "":
            messagebox.showerror("Chyba", "Nebylo vyplněno jedno z povinných polí. Povinná pole jsou označena hvězdičkou.")
            add_lector.lift()
            return

        elif len(tMail) > 0 and "@" not in tMail:
            messagebox.showerror("Chyba", "Zkontrolujte mailovou adresu lektora. Adresa musí obsahovat znak @.")
            add_lector.lift()
            return

        elif not re.match("[0123456789 +]", tPhone) and len(tPhone) > 0:
            messagebox.showerror("Chyba", "Zkontrolujte telefonni číslo lektora.")
            add_lector.lift()
            return

        if tName in var.teacher_list:
            messagebox.showerror("Chyba", "Jméno lektora již jednou v databázi je, přidejte za jméno např. město bydliště...")
            add_lector.lift()
            return

        c.execute(
            "INSERT INTO teacher(teacher_id, teacher_name, teacher_mail, teacher_phone, teacher_birthday, teacher_info) VALUES (NULL, ?, ?, ?, ?, ?)",
            (tName, tMail, tPhone, tBirth, tInfo))

        # pridani daliho lektora nebo vypnuti
        response = messagebox.askyesno("Lektor", "Chcete přidat dalšího lektora?")
        if response == 1:
            # Clear boxes
            t_name.delete(1.0, tk.END)
            t_mail.delete(1.0, tk.END)
            t_phone.delete(1.0, tk.END)
            t_birthday.delete(1.0, tk.END)
            t_info.delete(1.0, tk.END)
            # move window to forground
            add_lector.lift()
        else:
            add_lector.destroy()

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        utils.Utils.load_teachers(self.parent)
        self.show_lectors()
        self.show_lectors_money()

    def delete_lector(self, lector_id):
        """
            Remove lector from DB by lector ID
        """
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        response = messagebox.askyesno("Lektor", "Chcete opravdu odstranit lektora z databáze?")
        if response == 1:
            # delete record
            c.execute("DELETE from teacher WHERE oid=" + lector_id)
            print("Lektor byl odstraněn z databáze.")

            self.change_lector_tree.destroy()

            utils.Utils.load_teachers(self.parent)
            self.show_lectors()
            self.show_lectors_money()
        else:
            self.change_lector_tree.lift()
            print("Lektor nebyl odstraněn z databáze.")

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        self.show_lectors()
        self.show_lectors_money()

    def lector_detail_tree(self, event):
        global rowid
        global item
        rowid = t_tree.identify_row(event.y)
        item = t_tree.item(t_tree.focus())
        if not isinstance(item["text"], int) or var.clicked_tab == 1:
            print("Not a correct line")
        else:
            self.change_lector_tree = tk.Toplevel()
            # nenastavuj pevne rozmer
            self.change_lector_tree.minsize(800, 500)
            self.change_lector_tree.iconbitmap(var.icon)
            self.change_lector_tree.title("Lektor")

            top_tree = tk.Frame(self.change_lector_tree)
            top_tree.pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.W, expand=True)
            left_tree = tk.Frame(top_tree, bg=var.light)
            left_tree.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.W, expand=False)
            right_tree = tk.Frame(top_tree, bg=var.light)
            right_tree.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.W, expand=True)
            right_tree_top = tk.Frame(right_tree, bg=var.dark)
            right_tree_top.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)
            right_tree_lesson = tk.Frame(right_tree, bg=var.light)
            right_tree_lesson.pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.W, expand=True)
            bottom_tree = tk.Frame(self.change_lector_tree, bg=var.dark)
            bottom_tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)

            global t_tree_lesson_payment
            treeScroll = ttk.Scrollbar(right_tree_lesson)
            treeScroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
            t_tree_lesson_payment = ttk.Treeview(right_tree_lesson, columns=("student", "type", "duration", "cost", "date", "info"),
                                                 yscrollcommand=treeScroll.set)
            treeScroll.config(command=t_tree.yview)

            t_tree_lesson_payment.column("#0", width=35, minwidth=15, anchor="w", stretch="YES")
            t_tree_lesson_payment.column("student", width=150, minwidth=30, anchor="w", stretch="YES")
            t_tree_lesson_payment.column("type", width=100, minwidth=30, anchor="w", stretch="YES")
            t_tree_lesson_payment.column("duration", width=150, minwidth=30, anchor="w", stretch="YES")
            t_tree_lesson_payment.column("cost", width=100, minwidth=25, anchor="w", stretch="YES")
            t_tree_lesson_payment.column("date", width=100, minwidth=25, anchor="w", stretch="YES")
            t_tree_lesson_payment.column("info", width=200, minwidth=25, anchor="w", stretch="YES")

            t_tree_lesson_payment.heading("#0", text="ID", anchor="w")
            t_tree_lesson_payment.heading("student", text="Student", anchor="w")
            t_tree_lesson_payment.heading("type", text="Typ lekce", anchor="w")
            t_tree_lesson_payment.heading("duration", text="Doba trvání", anchor="w")
            t_tree_lesson_payment.heading("cost", text="Zisk z lekce", anchor="w")
            t_tree_lesson_payment.heading("date", text="Datum", anchor="w")
            t_tree_lesson_payment.heading("info", text="Dodatečné informace", anchor="w")

            t_tree_lesson_payment.pack(side=tk.TOP, pady=5, fill=tk.BOTH, expand=tk.YES)

            global year_option
            year_option = ttk.Combobox(right_tree_top, value=var.year, state="readonly", width=5)
            year_option.current(var.year.index(var.year_date))
            year_option.pack(side="right", pady=10, padx=5)
            year_option.bind("<<ComboboxSelected>>", self.combobox_year_month_selected)

            global month_option
            month_option = ttk.Combobox(right_tree_top, value=var.month, state="readonly", width=10)
            month_option.current(var.month_index)
            month_option.pack(side="right", pady=10, padx=1)
            month_option.bind("<<ComboboxSelected>>", self.combobox_year_month_selected)

            global check_lector_var
            check_lector_var = tk.BooleanVar()
            check = tk.Checkbutton(right_tree_top, text="Seskupovat data", variable=check_lector_var, fg=var.white, bg=var.dark,
                                   command=self.checkbutton_lector_tree)
            check.pack(side="right", pady=10, padx=10)
            check.config(selectcolor=var.dark, activebackground=var.dark, activeforeground=var.white)
            check.deselect()

            global status
            status = tk.Label(right_tree_top, font=("DejaVu Sans", 12, "bold"), fg=var.white, bg=var.dark)
            status.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, pady=3, padx=10)
            self.get_lector_total(item["values"][0])

            global teacher_detail_data

            teacher_detail_data_text = "Mail: " + item["values"][1] + "\n\nTelefon: " + str(item["values"][2]) + "\n\nNarozeniny: " + str(item["values"][3]) + "\n\n\n" + item["values"][4]

            teacher_detail_data = tk.Text(left_tree, width=33, wrap="word", font=("DejaVu Sans", 10, "bold"), bd=0, bg=var.light, fg=var.white)
            teacher_detail_data.tag_configure('small_ID', font=("DejaVu Sans", 8, "bold"))
            teacher_detail_data.tag_configure('big_name', font=("DejaVu Sans", 20, "bold"))
            teacher_detail_data.insert(tk.END, "ID: " + str(item["text"]), "small_ID")
            teacher_detail_data.insert(tk.END, "\n\n" + item["values"][0] + "\n\n", "big_name")
            teacher_detail_data.insert(tk.END, teacher_detail_data_text)
            teacher_detail_data.configure(state="disabled")
            teacher_detail_data.configure(inactiveselectbackground=teacher_detail_data.cget("selectbackground"))
            teacher_detail_data.pack(anchor=tk.W, pady=10, padx=10)

            # self.change_lector_tree.geometry("800x500")
            button1 = ttk.Button(bottom_tree, text="Editovat lektora", command=lambda: self.edit_lector(str(item["text"])))
            button1.pack(side="left", pady=10, padx=10, ipadx=5)
            button5 = ttk.Button(bottom_tree, text="Hodinová sazba", command=lambda: self.show_rate_frame_button(item["values"][0]))
            button5.pack(side="left", pady=10, padx=10, ipadx=5)
            button2 = ttk.Button(bottom_tree, text="Odstranit lektora", command=lambda: self.delete_lector(str(item["text"])))
            button2.pack(side="left", pady=10, padx=10, ipadx=5)
            button3 = ttk.Button(bottom_tree, text="Vytvořit PDF",
                                command=lambda: self.print_lector_PDF(str(item["text"]), month_option.get(), year_option.get()))
            button3.pack(side="left", pady=10, padx=10, ipadx=5)
            button4 = ttk.Button(bottom_tree, text="Poslat mailem",
                                command=lambda: self.send_mail(str(item["text"]), item["values"][0], item["values"][1], month_option.get(), year_option.get()))
            button4.pack(side="left", pady=10, padx=10, ipadx=5)

            self.show_lector_lesson(item["values"][0])

    def update_lector_save(self, lector_id):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        c.execute("""UPDATE teacher SET
            teacher_name = :name,
            teacher_mail = :mail,
            teacher_phone = :phone,
            teacher_birthday = :birthday,
            teacher_info = :info

            WHERE oid = :oid""",
                  {
                      "name": t_name_edit.get("1.0", 'end-1c'),
                      "mail": t_mail_edit.get("1.0", 'end-1c'),
                      "phone": t_phone_edit.get("1.0", 'end-1c'),
                      "birthday": t_birthday_edit.get("1.0", 'end-1c'),
                      "info": t_info_edit.get("1.0", 'end-1c'),
                      "oid": lector_id
                  }
                  )

        teacher_detail_data_text_new = "Mail: " + t_mail_edit.get("1.0", 'end-1c') + "\n\nTelefon: " + t_phone_edit.get("1.0", 'end-1c') + "\n\nNarozeniny: " + t_birthday_edit.get("1.0",
                                                                                                            'end-1c') + "\n\n" + t_info_edit.get("1.0", 'end-1c')

        teacher_detail_data.configure(state="normal")
        teacher_detail_data.delete("1.0", tk.END)
        teacher_detail_data.insert(tk.END, "ID: " + lector_id, "small_ID")
        teacher_detail_data.insert(tk.END, "\n\n" + t_name_edit.get("1.0", 'end-1c') + "\n\n", "big_name")
        teacher_detail_data.insert(tk.END, teacher_detail_data_text_new)
        teacher_detail_data.configure(state="disabled")

        rows = c.fetchall()
        for row in rows:
            t_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        # delete opened window
        self.change_lector.destroy()

        self.show_lectors()
        self.show_lectors_money()

    def edit_lector(self, lector_ID):
        global change_lector
        self.change_lector = tk.Toplevel()
        # self.change_lector.geometry("600x250")
        self.change_lector.resizable(False, False)
        self.change_lector.title("Lektor")
        self.change_lector.iconbitmap(var.icon)

        header_change_lector = tk.Frame(self.change_lector, bg=var.dark)
        header_change_lector.pack(fill="x", expand=False)
        content_change_lector = tk.Frame(self.change_lector)
        content_change_lector.pack(fill=tk.BOTH, expand=True)

        my_label = tk.Label(header_change_lector, text="Změňte potřebné údaje o lektorovi.", font=("DejaVu Sans", 10, "bold"), bg=var.dark, fg=var.white)
        my_label.grid(columnspan=2, pady=10, padx=10, sticky="W")

        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM teacher WHERE oid = " + lector_ID)
        records = c.fetchall()

        global t_name_edit
        t_name_edit = tk.Text(content_change_lector, width=50, height=1)
        t_name_edit.grid(row=1, column=1, padx=20, sticky="w")
        t_name_edit.bind("<Tab>", self.jump_to_next_window)
        t_name_label_edit = tk.Label(content_change_lector, text="Jméno a příjmení")
        t_name_label_edit.grid(padx=10, row=1, column=0, sticky="w", pady=3)

        global t_mail_edit
        t_mail_edit = tk.Text(content_change_lector, width=50, height=1)
        t_mail_edit.grid(row=2, column=1, padx=20, sticky="w")
        t_mail_edit.bind("<Tab>", self.jump_to_next_window)
        t_mail_label_edit = tk.Label(content_change_lector, text="Mail")
        t_mail_label_edit.grid(padx=10, row=2, column=0, sticky="w")

        global t_phone_edit
        t_phone_edit = tk.Text(content_change_lector, width=50, height=1)
        t_phone_edit.grid(row=3, column=1, padx=20, sticky="w")
        t_phone_edit.bind("<Tab>", self.jump_to_next_window)
        t_phone_label_edit = tk.Label(content_change_lector, text="Telefonní číslo")
        t_phone_label_edit.grid(padx=10, row=3, column=0, sticky="w", pady=3)

        global t_birthday_edit
        t_birthday_edit = tk.Text(content_change_lector, width=50, height=1)
        t_birthday_edit.grid(row=4, column=1, padx=20, sticky="w")
        t_birthday_edit.bind("<Tab>", self.jump_to_next_window)
        t_birthday_label_edit = tk.Label(content_change_lector, text="Datum narození")
        t_birthday_label_edit.grid(padx=10, row=4, column=0, sticky="w")

        global t_info_edit
        t_info_edit = tk.Text(content_change_lector, width=50, height=5, wrap=tk.WORD)
        t_info_edit.grid(row=5, column=1, padx=20, sticky="w")
        t_info_edit.bind("<Tab>", self.jump_to_next_window)
        t_info_label_edit = tk.Label(content_change_lector, text="Dodatečné informace")
        t_info_label_edit.grid(padx=10, row=5, column=0, sticky="w", pady=3)

        for record in records:
            t_name_edit.insert(tk.END, record[1])
            t_mail_edit.insert(tk.END, record[2])
            t_phone_edit.insert(tk.END, record[3])
            t_birthday_edit.insert(tk.END, record[4])
            t_info_edit.insert(tk.END, record[5])

        global save_btn
        save_btn = ttk.Button(content_change_lector, command=lambda: self.update_lector_save(lector_ID), text="Uložit změny", width=50)
        save_btn.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def filter_lectors(self, lector):
        if not lector == "Jméno lektora":
            self.show_lectors_money(lector_name=lector)
            self.show_lectors(lector_name=lector)

    def filter_lectors_entry(self, event):
        search = entry.get("1.0", 'end-1c')
        self.filter_lectors(search)
        return 'break'

    def show_lector_lesson(self, lector_name):
        t_tree_lesson_payment.delete(*t_tree_lesson_payment.get_children())

        month = month_option.get()
        month_number = ""
        if not month == "vše":
            month_number = str(var.month.index(month) + 1)
            if len(month_number) == 1:
                month_number = "0" + month_number

        lesson_lector_sql = "SELECT * from lesson WHERE lesson_date LIKE '%" + str(
            year_option.get()) + "-" + month_number + "%' AND lesson_teacher='" + lector_name + "' ORDER BY lesson_date"

        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        if not check_lector_var.get():
            c.execute(lesson_lector_sql)

            rows = c.fetchall()
            for row in rows:
                # ID lekce, jmeno studenta [1], typ lekce [4], doba trvani[5], datum[3]
                t_tree_lesson_payment.insert("", tk.END, text=row[0], values=(row[1], row[4], row[5], row[7], row[3], row[8]))

            t_tree_lesson_payment.heading("type", text="Typ lekce", anchor="w")
            t_tree_lesson_payment.heading("duration", text="Doba trvání", anchor="w")
            t_tree_lesson_payment.heading("cost", text="Zisk z lekce", anchor="w")
            t_tree_lesson_payment.heading("date", text="Datum", anchor="w")
            t_tree_lesson_payment.heading("info", text="Dodatečné informace", anchor="w")

        else:
            c.execute(
                "SELECT student.student_name, SUM(lesson.lesson_teacher_price), COUNT(lesson.lesson_duration), SUM(lesson.lesson_duration)  FROM student AS student INNER JOIN "
                "lesson AS lesson WHERE lesson.lesson_student=student.student_name AND lesson_date LIKE '%" + str(
                    year_option.get()) + "-" + month_number + "%' AND lesson.lesson_teacher LIKE '%" + lector_name + "%' GROUP BY student.student_name ORDER BY "
                                                                                                                     "student.student_name")
            rows = c.fetchall()
            for row in rows:
                t_tree_lesson_payment.insert("", tk.END, text="", values=(row[0], row[1], row[2], int(row[3]), ""))

            t_tree_lesson_payment.heading("type", text="Celkový zisk", anchor="w")
            t_tree_lesson_payment.heading("duration", text="Celkový počet hodin", anchor="w")
            t_tree_lesson_payment.heading("cost", text="Celkový čas lekcí", anchor="w")
            t_tree_lesson_payment.heading("date", text="--", anchor="w")
            t_tree_lesson_payment.heading("info", text="--", anchor="w")

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def get_lector_total(self, name):
        global total_lector_money

        # global total_student_money
        total_lector_money = self.sum_lector_lesson(name)

        if total_lector_money == None:
            total_lector_money = 0

        status.configure(text="Aktuální stav:  {price} Kč".format(price=total_lector_money))

    def combobox_year_month_selected(self, *args):
        self.show_lector_lesson(item["values"][0])
        self.get_lector_total(item["values"][0])

    def notebook_on_click(self, event):
        var.clicked_tab = content_lector_notebook.tk.call(content_lector_notebook._w, "identify", "tab", event.x, event.y)
        if var.clicked_tab == 1:
            month_option_money.config(state='readonly')
            year_option_money.config(state='readonly')
        elif var.clicked_tab == 0:
            month_option_money.config(state='disabled')
            year_option_money.config(state='disabled')

    def combobox_year_month_selected_money(self, *args):
        t_tree_money.delete(*t_tree_money.get_children())

        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        month = month_option_money.get()
        month_number = ""
        if not month == "vše":
            month_number = str(var.month.index(month) + 1)
            if len(month_number) == 1:
                month_number = "0" + month_number

        sql = "SELECT teacher.teacher_id, teacher.teacher_name, SUM(lesson.lesson_teacher_price) FROM teacher INNER JOIN lesson ON " \
              "lesson.lesson_teacher=teacher.teacher_name WHERE lesson.lesson_date LIKE '%" + str(
            year_option_money.get()) + "-" + month_number + "%' GROUP BY teacher.teacher_name ORDER BY teacher.teacher_name"

        c.execute(sql)
        rows = c.fetchall()

        for row in rows:
            t_tree_money.insert("", tk.END, text=row[0], values=(row[1], row[2]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def sum_lector_lesson(self, lector_name):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        month = month_option.get()
        month_number = ""
        if not month == "vše":
            month_number = str(var.month.index(month) + 1)
            if len(month_number) == 1:
                month_number = "0" + month_number

        total_payment = "SELECT SUM(lesson_teacher_price) FROM lesson WHERE lesson_teacher='" + lector_name + "' AND lesson_date LIKE '%" + str(
            year_option.get()) + "-" + month_number + "%'"
        c.execute(total_payment)
        sum = c.fetchone()[0]

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()
        return sum

    def jump_to_next_window(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def default_text_entry(self, event):
        current = entry.get("1.0", tk.END)
        if current == "Jméno lektora\n":
            entry.delete("1.0", tk.END)
        elif current == "\n":
            entry.insert("1.0", "Jméno lektora")

    def show_rate_frame_button(self, lector):
        self.show_rate_frame()

        lector_idx = var.teacher_list.index(lector)

        lector_combo.current(lector_idx)
        lector_combo.config(state='disabled')

        self.combobox_teacher_selected()

    def show_rate_frame(self):
        self.change_rate = tk.Toplevel()
        self.change_rate.resizable(False, False)
        self.change_rate.title("Hodinová sazba")
        self.change_rate.iconbitmap(var.icon)

        global content_rate
        header_rate = tk.Frame(self.change_rate, bg=var.dark)
        content_rate = tk.Frame(self.change_rate)
        footer_rate = tk.Frame(self.change_rate)

        header_rate.grid(row=0, column=0, sticky="NEWS")
        content_rate.grid(row=1, column=0, sticky="NEWS")
        footer_rate.grid(row=2, column=0, sticky="NEWS")

        lab1 = tk.Label(header_rate, text="Jméno lektora:", bg=var.dark, fg=var.white, font=("DejaVu Sans", 12, "bold"))
        lab1.grid(row=0, column=0, pady=10, padx=10, sticky="NEWS")

        global lector_combo
        lector_combo = ttk.Combobox(header_rate, value=var.teacher_list, state="readonly")
        lector_combo.grid(row=0, column=1, pady=10, padx=10, sticky="NEWS")
        lector_combo.bind("<<ComboboxSelected>>", self.combobox_teacher_selected)

        l1 = tk.Label(header_rate, text="            Doba\t      Částka student (Kč)     Částka lektor (Kč)", bg=var.dark, fg=var.white,
                      font=("DejaVu Sans", 10))
        l1.grid(row=2, column=0, pady=2, columnspan=3)

        content_rate.columnconfigure(0, weight=0)
        content_rate.columnconfigure(1, weight=3)
        content_rate.columnconfigure(2, weight=3)

        # ID, kdo, doba, kolik student, kolik lektor
        rate_entries = []

        global rate_entry
        # row loop
        for y in range(13):
            for x in range(3):
                if x == 0:
                    rate_entry = tk.Entry(content_rate)
                    rate_entry.grid(row=y, column=x, pady=2, padx=3)
                    rate_entries.append(lector_combo)
                    duration = var.lesson_type_options[y]
                    rate_entry.insert(0, duration)
                    rate_entry.configure(state='readonly')
                else:
                    rate_entry = tk.Entry(content_rate)
                    rate_entry.grid(row=y, column=x, pady=2, padx=3)
                rate_entries.append(rate_entry)

        # self.change_rate.destroy()

        footer_rate.columnconfigure(0, weight=1)
        footer_rate.columnconfigure(1, weight=1)

        entry_button = ttk.Button(footer_rate, text="Uložit", command=lambda: [self.add_rate(rate_entries)], width=20)
        entry_button.grid(row=0, column=0, pady=10, padx=10, sticky="NEWS")

        entry_close_button = ttk.Button(footer_rate, text="Uložit a zavřít", command=lambda: [self.add_rate(rate_entries), self.change_rate.destroy()], width=20)
        entry_close_button.grid(row=0, column=1, pady=10, padx=10, sticky="NEWS")

    def add_rate(self, rate_entries):
        rate_list = list()
        final_rate_list = []
        i = 0

        for entry in rate_entries:
            if i % 4 == 3:
                rate_list.append(entry.get())
                if not len(rate_list[2]) == 0:
                    final_rate_list.append(tuple(rate_list))
                else:
                    rate_list[2] = '0'
                    rate_list[3] = '0'
                    final_rate_list.append(tuple(rate_list))
                rate_list.clear()
                i += 1
            else:
                rate_list.append(entry.get())
                i += 1

        self.add_rate_to_database(final_rate_list)

    def combobox_teacher_selected(self, *args):
        choosen_lector = lector_combo.get()
        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()
        count_sql = "SELECT COUNT(rate_time) FROM rate WHERE rate_teacher_name LIKE '%" + choosen_lector + "%'"
        c.execute(count_sql)
        count = c.fetchone()[0]
        i = 0

        if count != 0:
            sql = "SELECT rate_time, rate_student_money, rate_teacher_money FROM rate WHERE rate_teacher_name LIKE '%" + choosen_lector + "%'"
            c.execute(sql)

            rows = c.fetchall()
            for row in rows:
                element_duration = content_rate.grid_slaves(row=i, column=0)
                element_duration[0].delete(0, tk.END)
                element_duration[0].insert(tk.END, str(row[0]))

                element_student_money = content_rate.grid_slaves(row=i, column=1)
                element_student_money[0].delete(0, tk.END)
                element_student_money[0].insert(tk.END, str(row[1]))

                element_teacher_money = content_rate.grid_slaves(row=i, column=2)
                element_teacher_money[0].delete(0, tk.END)
                element_teacher_money[0].insert(tk.END, str(row[2]))
                i += 1
        else:
            for i in range(13):
                element_student_money = content_rate.grid_slaves(row=i, column=1)
                element_student_money[0].delete(0, tk.END)
                element_student_money[0].insert(tk.END, "")

                element_teacher_money = content_rate.grid_slaves(row=i, column=2)
                element_teacher_money[0].delete(0, tk.END)
                element_teacher_money[0].insert(tk.END, "")

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def add_rate_to_database(self, final_rate_list):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()
        choosen_lector = lector_combo.get()

        count_sql = "SELECT COUNT(rate_time) FROM rate WHERE rate_teacher_name LIKE '%" + choosen_lector + "%'"
        c.execute(count_sql)
        count = c.fetchone()[0]
        if count != 0:
            sql = "DELETE FROM rate WHERE rate_teacher_name LIKE '%" + choosen_lector + "%'"
            c.execute(sql)
        else:
            print("Database was empty before")

        sql = "INSERT INTO rate (rate_id, rate_teacher_name, rate_time, rate_student_money, rate_teacher_money) VALUES (NULL, ?, ?, ?, ?)"
        c.executemany(sql, final_rate_list)

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def checkbutton_lector_tree(self):
        self.show_lector_lesson(item["values"][0])

    #####################################################
    def addPageNumber(self, canvas, doc):
        """
        Add the page number
        """
        pdfmetrics.registerFont(
            TTFont('georgia', 'Georgia.ttf')
        )

        canvas.line(26, 30, 570, 30)

        page_num = canvas.getPageNumber()
        text = var.company_name + "                                             " + var.company_web + "                              TEL: " + var.company_phone + "                                             " \
                                                                                                                               "Strana č. %s" % page_num
        canvas.setFont("georgia", 10)

        # canvas.drawRightString(280*mm, 20*mm, text) 112
        canvas.drawRightString(200 * mm, 5 * mm, text)

    def print_lector_PDF(self, record_ID, month_name, year_number, show_info=True):
        # Connect to database or create database
        month_number = ""
        if not month_name == "vše":
            month_number = str(var.month.index(month_name) + 1)
            if len(month_number) == 1:
                month_number = "0" + month_number
        global mail, phone, name
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM teacher WHERE oid = " + record_ID)
        records = c.fetchall()

        date = datetime.datetime.now()

        for record in records:
            name = record[1]
            mail = record[2]
            phone = record[3]
        month = month_name.lower()
        year = year_number
        fileName = "{j}_{m}_{y}.pdf".format(j=name, m=month, y=year)

        logo = r"C:\Users\42073\Desktop\DP\logo_pdf.png"
        elements = []

        pdfmetrics.registerFont(
            TTFont('georgia', 'Georgia.ttf')
        )

        titlestyle = ParagraphStyle(
            name='Title',
            fontName='georgia',
            fontSize=20,
            leading=10,
            textColor="#fefffe"
        )

        headstyle = ParagraphStyle(
            name='Header',
            fontName='georgia',
            fontSize=14,
            leading=10,
            leftIndent=120,
        )

        headstyle_money = ParagraphStyle(
            name='Header',
            fontName='georgia',
            fontSize=14,
            leading=10,
        )

        headstyle_money_right = ParagraphStyle(
            name='Header',
            fontName='georgia',
            fontSize=14,
            leading=10,
            alignment=TA_RIGHT,
        )

        normal = ParagraphStyle(
            name='left',
            fontName='georgia',
            fontSize=10,
        )

        normal_white = ParagraphStyle(
            name='left',
            fontName='georgia',
            fontSize=10,
            textColor="#fefffe",
        )

        normal_money_right = ParagraphStyle(
            name='left',
            fontName='georgia',
            fontSize=10,
            alignment=TA_RIGHT,
        )

        right = ParagraphStyle(
            name='right',
            fontName='georgia',
            fontSize=10,
            leftIndent=120,
        )

        im = Image(logo, width=150, height=50.7, hAlign='RIGHT')
        elements.append(im)

        dataBasicInfo = [[Paragraph(name, style=normal), Paragraph(var.company_name, style=headstyle)],
                         [Paragraph(mail, style=normal), Paragraph(var.company_address, style=right)],
                         [Paragraph(phone, style=normal), Paragraph(var.company_city, style=right)]]

        BasicInfoTable = Table(dataBasicInfo, repeatRows=1)
        BasicInfoTable.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'georgia'),
            ('BACKGROUND', (0, 0), (0, 3), "#dfc8cb"),
        ]))
        elements.append(BasicInfoTable)
        elements.append(Spacer(20, 20))

        dataMonth = [[Paragraph(date.strftime("Datum a čas vytvoření dokumentu: %d.%m.%Y, %H:%M:%S"), style=normal)]]
        dataMonthTable = Table(dataMonth, repeatRows=1)
        dataMonthTable.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'georgia'),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ]))
        elements.append(dataMonthTable)
        elements.append(Spacer(5, 5))

        if month == "vše":
            dataTitle = [[Paragraph("Výpis hodin za rok {y}".format(y=year), style=titlestyle)]]
        else:
            dataTitle = [[Paragraph("Výpis hodin za měsíc {m} {y}".format(m=month, y=year), style=titlestyle)]]
        dataTitleTable = Table(dataTitle, repeatRows=1, rowHeights=35)
        dataTitleTable.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 1), (0, -1), "#fefffe"),
            ('FONTNAME', (0, 0), (-1, -1), 'georgia'),
            ('BACKGROUND', (0, 0), (3, 0), "#802430"),
        ]))
        elements.append(dataTitleTable)
        elements.append(Spacer(20, 20))

        partInfo = [[Paragraph("Přehled hodin", style=normal_white)]]
        partInfoTable = Table(partInfo, repeatRows=1)
        partInfoTable.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 1), (0, -1), "#fefffe"),
            ('FONTNAME', (0, 0), (-1, -1), 'georgia'),
            ('BACKGROUND', (0, 0), (3, 0), "#802430"),
        ]))
        elements.append(partInfoTable)
        elements.append(Spacer(5, 5))

        if check_lector_var.get():
            line3 = [Paragraph("Student", style=normal), Paragraph("Celkový čas (minuty) + CALLs", style=normal), Paragraph("Zisk z lekcí",
                                                                                                                            style=normal)]
            data = [line3]

            c.execute("SELECT student.student_name, SUM(lesson.lesson_teacher_price), SUM(lesson.lesson_duration) FROM student AS student INNER JOIN lesson "
                      "AS lesson WHERE lesson.lesson_student=student.student_name AND lesson_date LIKE '%" + str(
                year_option.get()) + "-" + month_number + "%' AND lesson.lesson_teacher LIKE '%" + name + "%' GROUP BY student.student_name ORDER BY "
                                                                                                          "student.student_name")
            lessons_records = c.fetchall()
            for row in lessons_records:
                lessons_duration = "%0.2f" % (row[2] / 60)
                temp = [row[0], lessons_duration, row[1]]
                data.append(temp)
        else:
            line3 = [Paragraph("Datum", style=normal), Paragraph("Délka lekce (minuty)", style=normal), Paragraph("Zisk z lekce", style=normal),
                     Paragraph("Student", style=normal)]
            data = [line3]

            sql_lessons = "SELECT * FROM lesson WHERE lesson_teacher='" + name + "' AND lesson_date LIKE '%" + year_number + "-" + str(
                month_number) + "%' ORDER BY lesson_date"
            c.execute(sql_lessons)
            lessons_records = c.fetchall()

            for row in lessons_records:
                temp = [row[3], row[4], row[6], row[1]]
                data.append(temp)

        lessontable = Table(data, repeatRows=1, hAlign="LEFT")
        lessontable.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), "#dfc8cb"),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'georgia'),
            ('LINEBELOW', (0, -1), (0, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(lessontable)
        elements.append(Spacer(20, 20))

        endInfo = [[Paragraph("Závěrečné shrnutí", style=normal_white)]]
        endInfoTable = Table(endInfo, repeatRows=1)
        endInfoTable.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 1), (0, -1), "#fefffe"),
            ('FONTNAME', (0, 0), (-1, -1), 'georgia'),
            ('BACKGROUND', (0, 0), (3, 0), "#802430"),
        ]))
        elements.append(endInfoTable)
        elements.append(Spacer(5, 5))

        sql_sum = "SELECT SUM(lesson_teacher_price), SUM(lesson_duration) FROM lesson WHERE lesson_teacher='" + name + "' AND lesson_date LIKE '%" + year_number + "-" + str(
            month_number) + "%' " \
                            "ORDER BY lesson_date"
        c.execute(sql_sum)
        summary = c.fetchone()
        lesson_minutes = summary[1]
        lesson_hours = 0
        if not lesson_minutes == ("" or 0):
            lesson_hours = lesson_minutes / 60
            # lesson_hours = "%0.2f" % (lesson_minutes / 60)

        finalData = [[Paragraph("Celkový počet odpracovaných hodin (minut):", style=normal_money_right),
                      Paragraph(str(lesson_hours) + " hodin (" + str(lesson_minutes) + " minut) + CALLs",
                                style=normal)], [Paragraph("Částka k výplatě:", style=headstyle_money_right), Paragraph(str(summary[0]) + " Kč",
                                                                                                                        style=headstyle_money)]]

        BottomTable = Table(finalData, repeatRows=1, rowHeights=(15, 25))
        BottomTable.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'georgia'),
            ('BACKGROUND', (0, 0), (-1, -1), "#dfc8cb"),
        ]))

        elements.append(BottomTable)

        try:
            # pocet odpracovanych hodin, plat
            doc = SimpleDocTemplate(fileName, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20, allowSplitting=1,
                                    title="Měsíční vyúčtování", author="LENKA© corporation",
                                    showBoundary=0)
            doc.build(elements, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)
        except Exception as e:
            messagebox.showerror("Lektor",
                                 "PDF soubor se nepodařilo vygenerovat. Zkuste to prosím znovu.\n\nRADA: Pravděpodobně máte PDF soubor otevřený a nepodařilo se ho přepsat. "
                                 "\n\nERROR: {e}".format(e=e))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        if show_info:
            messagebox.showinfo("Lektor", "PDF soubor lektora {l} byl vygenerován.".format(l=name))

        self.change_lector_tree.lift()

    ############################################ record_ID, month_name, year_number, show_info=True
    def send_mail(self, record_ID, name, contact, month_name, year_number):
        import mail as mail
        pdf_path = name + "_" + month_name + "_" + year_number + ".pdf"
        print(pdf_path)
        try:
            self.print_lector_PDF(record_ID, month_name, year_number, show_info=False)
            if not os.path.exists(pdf_path):
                messagebox.showerror("Lektor",
                                     "PDF soubor se nepodařilo vygenerovat. Mail nemá cenu posílat bez PDF souboru s přehledem. Zkuste to prosím znovu.\n\nRADA: Pravděpodobně máte PDF "
                                     "soubor otevřený a nepodařilo se ho přepsat.")
            mail.Mail.send_lector_mail(self.parent, name, contact, month_name, year_number)
            # mail.Mail.send_student_mail(self.parent, name, contact, mail_year_option)
        except Exception as e:
            messagebox.showerror("Lektor",
                                 "PDF soubor nebo mail se nepodařilo vygenerovat. Zkuste to prosím znovu.\n\nRADA: Pravděpodobně máte PDF soubor otevřený a nepodařilo se ho přepsat nebo "
                                 "je problém s programem Outlook.\n\nERROR: {e}".format(e=e))
            self.change_lector_tree.lift()
