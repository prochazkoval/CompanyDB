from builtins import print
import os
import re

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
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, TableStyle, Image, Spacer, Paragraph, Frame
from reportlab.platypus.tables import Table
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics




class StudentPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        utils.Utils.get_school_year(self.parent)

        global content_student_notebook
        header_student = tk.Frame(self, bg=var.dark)
        content_student_notebook = ttk.Notebook(self)
        footer_student = tk.Frame(self)

        header_student.pack(fill="x", expand=False)
        content_student_notebook.pack(fill=tk.BOTH, expand=True)
        content_student_notebook.bind('<Button-1>', self.notebook_on_click)
        footer_student.pack(fill="x", expand=False)

        content_student = tk.Frame(content_student_notebook)
        content_student.pack(fill=tk.BOTH, expand=True)

        money_student = tk.Frame(content_student_notebook)
        money_student.pack(fill=tk.BOTH, expand=True)

        content_student_notebook.add(content_student, text=" Přehled studentů ")
        content_student_notebook.add(money_student, text=" Přehled aktuálního stavu studentů ")

        label1 = tk.Label(master=header_student, text="Studenti\t", font=controller.title_header_font, bg=var.dark, fg=var.white)
        label1.pack(side="left", fill="x", pady=10, padx=10)

        b3 = ttk.Button(header_student, text="Filtrovat", command=lambda: self.filter_students_entry(entry.get("1.0", 'end-1c')))
        b3.pack(side="right", pady=10, padx=10)

        global entry
        entry = tk.Text(header_student, width=20, height=1)
        entry.insert(tk.END, "Jméno studenta")
        entry.bind("<FocusIn>", self.default_text_entry)
        entry.bind("<FocusOut>", self.default_text_entry)
        entry.bind("<Return>", self.filter_students_entry)
        entry.pack(side="right", pady=10, padx=10)

        global school_year_option_money
        school_year_option_money = ttk.Combobox(header_student, value=var.school_year, state="disabled", width=10)
        current_school_year_money = utils.Utils.get_school_year(self.parent)
        current_school_year_index_money = var.school_year.index(current_school_year_money)
        school_year_option_money.current(current_school_year_index_money)
        school_year_option_money.pack(side="right", pady=10, padx=1)
        school_year_option_money.bind("<<ComboboxSelected>>", self.show_students_money)

        label3 = tk.Label(master=header_student, text="\t", bg=var.dark)
        label3.pack(side="right", fill="x")

        b1 = ttk.Button(header_student, text="Přidat studenta", command=lambda: self.open_add_student())
        b1.pack(side="left", pady=10, padx=10)

        global s_tree
        s_scrollbar_y = tk.Scrollbar(content_student)
        s_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        s_scrollbar_x = tk.Scrollbar(content_student, orient=tk.HORIZONTAL)
        s_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        s_tree = ttk.Treeview(content_student, columns=("name", "mail", "phone", "level", "curse", "adult", "parent_mail", "parent_phone", "info"),
                              yscrollcommand=s_scrollbar_y.set,
                              xscrollcommand=s_scrollbar_x.set)
        s_scrollbar_y.config(command=s_tree.yview)
        s_scrollbar_x.config(command=s_tree.xview)
        s_tree.bind("<Double-1>", self.student_detail_tree)
        s_tree.column("#0", width=45, minwidth=15, anchor="w", stretch="NO")
        s_tree.column("name", width=200, minwidth=35, anchor="w", stretch="NO")
        s_tree.column("mail", width=200, minwidth=35, anchor="w", stretch="NO")
        s_tree.column("phone", width=130, minwidth=35, anchor="w", stretch="NO")
        s_tree.column("level", width=70, minwidth=45, anchor="w", stretch="YES")
        s_tree.column("curse", width=70, minwidth=45, anchor="w", stretch="YES")
        s_tree.column("adult", width=60, minwidth=35, anchor="w", stretch="NO")
        s_tree.column("parent_mail", width=200, minwidth=25, anchor="w", stretch="YES")
        s_tree.column("parent_phone", width=100, minwidth=25, anchor="w", stretch="YES")
        s_tree.column("info", width=200, minwidth=25, anchor="w", stretch="YES")

        s_tree.heading("#0", text="ID", anchor="w")
        s_tree.heading("name", text="Jméno a příjmení", anchor="w")
        s_tree.heading("mail", text="Mail", anchor="w")
        s_tree.heading("phone", text="Telefonní číslo", anchor="w")
        s_tree.heading("level", text="Úroveň znalostí", anchor="w")
        s_tree.heading("curse", text="Kurz", anchor="w")
        s_tree.heading("adult", text="Věková kategorie", anchor="w")
        s_tree.heading("parent_mail", text="Mail na rodiče", anchor="w")
        s_tree.heading("parent_phone", text="Telefonní číslo na rodiče", anchor="w")
        s_tree.heading("info", text="Dodatečné informace", anchor="w")

        global s_tree_money
        s_scrollbar_money = ttk.Scrollbar(money_student)
        s_scrollbar_money.pack(side=tk.RIGHT, fill=tk.Y)
        s_scrollbar_x_money = tk.Scrollbar(money_student, orient=tk.HORIZONTAL)
        s_scrollbar_x_money.pack(side=tk.BOTTOM, fill=tk.X)
        s_tree_money = ttk.Treeview(money_student, columns=("lesson", "payment", "money"), yscrollcommand=s_scrollbar_money.set,
                                    xscrollcommand=s_scrollbar_x_money.set)
        s_scrollbar_x_money.config(command=s_tree_money.xview)
        s_scrollbar_money.config(command=s_tree_money.yview)

        s_tree_money.column("#0", width=100, minwidth=100, anchor="w", stretch="YES")
        s_tree_money.column("lesson", width=100, minwidth=100, anchor="w", stretch="YES")
        s_tree_money.column("payment", width=100, minwidth=100, anchor="w", stretch="YES")
        s_tree_money.column("money", width=100, minwidth=100, anchor="w", stretch="YES")

        s_tree_money.heading("#0", text="Jméno a příjmení", anchor="w")
        s_tree_money.heading("lesson", text="Cena lekcí", anchor="w")
        s_tree_money.heading("payment", text="Platby", anchor="w")
        s_tree_money.heading("money", text="Stav konta", anchor="w")

        s_tree_money.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        s_tree.pack(fill=tk.BOTH, expand=True)

        label4 = tk.Label(footer_student, text=var.version, font=controller.title_text_font)
        label4.pack(side="left", padx=10)
        label2 = tk.Label(footer_student, text=var.company, font=controller.title_text_font)
        label2.pack(side="right", padx=10)

        return

    def open_add_student(self):
        global add_student
        global var_student_age
        global var_student_level

        add_student = tk.Toplevel()
        add_student.resizable(False, False)
        add_student.title("Student")
        add_student.iconbitmap(var.icon)

        header_add_student = tk.Frame(add_student, bg=var.dark)
        header_add_student.grid(row=0, column=0, sticky="NEWS")
        content_add_student = tk.Frame(add_student)
        content_add_student.grid(row=1, column=0, sticky="NEWS")

        my_label = tk.Label(header_add_student, text="Vyplňte údaje nového studenta", font=("DejaVu Sans", 10, "bold"), bg=var.dark, fg=var.white)
        my_label.grid(row=0, column=0, padx=10, pady=10, sticky="W")
        my_label2 = tk.Label(header_add_student, text="(* povinná pole)", font=("DejaVu Sans", 8), bg=var.dark, fg=var.white)
        my_label2.grid(row=0, column=1, padx=10, pady=10, sticky="E")

        global s_name
        s_name = tk.Text(content_add_student, height=1)
        s_name.grid(row=1, column=1, padx=20, columnspan=3)
        s_name.bind("<Tab>", self.jump_to_next_window)
        s_name_label = tk.Label(content_add_student, text="Jméno a příjmení  ⃰⃰ ")
        s_name_label.grid(row=1, column=0, sticky="W", padx=10, pady=2)

        global s_mail
        s_mail = tk.Text(content_add_student, height=1)
        s_mail.grid(row=2, column=1, columnspan=3)
        s_mail.bind("<Tab>", self.jump_to_next_window)
        s_mail_label = tk.Label(content_add_student, text="Mail")
        s_mail_label.grid(row=2, column=0, sticky="W", padx=10, pady=2)

        global s_phone
        s_phone = tk.Text(content_add_student, height=1)
        s_phone.grid(row=3, column=1, columnspan=3)
        s_phone.bind("<Tab>", self.jump_to_next_window)
        s_phone_label = tk.Label(content_add_student, text="Telefonní číslo")
        s_phone_label.grid(row=3, column=0, sticky="W", padx=10, pady=2)

        """s_course_day = ttk.Combobox(content_add_student, value=var.week_days, state="readonly", width=10)
        s_course_day.grid(row=4, column=1, padx = 10)
        s_course_day.bind("<Tab>", self.jump_to_next_window)

        s_course_hour = ttk.Combobox(content_add_student, value=var.hour, state="readonly", width=10)
        s_course_hour.grid(row=4, column=2)
        s_course_hour.bind("<Tab>", self.jump_to_next_window)"""

        global s_course
        s_course = tk.Text(content_add_student, height=1)
        s_course.grid(row=4, column=1, columnspan=3)
        s_course.bind("<Tab>", self.jump_to_next_window)
        s_course_label = tk.Label(content_add_student, text="Termín kurzu (den a čas)")
        s_course_label.grid(row=4, column=0, sticky="W", padx=10, pady=2)

        global s_level_option
        s_level_option = ttk.Combobox(content_add_student, value=var.knowledge_level_option, state="readonly", width=25)
        s_level_option.grid(row=5, column=1, columnspan=2, sticky="W", padx=20)
        s_level_option.bind("<Tab>", self.jump_to_next_window)
        s_level_option_label = tk.Label(content_add_student, text="Zvolte úroveň znalostí")
        s_level_option_label.grid(row=5, column=0, sticky="W", padx=10, pady=2)

        s_adult_label = tk.Label(content_add_student, text="Věková kategorie")
        s_adult_label.grid(row=6, column=0, sticky="W", padx=10, pady=2)

        global s_is_adult
        s_is_adult = ttk.Combobox(content_add_student, value=var.age_group_options, state="readonly", width=25)
        s_is_adult.bind("<Tab>", self.jump_to_next_window)
        s_is_adult.grid(row=6, column=1, columnspan=2, sticky="W", padx=20)

        global s_parent_mail
        s_parent_mail = tk.Text(content_add_student, height=1)
        s_parent_mail.grid(row=7, column=1, columnspan=3)
        s_parent_mail.bind("<Tab>", self.jump_to_next_window)
        s_parent_mail_label = tk.Label(content_add_student, text="Mail na rodiče")
        s_parent_mail_label.grid(row=7, column=0, sticky="W", pady=2, padx=10)

        global s_parent_phone
        s_parent_phone = tk.Text(content_add_student, height=1)
        s_parent_phone.grid(row=8, column=1, columnspan=3)
        s_parent_phone.bind("<Tab>", self.jump_to_next_window)
        s_parent_phone_label = tk.Label(content_add_student, text="Telefonní číslo na rodiče")
        s_parent_phone_label.grid(row=8, column=0, sticky="W", padx=10, pady=2)

        global s_info
        s_info = tk.Text(content_add_student, height=5, wrap=tk.WORD)
        s_info.grid(row=9, column=1, columnspan=3)
        s_info.bind("<Tab>", self.jump_to_next_window)
        s_info_label = tk.Label(content_add_student, text="Dodatečné informace")
        s_info_label.grid(row=9, column=0, sticky="W", pady=2, padx=10)

        submit_btn = ttk.Button(content_add_student, text="Přidat studenta do databáze", command=self.submit_student)
        submit_btn.grid(row=10, column=0, columnspan=4, pady=10, padx=10, ipadx=100)
        submit_btn.bind("<Return>", self.submit_student_enter)

    def submit_student_enter(self, event):
        self.submit_student()

    def submit_student(self):
        """
            Add new student to DB
        """
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        sName = s_name.get("1.0", 'end-1c')
        sMail = s_mail.get("1.0", 'end-1c')
        sPhone = s_phone.get("1.0", 'end-1c')
        sLevelOption = s_level_option.get()
        sCourse = s_course.get("1.0", 'end-1c')
        sIsAdult = s_is_adult.get()
        sParentMail = s_parent_mail.get("1.0", 'end-1c')
        sParentPhone = s_parent_phone.get("1.0", 'end-1c')
        sInfo = s_info.get("1.0", 'end-1c')

        if sName == "":
            messagebox.showerror("Chyba", "Jméno studenta musí být vyplněno, jedná se o povinné pole. Povinná pole jsou označena hvězdičkou.")
            add_student.lift()
            return

        elif len(sMail) > 0 and "@" not in sMail:
            messagebox.showerror("Chyba", "Zkontrolujte mailovou adresu studenta. Adresa musí obsahovat znak @.")
            add_student.lift()
            return

        elif len(sParentMail) > 0 and "@" not in sParentMail:
            messagebox.showerror("Chyba", "Zkontrolujte mailovou adresu na rodiče studenta. Adresa musí obsahovat znak @.")
            add_student.lift()
            return

        elif not re.match("[0123456789 +]", sPhone) and len(sPhone) > 0:
            messagebox.showerror("Chyba", "Zkontrolujte telefonni číslo studenta.")
            add_student.lift()
            return

        elif not re.match("[0123456789 +,]", sParentPhone) and len(sParentPhone) > 0:
            messagebox.showerror("Chyba", "Zkontrolujte telefonni číslo na rodiče studenta.")
            add_student.lift()
            return

        if sName in var.student_list:
            messagebox.showerror("Chyba", "Jméno studenta již jednou v databázi je, přidejte za jméno např. místo bydliště, věk...")
            add_student.lift()
            return

        # insert student info into table
        c.execute(
            "INSERT INTO student(student_id, student_name, student_mail, student_phone, student_level, student_course, "
            "student_is_adult, student_parent_mail, student_parent_phone, student_info) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (sName, sMail, sPhone, sLevelOption, sCourse, sIsAdult, sParentMail, sParentPhone, sInfo))

        # pridani daliho lektora nebo vypnuti
        response = messagebox.askyesno("Student", "Chcete přidat dalšího studenta?")
        if response == 1:
            # Clear boxes
            s_name.delete(1.0, tk.END)
            s_mail.delete(1.0, tk.END)
            s_phone.delete(1.0, tk.END)
            s_course.delete(1.0, tk.END)
            s_level_option.set('')
            s_is_adult.set('')
            s_parent_mail.delete(1.0, tk.END)
            s_parent_phone.delete(1.0, tk.END)
            s_info.delete(1.0, tk.END)
            # move window to forground
            add_student.lift()
        else:
            add_student.destroy()
        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        utils.Utils.load_students(self.parent)
        self.show_students()
        self.show_students_money()

    def show_students(self, student_name: str = ""):
        """
            Update student list in s_tree
        """
        print("show_students")
        s_tree.delete(*s_tree.get_children())
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM student WHERE student_name LIKE '%" + student_name + "%' ORDER BY student_name")
        rows = c.fetchall()
        for row in rows:
            # s_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], money, row[6], row[7], row[8], dospelak, row[10], row[11], row[12]))
            s_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def delete_student(self, student_id):
        """
            Remove student from DB by student ID
        """
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        response = messagebox.askyesno("Student", "Chcete opravdu odstranit studenta z databáze?")
        if response == 1:
            # delete record
            c.execute("DELETE from student WHERE oid=" + student_id)
            print("Student byl odstraněn z databáze.")
            utils.Utils.load_students(self.parent)
        else:
            print("Student nebyl odstraněn z databáze.")

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        self.change_student_tree.destroy()
        utils.Utils.load_students(self.parent)

        self.show_students()
        self.show_students_money()

    def student_detail_tree(self, event):
        global rowid
        global item
        rowid = s_tree.identify_row(event.y)
        item = s_tree.item(s_tree.focus())
        if not isinstance(item["text"], int):
            print("Not a correct line")
        else:
            self.change_student_tree = tk.Toplevel()
            self.change_student_tree.minsize(950, 570)
            self.change_student_tree.title("Student")
            self.change_student_tree.iconbitmap(var.icon)

            top_tree = tk.Frame(self.change_student_tree)
            top_tree.pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.W, expand=True)
            ####
            left_tree = tk.Frame(top_tree, width=250, bg=var.light)
            left_tree.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.W, expand=False)
            #####
            right_tree = tk.Frame(top_tree)
            right_tree.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.W, expand=True)
            right_tree_top = tk.Frame(right_tree, bg=var.dark)
            right_tree_top.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)
            right_tree_lesson = tk.Frame(right_tree, bg=var.light)
            right_tree_lesson.pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.W, expand=True)
            right_tree_payment = tk.Frame(right_tree, bg=var.light)
            right_tree_payment.pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.W, expand=True)
            ####
            bottom_tree = tk.Frame(self.change_student_tree, bg=var.dark)
            bottom_tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)

            global school_year_option
            school_year_option = ttk.Combobox(right_tree_top, value=var.school_year, state="readonly", width=10)
            current_school_year = utils.Utils.get_school_year(self.parent)
            current_school_year_index = var.school_year.index(current_school_year)
            school_year_option.current(current_school_year_index)
            school_year_option.pack(side="right", pady=10, padx=10)
            school_year_option.bind("<<ComboboxSelected>>", self.combobox_school_year_selected)

            global status
            status = tk.Label(right_tree_top, font=("DejaVu Sans", 12, "bold"))
            status.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, pady=3, padx=10)
            self.get_student_total(item["values"][0])

            global s_tree_lesson
            treeScroll = ttk.Scrollbar(right_tree_lesson)
            treeScroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
            s_tree_lesson = ttk.Treeview(right_tree_lesson, columns=("date", "duration", "cost", "lector", "info"), yscrollcommand=treeScroll.set)
            treeScroll.config(command=s_tree.yview)

            s_tree_lesson.bind("<Double-1>")
            s_tree_lesson.column("#0", width=50, minwidth=15, anchor="w", stretch="NO")
            s_tree_lesson.column("date", width=90, minwidth=25, anchor="w", stretch="NO")
            s_tree_lesson.column("duration", width=90, minwidth=25, anchor="w", stretch="NO")
            s_tree_lesson.column("cost", width=90, minwidth=25, anchor="w", stretch="NO")
            s_tree_lesson.column("lector", width=100, minwidth=25, anchor="w", stretch="YES")
            s_tree_lesson.column("info", width=200, minwidth=25, anchor="w", stretch="YES")

            s_tree_lesson.heading("#0", text="ID", anchor="w")
            s_tree_lesson.heading("date", text="Datum", anchor="w")
            s_tree_lesson.heading("duration", text="Doba trvání", anchor="w")
            s_tree_lesson.heading("cost", text="Cena lekce", anchor="w")
            s_tree_lesson.heading("lector", text="Lektor", anchor="w")
            s_tree_lesson.heading("info", text="Dodatečné informace", anchor="w")

            s_tree_lesson.pack(side=tk.TOP, pady=5, fill=tk.BOTH, expand=tk.YES)

            global s_tree_payment
            treeScroll = ttk.Scrollbar(right_tree_payment)
            treeScroll.pack(side=tk.RIGHT, pady=5, fill=tk.Y)
            s_tree_payment = ttk.Treeview(right_tree_payment, columns=("money", "date", "type", "info"), yscrollcommand=treeScroll.set)
            treeScroll.config(command=s_tree.yview)

            s_tree_payment.bind("<Double-1>")
            s_tree_payment.column("#0", width=50, minwidth=15, anchor="w", stretch="NO")
            s_tree_payment.column("money", width=90, minwidth=25, anchor="w", stretch="NO")
            s_tree_payment.column("date", width=90, minwidth=25, anchor="w", stretch="NO")
            s_tree_payment.column("type", width=120, minwidth=25, anchor="w", stretch="YES")
            s_tree_payment.column("info", width=200, minwidth=25, anchor="w", stretch="YES")

            s_tree_payment.heading("#0", text="ID", anchor="w")
            s_tree_payment.heading("money", text="Částka (Kč)", anchor="w")
            s_tree_payment.heading("date", text="Datum", anchor="w")
            s_tree_payment.heading("type", text="Způsob platby", anchor="w")
            s_tree_payment.heading("info", text="Dodatečné informace", anchor="w")

            s_tree_payment.pack(side=tk.TOP, pady=5, fill=tk.BOTH, expand=tk.YES)

            self.show_student_payment(item["values"][0])
            self.show_student_lesson(item["values"][0])

            global student_detail_data

            student_detail_data_text = "Mail: " + item["values"][1] + "\n\nTelefon: " + str(item["values"][2]) + "\n\nÚroveň znalostí: " + str(item[
                                                                                                                                                   "values"][3]) + "\n\nTermín kurzu: " + str(
                item["values"][4]) + "\n\nVěková kategorie: " + str(item["values"][5]) + "\n\nMail na rodiče: " + \
                                       str(item["values"][6]) + "\n\nTelefon na rodiče: " + str(item["values"][7]) + "\n\n\n" + str(item["values"][8])

            student_detail_data = tk.Text(left_tree, width=33, wrap="word", font=("DejaVu Sans", 10, "bold"), bd=0, bg=var.light, fg=var.white)
            student_detail_data.tag_configure('small_ID', font=("DejaVu Sans", 8, "bold"))
            student_detail_data.tag_configure('big_name', font=("DejaVu Sans", 20, "bold"))
            student_detail_data.insert(tk.END, "ID: " + str(item["text"]), "small_ID")
            student_detail_data.insert(tk.END, "\n\n" + item["values"][0] + "\n\n", "big_name")
            student_detail_data.insert(tk.END, student_detail_data_text)
            student_detail_data.configure(state="disabled")
            student_detail_data.configure(inactiveselectbackground=student_detail_data.cget("selectbackground"))
            student_detail_data.pack(anchor=tk.W, pady=10, padx=10)

            button1 = ttk.Button(bottom_tree, text="Editovat studenta", command=lambda: self.edit_student(str(item["text"])))
            button1.pack(side="left", pady=10, padx=10, ipadx=5)
            button2 = ttk.Button(bottom_tree, text="Odstranit studenta", command=lambda: self.delete_student(str(item["text"])))
            button2.pack(side="left", pady=10, padx=10, ipadx=5)
            button3 = ttk.Button(bottom_tree, text="Vytvořit PDF",
                                 command=lambda: self.print_student_PDF(str(item["text"]), total_student_money, total_student_lesson, school_year_option.get()))
            button3.pack(side="left", pady=10, padx=10, ipadx=5)
            button4 = ttk.Button(bottom_tree, text="Poslat mailem",
                                 command=lambda: self.send_mail(str(item["text"]), item["values"][0], item["values"][1], school_year_option.get(),
                                                                total_student_money, total_student_lesson))
            button4.pack(side="left", pady=10, padx=10, ipadx=5)

    def update_student_save(self, student_id):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        c.execute("""UPDATE student SET
            student_name = :name,
            student_mail = :mail,
            student_phone = :phone,        	
            student_level = :level,	
        	student_course = :course,
        	student_is_adult = :adult,
        	student_parent_mail = :parent_mail,
        	student_parent_phone = :parent_phone,
            student_info = :info

            WHERE oid = :oid""",
                  {
                      "name": s_name_edit.get("1.0", 'end-1c'),
                      "mail": s_mail_edit.get("1.0", 'end-1c'),
                      "phone": s_phone_edit.get("1.0", 'end-1c'),
                      "course": s_course_edit.get("1.0", 'end-1c'),
                      "level": s_level_option_edit.get(),
                      "adult": s_is_adult_edit.get(),
                      "parent_mail": s_adult_mail_edit.get("1.0", 'end-1c'),
                      "parent_phone": s_adult_phone_edit.get("1.0", 'end-1c'),
                      "info": s_info_edit.get("1.0", 'end-1c'),
                      "oid": student_id
                  }
                  )

        student_detail_data_text_new = "Mail: " + s_mail_edit.get("1.0", 'end-1c') + "\n\nTelefon: " + s_phone_edit.get("1.0", 'end-1c') + "\n\nÚroveň znalostí: " + s_level_option_edit.get() + \
                                       "\n\nTermín kurzu: " + s_course_edit.get("1.0", 'end-1c') + "\n\nVěková kategorie: " + s_is_adult_edit.get() + "\n\nMail na rodiče: " + s_adult_mail_edit.get(
            "1.0", 'end-1c') + "\n\nTelefon na rodiče: " + s_adult_phone_edit.get("1.0", 'end-1c') + "\n\n" + s_info_edit.get("1.0", 'end-1c')

        student_detail_data.configure(state="normal")
        student_detail_data.delete("1.0", tk.END)
        student_detail_data.insert(tk.END, "ID: " + student_id, "small_ID")
        student_detail_data.insert(tk.END, "\n\n" + s_name_edit.get("1.0", 'end-1c') + "\n\n", "big_name")
        student_detail_data.insert(tk.END, student_detail_data_text_new)
        student_detail_data.configure(state="disabled")

        rows = c.fetchall()
        for row in rows:
            s_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        # delete opened window
        self.change_student.destroy()

        self.show_students()
        self.show_students_money()

    def show_student_payment(self, student_name):
        s_tree_payment.delete(*s_tree_payment.get_children())

        school_year = school_year_option.get()

        payment_student_sql = "SELECT * FROM payment WHERE payment_student='" + student_name + "' AND payment_date >= '" + school_year[
                                                                                                                           0:4] + "-09-01' AND payment_date <= '" + school_year[
                                                                                                                                                                    5:9] + \
                              "-08-31' " \
                              "ORDER BY payment_date"
        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        c.execute(payment_student_sql)

        rows = c.fetchall()
        for row in rows:
            s_tree_payment.insert("", tk.END, text=row[0], values=(row[2], row[3], row[4], row[5]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def show_student_lesson(self, student_name):
        s_tree_lesson.delete(*s_tree_lesson.get_children())

        school_year = school_year_option.get()
        lesson_student_sql = "SELECT * FROM lesson WHERE lesson_student='" + student_name + "' AND lesson_date >= '" + school_year[
                                                                                                                       0:4] + "-09-01' AND lesson_date <= '" + school_year[
                                                                                                                                                               5:9] + "-08-31'"

        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        c.execute(lesson_student_sql)

        rows = c.fetchall()
        for row in rows:
            s_tree_lesson.insert("", tk.END, text=row[0], values=(row[3], row[4], row[5], row[2]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def sum_student_lesson_payment(self, student_name):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        school_year = school_year_option.get()

        sql_sum_student_lesson_payment = "SELECT " \
                                         "student_name, " \
                                         "(SELECT SUM(lesson_student_price) FROM lesson " \
                                         "WHERE lesson_student = '" + student_name + "' " \
                                                                                     "AND lesson_date >= '" + school_year[0:4] + "-09-01' " \
                                                                                                                                 "AND lesson_date <= '" + school_year[5:9] + "-08-31') AS lekce, " \
                                                                                                                                                                             "(SELECT SUM(payment_value) FROM payment " \
                                                                                                                                                                             "WHERE payment_student = '" + student_name + "'" \
                                                                                                                                                                                                                          "AND payment_date >= '" + school_year[
                                                                                                                                                                                                                                                    0:4] + "-09-01' " \
                                                                                                                                                                                                                                                           "AND payment_date <= '" + school_year[
                                                                                                                                                                                                                                                                                     5:9] + "-08-31') AS plateby " \
                                                                                                                                                                                                                                                                                            "FROM student WHERE student_name = '" + student_name + "'"

        c.execute(sql_sum_student_lesson_payment)
        student_lesson_payment_values = c.fetchone()

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()
        return student_lesson_payment_values

    def edit_student(self, student_ID):
        global change_student
        self.change_student = tk.Toplevel()
        self.change_student.resizable(False, False)
        self.change_student.title("Student")
        self.change_student.iconbitmap(var.icon)

        header_change_student = tk.Frame(self.change_student, bg=var.dark)
        header_change_student.pack(fill="x", expand=False)
        content_change_student = tk.Frame(self.change_student)
        content_change_student.pack(fill=tk.BOTH, expand=True)

        my_label = tk.Label(header_change_student, text="Změňte potřebné údaje o studentovi.", bg=var.dark, fg=var.white, font=("DejaVu Sans", 10, "bold"))
        my_label.grid(columnspan=2, pady=10, padx=10, sticky="W")

        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM student WHERE oid = " + student_ID)
        records = c.fetchall()

        global s_name_edit
        s_name_edit = tk.Text(content_change_student, width=50, height=1)
        s_name_edit.grid(row=1, column=1, padx=20, sticky="w", pady=3)
        s_name_edit.bind("<Tab>", self.jump_to_next_window)
        s_name_label_edit = tk.Label(content_change_student, text="Jméno a příjmení")
        s_name_label_edit.grid(padx=10, row=1, column=0, sticky="w")

        global s_mail_edit
        s_mail_edit = tk.Text(content_change_student, width=50, height=1)
        s_mail_edit.grid(row=2, column=1, padx=20, sticky="w")
        s_mail_edit.bind("<Tab>", self.jump_to_next_window)
        s_mail_label_edit = tk.Label(content_change_student, text="Mail")
        s_mail_label_edit.grid(padx=10, row=2, column=0, sticky="w")

        global s_phone_edit
        s_phone_edit = tk.Text(content_change_student, width=50, height=1)
        s_phone_edit.grid(row=3, column=1, padx=20, sticky="w", pady=3)
        s_phone_edit.bind("<Tab>", self.jump_to_next_window)
        s_phone_label_edit = tk.Label(content_change_student, text="Telefonní číslo")
        s_phone_label_edit.grid(padx=10, row=3, column=0, sticky="w")

        global s_course_edit
        s_course_edit = tk.Text(content_change_student, width=50, height=1)
        s_course_edit.grid(row=4, column=1, padx=20, sticky="W")
        s_course_edit.bind("<Tab>", self.jump_to_next_window)
        s_course_label_edit = tk.Label(content_change_student, text="Termín kurzu (den a čas)")
        s_course_label_edit.grid(padx=10, row=4, column=0, sticky="W")

        global s_level_option_edit
        s_level_option_edit = ttk.Combobox(content_change_student, value=var.knowledge_level_option, state="readonly", width=25)
        s_level_option_edit.grid(row=5, column=1, sticky="W", padx=20)
        s_level_option_label_edit = tk.Label(content_change_student, text="Zvolte úroveň znalostí")
        s_level_option_label_edit.grid(padx=10, row=5, column=0, sticky="W", pady=3)

        global s_is_adult_edit
        s_is_adult_edit = ttk.Combobox(content_change_student, value=var.age_group_options, state="readonly", width=25)
        s_is_adult_edit.bind("<Tab>", self.jump_to_next_window)
        s_is_adult_edit.grid(row=6, column=1, sticky="W", padx=20)
        s_adult_mail_edit_label = tk.Label(content_change_student, text="Věková kategorie")
        s_adult_mail_edit_label.grid(padx=10, row=6, column=0, sticky="W")

        global s_adult_mail_edit
        s_adult_mail_edit = tk.Text(content_change_student, width=50, height=1)
        s_adult_mail_edit.grid(row=7, column=1, padx=20, sticky="W", pady=3)
        s_adult_mail_edit.bind("<Tab>", self.jump_to_next_window)
        s_adult_mail_edit_label = tk.Label(content_change_student, text="Mail na rodiče")
        s_adult_mail_edit_label.grid(padx=10, row=7, column=0, sticky="W")

        global s_adult_phone_edit
        s_adult_phone_edit = tk.Text(content_change_student, width=50, height=1)
        s_adult_phone_edit.grid(row=8, column=1, padx=20, sticky="W")
        s_adult_phone_edit.bind("<Tab>", self.jump_to_next_window)
        s_adult_phone_label_edit = tk.Label(content_change_student, text="Telefonní číslo na rodiče")
        s_adult_phone_label_edit.grid(padx=10, row=8, column=0, sticky="W")

        global s_info_edit
        s_info_edit = tk.Text(content_change_student, width=50, height=5, wrap=tk.WORD)
        s_info_edit.grid(row=9, column=1, padx=20, sticky="w", pady=3)
        s_info_edit.bind("<Tab>", self.jump_to_next_window)
        s_info_label_edit = tk.Label(content_change_student, text="Dodatečné informace")
        s_info_label_edit.grid(padx=10, row=9, column=0, sticky="w")

        for record in records:
            s_name_edit.insert(tk.END, record[1])
            s_mail_edit.insert(tk.END, record[2])
            s_phone_edit.insert(tk.END, record[3])
            current_knowledge_option_index = var.knowledge_level_option.index(record[4])
            s_level_option_edit.current(current_knowledge_option_index)
            s_course_edit.insert(tk.END, record[5])
            current_adult_option_index = var.age_group_options.index(record[6])
            s_is_adult_edit.current(current_adult_option_index)
            s_adult_mail_edit.insert(tk.END, record[7])
            s_adult_phone_edit.insert(tk.END, record[8])
            s_info_edit.insert(tk.END, record[9])

        global save_btn
        save_btn = ttk.Button(content_change_student, command=lambda: self.update_student_save(student_ID), text="Uložit změny", width=50)
        save_btn.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def notebook_on_click(self, event):
        var.clicked_tab = content_student_notebook.tk.call(content_student_notebook._w, "identify", "tab", event.x, event.y)

        if var.clicked_tab == 1:
            school_year_option_money.config(state='readonly')
        elif var.clicked_tab == 0:
            school_year_option_money.config(state='disabled')

    def show_students_money(self, *args, student_name: str = ""):
        print("show_students_money")
        s_tree_money.delete(*s_tree_money.get_children())

        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        school_year = school_year_option_money.get()

        sql2 = "SELECT lesson_student, SUM(lesson_student_price), (SELECT SUM(payment_value) FROM payment WHERE payment_student LIKE '%" + student_name + "%' AND payment_date >= '" + school_year[
                                                                                                                                                                                       0:4] + "-09-01' AND payment_date <= '" + school_year[
                                                                                                                                                                                                                                5:9] + "-08-31' GROUP BY payment_student) FROM lesson WHERE lesson_student " \
                                                                                                                                                                                                                                       "LIKE '%" + student_name + "%' AND lesson_date >= '" + school_year[
                                                                                                                                                                                                                                                                                              0:4] + "-09-01' AND lesson_date <= '" + school_year[
                                                                                                                                                                                                                                                                                                                                      5:9] + "-08-31' GROUP BY lesson_student"

        c.execute(sql2)

        rows = c.fetchall()

        for row in rows:
            first = row[1]
            second = row[2]
            if first == None:
                first = '0'
            if second == None:
                second = '0'
            s_tree_money.insert("", tk.END, text=row[0], values=(first, second, str(int(second) - int(first))))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def jump_to_next_window(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def default_text_entry(self, event):
        current = entry.get("1.0", tk.END)
        if current == "Jméno studenta\n":
            entry.delete("1.0", tk.END)
        elif current == "\n":
            entry.insert("1.0", "Jméno studenta")

    def filter_student(self, student):
        if not student == "Jméno studenta":
            self.show_students(student_name=student)
            self.show_students_money(student_name=student)

    def filter_students_entry(self, event):
        search = entry.get("1.0", 'end-1c')
        self.filter_student(search)
        return 'break'

    def get_student_total(self, student_name):
        global total_student_account_balance
        global total_student_lesson
        global total_student_money

        total_student_account_balance = self.sum_student_lesson_payment(student_name)

        # name, lesson, payment
        if total_student_account_balance[2] is None:
            total_student_money = 0
        else:
            total_student_money = total_student_account_balance[2]

        if total_student_account_balance[1] is None:
            total_student_lesson = 0
        else:
            total_student_lesson = total_student_account_balance[1]

        total_status = total_student_money - total_student_lesson

        if total_status < 0:
            status.configure(
                text="Aktuální stav:  {price} Kč\tCena lekcí: {lesson} Kč | Součet plateb: {payment} Kč".format(price=total_status, lesson=total_student_lesson,
                                                                                                                payment=total_student_money), fg=var.orange,
                bg=var.dark)
        else:
            status.configure(
                text="Aktuální stav:  {price} Kč\tCena lekcí: {lesson} Kč | Součet plateb: {payment} Kč".format(price=total_status, lesson=total_student_lesson,
                                                                                                                payment=total_student_money), fg=var.white,
                bg=var.dark)

    def combobox_school_year_selected(self, *args):
        self.show_student_payment(item["values"][0])
        self.show_student_lesson(item["values"][0])
        self.get_student_total(item["values"][0])

    ###############################################################
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

    def print_student_PDF(self, record_ID, total_student_money, total_student_lesson, school_year, show_info=True):
        # Connect to database or create database
        global mail, phone, name
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM student WHERE oid = " + record_ID)
        records = c.fetchall()

        import datetime
        date = datetime.datetime.now()

        for record in records:
            name = record[1]
            mail = record[2]
            phone = record[3]
        fileName = "{n}_{y}.pdf".format(n=name, y=school_year)

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

        dataTitle = [[Paragraph("Přehled hodin a plateb za školní rok {y}".format(y=school_year), style=titlestyle)]]
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

        partInfo = [[Paragraph("Přehled lekcí", style=normal_white)]]
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

        line3 = [Paragraph("Datum", style=normal), Paragraph("Délka lekce (minuty)", style=normal), Paragraph("Cena lekce", style=normal),
                 Paragraph("Lektor", style=normal)]
        data = [line3]

        sql_lessons = "SELECT * FROM lesson WHERE lesson_student='" + name + "' AND lesson_date >='" + school_year[
                                                                                                       0:4] + "-09-01' AND lesson_date <='" + school_year[
                                                                                                                                              5:9] + "-08-31' ORDER BY " \
                                                                                                                                                     "lesson_date"
        c.execute(sql_lessons)
        lessons_records = c.fetchall()

        for row in lessons_records:
            temp = [row[3], row[4], row[5], row[2]]
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

            # ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(lessontable)
        elements.append(Spacer(20, 20))

        partPayment = [[Paragraph("Přehled plateb", style=normal_white)]]
        partPaymentTable = Table(partPayment, repeatRows=1)
        partPaymentTable.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 1), (0, -1), "#fefffe"),
            ('FONTNAME', (0, 0), (-1, -1), 'georgia'),
            ('BACKGROUND', (0, 0), (3, 0), "#802430"),
        ]))
        elements.append(partPaymentTable)
        elements.append(Spacer(5, 5))

        line4 = [Paragraph("Datum", style=normal), Paragraph("Částka", style=normal), Paragraph("Způsob platby", style=normal),
                 Paragraph("Dodatečné informace", style=normal)]
        dataPayment = [line4]

        sql_payment = "SELECT * FROM payment WHERE payment_student='" + name + "' AND payment_date >='" + school_year[
                                                                                                          0:4] + "-09-01' AND payment_date <='" + school_year[
                                                                                                                                                  5:9] + "-08-31' ORDER BY payment_date"
        c.execute(sql_payment)
        payment_records = c.fetchall()

        for row in payment_records:
            temp = [row[3], row[2], row[4], row[5]]
            dataPayment.append(temp)

        paymentTable = Table(dataPayment, repeatRows=1, hAlign="LEFT")
        paymentTable.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), "#dfc8cb"),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'georgia'),
            ('LINEBELOW', (0, -1), (0, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),

            # ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(paymentTable)
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

        finalData = [[Paragraph("Stav na účtu:", style=normal_money_right), Paragraph(str(total_student_money) + " Kč", style=normal)], [Paragraph("Celková "
                                                                                                                                                   "cena lekcí:", style=normal_money_right),
                                                                                                                                         Paragraph(str(total_student_lesson) + " Kč", style=normal)],
                     [Paragraph("Zůstatek:", style=headstyle_money_right),
                      Paragraph(str(total_student_money - total_student_lesson) + " Kč", style=headstyle_money)]]

        BottomTable = Table(finalData, repeatRows=1, rowHeights=(15, 15, 25))
        BottomTable.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'georgia'),
            ('BACKGROUND', (0, 0), (-1, -1), "#dfc8cb"),
        ]))

        elements.append(BottomTable)

        try:
            # výpis lekcí a plateb
            doc = SimpleDocTemplate(fileName, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20, allowSplitting=1,
                                    title="Měsíční vyúčtování", author=var.company,
                                    showBoundary=0)
            doc.build(elements, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)
        except Exception as e:
            messagebox.showerror("Student",
                                 "PDF soubor se nepodařilo vygenerovat. Zkuste to prosím znovu.\n\nRADA: Pravděpodobně máte PDF soubor otevřený a nepodařilo se ho přepsat. "
                                 "\n\nERROR: {e}".format(e=e))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        if show_info:
            messagebox.showinfo("Student", "PDF soubor studenta {s} byl vygenerován.".format(s=name))

        self.change_student_tree.lift()

    ###############################################################

    def send_mail(self, record_ID, name, contact, mail_year_option, total_student_money, total_student_lesson):
        import mail as mail
        pdf_path = name + "_" + mail_year_option + ".pdf"
        try:
            self.print_student_PDF(record_ID, total_student_money, total_student_lesson, mail_year_option, show_info=False)
            if not os.path.exists(pdf_path):
                messagebox.showerror("Student",
                                     "PDF soubor se nepodařilo vygenerovat. Mail nemá cenu posílat bez PDF souboru s přehledem. Zkuste to prosím znovu.\n\nRADA: Pravděpodobně máte PDF "
                                     "soubor otevřený a nepodařilo se ho přepsat.")
            mail.Mail.send_student_mail(self.parent, name, contact, mail_year_option)
        except Exception as e:
            messagebox.showerror("Student",
                                 "PDF soubor nebo mail se nepodařilo vygenerovat. Zkuste to prosím znovu.\n\nRADA: Pravděpodobně máte PDF soubor otevřený a nepodařilo se ho přepsat nebo "
                                 "je problém s programem Outlook.\n\nERROR: {e}".format(e=e))
            self.change_student_tree.lift()
