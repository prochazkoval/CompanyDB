try:
    # Python2
    import Tkinter as tk
    import ttk
except ImportError:
    # Python3
    import tkinter as tk
    import tkinter.ttk as ttk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
import variables as var
import utils as utils
from lector import LectorPage as lector
import re


class LessonPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        header_lesson = tk.Frame(self, bg=var.dark)
        content_lesson = tk.Frame(self)
        footer_lesson = tk.Frame(self)

        header_lesson.pack(fill="x", expand=False)
        content_lesson.pack(fill=tk.BOTH, expand=True)
        footer_lesson.pack(fill="x", expand=False)

        label1 = tk.Label(master=header_lesson, text="Lekce", font=controller.title_header_font, bg=var.dark, fg=var.white)
        label1.pack(side="left", fill="x", pady=10, padx=10)

        b3 = ttk.Button(header_lesson, text="Filtrovat", command=lambda: self.filter_lesson(t_entry.get("1.0", 'end-1c'), s_entry.get("1.0", 'end-1c')))
        b3.pack(side="right", pady=10, padx=10)

        global t_entry
        t_entry = tk.Text(header_lesson, width=16, height=1)
        t_entry.insert(tk.END, "Jméno lektora")
        t_entry.pack(side="right", pady=10, padx=10)
        t_entry.bind("<FocusIn>", self.default_text_entry_lector)
        t_entry.bind("<FocusOut>", self.default_text_entry_lector)
        t_entry.bind("<Return>", self.filter_student_teacher_entry)

        global s_entry
        s_entry = tk.Text(header_lesson, width=16, height=1)
        s_entry.insert(tk.END, "Jméno studenta")
        s_entry.pack(side="right", pady=10, padx=10)
        s_entry.bind("<FocusIn>", self.default_text_entry_student)
        s_entry.bind("<FocusOut>", self.default_text_entry_student)
        s_entry.bind("<Return>", self.filter_student_teacher_entry)

        global year_option
        year_option = ttk.Combobox(header_lesson, value=var.year, state="readonly", width=5)
        year_option.current(var.year.index(var.year_date))
        year_option.pack(side="right", pady=10, padx=1)
        year_option.bind("<<ComboboxSelected>>", self.combobox_year_month_selected)

        global month_option
        month_option = ttk.Combobox(header_lesson, value=var.month, state="readonly", width=10)
        month_option.current(var.month_index)
        month_option.pack(side="right", pady=10, padx=1)
        month_option.bind("<<ComboboxSelected>>", self.combobox_year_month_selected)

        b1 = ttk.Button(header_lesson, text="Přidat lekce", command=lambda: self.open_add_lesson())
        b1.pack(side="left", pady=10, padx=10)

        self.selected = []
        b3 = ttk.Button(header_lesson, text="Odstranit lekce", command=lambda: self.delete_lesson(self.selected))
        b3.pack(side="left", pady=10, padx=10)

        global l_tree
        l_scrollbar = ttk.Scrollbar(content_lesson)
        l_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        l_scrollbar_x = tk.Scrollbar(content_lesson, orient=tk.HORIZONTAL)
        l_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        # ID, kdo, koho, kdy, délka lekce, info
        l_tree = ttk.Treeview(content_lesson, columns=("student", "lector", "date", "type", "duration", "student_price", "lector_price", "info"),
                              yscrollcommand=l_scrollbar.set, xscrollcommand=l_scrollbar_x.set)
        l_scrollbar.config(command=l_tree.yview)
        l_scrollbar_x.config(command=l_tree.xview)

        l_tree.bind("<<TreeviewSelect>>", self.get_choosen_line)

        l_tree.column("#0", width=45, minwidth=15, anchor="w", stretch="NO")
        l_tree.column("student", width=150, minwidth=25, anchor="w", stretch="NO")
        l_tree.column("lector", width=150, minwidth=25, anchor="w", stretch="NO")
        l_tree.column("date", width=130, minwidth=25, anchor="w", stretch="NO")
        l_tree.column("type", width=150, minwidth=25, anchor="w", stretch="NO")
        l_tree.column("duration", width=100, minwidth=25, anchor="w", stretch="NO")
        l_tree.column("student_price", width=100, minwidth=25, anchor="w", stretch="NO")
        l_tree.column("lector_price", width=100, minwidth=25, anchor="w", stretch="NO")
        l_tree.column("info", width=200, minwidth=25, anchor="w", stretch="YES")

        l_tree.heading("#0", text="ID", anchor="w")
        l_tree.heading("student", text="Student", anchor="w")
        l_tree.heading("lector", text="Lektor", anchor="w")
        l_tree.heading("date", text="Datum (rok-měsíc-den)", anchor="w")
        l_tree.heading("type", text="Typ lekce", anchor="w")
        l_tree.heading("duration", text="Délka lekce", anchor="w")
        l_tree.heading("student_price", text="Cena (student)", anchor="w")
        l_tree.heading("lector_price", text="Zisk (lektor)", anchor="w")
        l_tree.heading("info", text="Dodatečné informace", anchor="w")

        l_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        # footer
        label4 = tk.Label(footer_lesson, text=var.version, font=controller.title_text_font)
        label4.pack(side="left", padx=10)
        label2 = tk.Label(footer_lesson, text=var.company, font=controller.title_text_font)
        label2.pack(side="right", padx=10)

        return

    def show_lesson(self):
        """
            Update payment list in p_tree
        """
        l_tree.delete(*l_tree.get_children())
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
        print(month_number)

        c.execute("SELECT * from lesson WHERE lesson_date LIKE '%" + str(year_option.get()) + "-" + month_number + "%' ORDER BY lesson_student DESC, lesson_date")
        rows = c.fetchall()
        for row in rows:
            l_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def open_add_lesson(self):
        """
            Open new window to add new lesson
        """

        global add_lessons
        add_lessons = tk.Toplevel()
        add_lessons.resizable(False, False)
        add_lessons.title("Přidat lekce")
        add_lessons.iconbitmap(var.icon)

        header_lesson_add = tk.Frame(add_lessons, bg=var.dark)
        header_lesson_add.grid(row=0, column=0, sticky="NEWS")
        global content_lesson_add
        content_lesson_add = tk.Frame(add_lessons)
        content_lesson_add.grid(row=1, column=0, sticky="NEWS")

        # ID, kdy, délka lekce, kdo, koho, info
        lesson_entries = []

        header_lesson_add.grid_columnconfigure(0, weight=1)
        header_lesson_add.grid_columnconfigure(1, weight=1)
        header_lesson_add.grid_columnconfigure(2, weight=1)
        header_lesson_add.grid_columnconfigure(3, weight=1)

        # lektor, student
        lab1 = tk.Label(header_lesson_add, text="Student:", bg=var.dark, fg=var.white, font=("DejaVu Sans", 10, "bold"))
        lab1.grid(row=0, column=0, pady=10)
        student_combo = ttk.Combobox(header_lesson_add, value=var.student_list, state="readonly")
        student_combo.grid(row=0, column=1, pady=10, padx=10)
        lab2 = tk.Label(header_lesson_add, text=" Lektor:", bg=var.dark, fg=var.white, font=("DejaVu Sans", 10, "bold"))
        lab2.grid(row=0, column=2, pady=10)
        global lector_combo
        lector_combo = ttk.Combobox(header_lesson_add, value=var.teacher_list, state="readonly")
        lector_combo.grid(row=0, column=3, pady=10, padx=10)
        lector_combo.bind("<<ComboboxSelected>>", self.combobox_teacher_selected)
        content_lesson_add.grid_columnconfigure(0, weight=2)
        content_lesson_add.grid_columnconfigure(1, weight=2)
        content_lesson_add.grid_columnconfigure(2, weight=2)
        content_lesson_add.grid_columnconfigure(3, weight=2)
        content_lesson_add.grid_columnconfigure(4, weight=1)
        content_lesson_add.grid_columnconfigure(5, weight=1)
        content_lesson_add.grid_columnconfigure(6, weight=3)

        # row loop
        for y in range(21):
            # column loop
            for x in range(6):
                if y == 0:
                    l1 = tk.Label(content_lesson_add, text="Datum (rok-měsíc-den)")
                    l1.grid(row=0, column=0, pady=2, padx=2)
                    l2 = tk.Label(content_lesson_add, text="Typ lekce")
                    l2.grid(row=0, column=1, pady=2, padx=2)
                    l3 = tk.Label(content_lesson_add, text="Délka lekce")
                    l3.grid(row=0, column=2, pady=2, padx=2)
                    l4 = tk.Label(content_lesson_add, text="Cena (student)")
                    l4.grid(row=0, column=3, pady=2, padx=2)
                    l5 = tk.Label(content_lesson_add, text="Zisk (Lektor)")
                    l5.grid(row=0, column=4, pady=2, padx=2)
                    l6 = tk.Label(content_lesson_add, text="Dodatečné informace")
                    l6.grid(row=0, column=5, pady=2, padx=2)
                else:
                    if x == 1:
                        global lesson_combo
                        # oddelat posledni moznost - CALL
                        lesson_combo = ttk.Combobox(content_lesson_add, value=var.lesson_type_options, state="readonly")
                        lesson_combo.grid(row=y, column=x, pady=2, padx=3)
                        lesson_combo.bind("<<ComboboxSelected>>", self.combobox_lesson_duration_selected)
                        lesson_entries.append(lesson_combo)
                    elif x == 2:
                        global lesson_entry_duration
                        lesson_entry_duration = tk.Entry(content_lesson_add)
                        lesson_entry_duration.grid(row=y, column=x, pady=2, padx=3)
                        lesson_entries.append(lesson_entry_duration)
                    elif x == 3:
                        global lesson_entry_money_student
                        lesson_entry_money_student = tk.Entry(content_lesson_add)
                        lesson_entry_money_student.grid(row=y, column=x, pady=2, padx=3)
                        lesson_entries.append(lesson_entry_money_student)
                    elif x == 4:
                        global lesson_entry_money_teacher
                        lesson_entry_money_teacher = tk.Entry(content_lesson_add)
                        lesson_entry_money_teacher.grid(row=y, column=x, pady=2, padx=3)
                        lesson_entries.append(lesson_entry_money_teacher)
                    else:
                        if x == 0:
                            lesson_entries.append(student_combo)
                            lesson_entries.append(lector_combo)

                        lesson_entry = tk.Entry(content_lesson_add)
                        lesson_entry.grid(row=y, column=x, pady=2, padx=3)
                        lesson_entries.append(lesson_entry)

        call_l = tk.Entry(content_lesson_add, fg=var.dark, relief=tk.SUNKEN, justify=tk.CENTER)
        call_l.insert(tk.END, 'CALLs')
        call_l.config(state=tk.DISABLED)
        call_l.grid(row=22, column=0, pady=2, padx=3)
        call_l1 = tk.Label(content_lesson_add, text="Datum (rok-měsíc-den)")
        call_l1.grid(row=21, column=1, pady=2, padx=2)
        call_l3 = tk.Label(content_lesson_add, text="Počet CALLS")
        call_l3.grid(row=21, column=2, pady=2, padx=2)
        call_l4 = tk.Label(content_lesson_add, text="Cena (student)")
        call_l4.grid(row=21, column=3, pady=2, padx=2)
        call_l5 = tk.Label(content_lesson_add, text="Zisk (Lektor)")
        call_l5.grid(row=21, column=4, pady=2, padx=2)
        call_l6 = tk.Label(content_lesson_add, text="Dodatečné informace")
        call_l6.grid(row=21, column=5, pady=2, padx=2)

        call_entry1 = tk.Entry(content_lesson_add)
        call_entry1.grid(row=22, column=1, pady=2, padx=3)
        # pocet
        global call_number, call_entry3, call_entry4
        call_number = tk.StringVar()
        call_entry2 = tk.Entry(content_lesson_add, textvariable=call_number)
        call_entry2.grid(row=22, column=2, pady=2, padx=3)
        call_number.trace('w', self.get_number_calls)
        call_entry3 = tk.Entry(content_lesson_add)
        call_entry3.grid(row=22, column=3, pady=2, padx=3)
        call_entry4 = tk.Entry(content_lesson_add)
        call_entry4.grid(row=22, column=4, pady=2, padx=3)
        call_entry5 = tk.Entry(content_lesson_add)
        call_entry5.grid(row=22, column=5, pady=2, padx=3)

        lesson_entries.append(student_combo)
        lesson_entries.append(lector_combo)
        lesson_entries.append(call_l)
        lesson_entries.append(call_entry2)
        lesson_entries.append(call_entry3)
        lesson_entries.append(call_entry4)
        lesson_entries.append(call_entry5)

        entry_button = ttk.Button(content_lesson_add, text="Uložit lekce", command=lambda: [self.print_lesson(lesson_entries)])
        entry_button.grid(row=23, column=0, pady=10, padx=10, columnspan=6, ipadx=100)

    def get_number_calls(self, *args):
        number_entred = call_number.get()
        teacher_value = 0
        student_value = 0

        for item in teacher_rate_rows:
            if item[0] == "CALL":
                student_value = item[1]
                teacher_value = item[2]

        if len(number_entred) != 0 and number_entred.isnumeric():
            call_entry3.delete(0, tk.END)
            call_entry3.insert(tk.END, str(int(student_value) * int(call_number.get())))
            call_entry4.delete(0, tk.END)
            call_entry4.insert(tk.END, str(int(teacher_value) * int(call_number.get())))
        if len(number_entred) == 0:
            call_entry4.delete(0, tk.END)
            call_entry3.delete(0, tk.END)

    def print_lesson(self, lesson_entries):
        entry_list = list()
        final_entry_list = []
        i = 0
        global num_incorrect_entry
        num_incorrect_entry = 0

        print(lesson_entries)

        for entry in lesson_entries:
            if i % 8 == 7:
                # print("i % 5 == 4 -> {}".format(i))
                entry_list.append(entry.get())
                if len(entry_list[1]) != 0 and len(entry_list[2]) != 0 and len(entry_list[3]) != 0 and len(entry_list[4]) != 0 and len(entry_list[5]) != 0 and len(entry_list[6]) != 0:
                    if re.match("[0-9]{4}\-?[0-9]{2}\-?[0-9]{2}", entry_list[2]) and re.match("[0-9]", entry_list[4]) and re.match("[0-9]", entry_list[5]) and re.match("[0-9]", entry_list[6]):
                        print(entry_list)
                        final_entry_list.append(tuple(entry_list))
                    else:
                        print(entry_list)
                        print("incorrect entry")
                        num_incorrect_entry += 1
                else:
                    print("list is empty, not adding to DB")
                entry_list.clear()
                i += 1
            else:
                entry_list.append(entry.get())
                i += 1

        print(final_entry_list)
        print("pocet incorrect entry:{}".format(num_incorrect_entry))
        if num_incorrect_entry == 0:
            add_lessons.destroy()
            self.add_to_database(final_entry_list)
        else:
            messagebox.showerror("Chyba", "Všechny údaje o lekcích nebyly vyplněny správně. Zkontorlujete jednotlivé informace a znovu lekce uložte.")
            num_incorrect_entry = 0
            add_lessons.lift()

    def add_to_database(self, final_entry_list):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        sql = "INSERT INTO lesson (lesson_id, lesson_student, lesson_teacher, lesson_date, lesson_type, lesson_duration, lesson_student_price, " \
              "lesson_teacher_price, lesson_info) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c.executemany(sql, final_entry_list)

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        lector.show_lectors(self)
        lector.show_lectors_money(self)
        self.show_lesson()

    def combobox_teacher_selected(self, *args):
        choosen_lector = lector_combo.get()

        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        sql = "SELECT rate_time, rate_student_money, rate_teacher_money FROM rate WHERE rate_teacher_name LIKE '%" + choosen_lector + "%'"
        c.execute(sql)

        global teacher_rate_rows
        teacher_rate_rows = c.fetchall()

        print(teacher_rate_rows)

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def combobox_year_month_selected(self, *args):
        l_tree.delete(*l_tree.get_children())

        print(month_option.get())
        print(year_option.get())
        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        student = s_entry.get("1.0", 'end-1c')
        if student == "Jméno studenta":
            student = ""
        teacher = t_entry.get("1.0", 'end-1c')
        if teacher == "Jméno lektora":
            teacher = ""

        month = month_option.get()
        print(month)
        month_number = ""
        if not month == "vše":
            print(var.month.index(month) + 1)
            month_number = str(var.month.index(month) + 1)
            if len(month_number) == 1:
                month_number = "0" + month_number
        print(month_number)

        sql = "SELECT * from lesson WHERE lesson_student LIKE '%" + student + "%' AND lesson_teacher LIKE '%" + teacher + "%' AND lesson_date LIKE '%" + str(
            year_option.get()) + "-" + month_number + "%' ORDER BY lesson_student DESC, lesson_date"
        c.execute(sql)
        print(sql)
        rows = c.fetchall()
        for row in rows:
            # print(row)
            l_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def combobox_lesson_duration_selected(self, eff):
        print(lector_combo.get())
        row = eff.widget.grid_info()['row']
        elements_duration = content_lesson_add.grid_slaves(row=row, column=1)
        elements_duration_number = elements_duration[0].get()

        student_payment = 0
        teacher_payment = 0

        for item in teacher_rate_rows:
            if item[0] == elements_duration_number:
                student_payment = item[1]
                teacher_payment = item[2]

        duration = ""
        if elements_duration_number != "CALL":
            duration = elements_duration_number[len(elements_duration_number) - 2:]
            print(duration)
        else:
            print("CALL")

        elements_duration_lesson = content_lesson_add.grid_slaves(row=row, column=2)
        elements_duration_lesson[0].delete(0, tk.END)
        elements_duration_lesson[0].insert(tk.END, str(duration))

        elements_student = content_lesson_add.grid_slaves(row=row, column=3)
        elements_student[0].delete(0, tk.END)
        elements_student[0].insert(tk.END, str(student_payment))

        elements_teacher = content_lesson_add.grid_slaves(row=row, column=4)
        elements_teacher[0].delete(0, tk.END)
        elements_teacher[0].insert(tk.END, str(teacher_payment))

    def filter_lesson(self, teacher, student):
        # print("filtrovat")
        if student == "Jméno studenta":
            student = ""
        if teacher == "Jméno lektora":
            teacher = ""

        print("student {}-".format(student))
        print("lector {}-".format(teacher))

        month = month_option.get()
        print(month)
        month_number = ""
        if not month == "vše":
            print(var.month.index(month) + 1)
            month_number = str(var.month.index(month) + 1)
            if len(month_number) == 1:
                month_number = "0" + month_number
        print(month_number)

        l_tree.delete(*l_tree.get_children())

        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        sql = "SELECT * from lesson WHERE lesson_student LIKE '%" + student + "%' AND lesson_teacher LIKE '%" + teacher + "%' AND lesson_date LIKE '%" + str(
            year_option.get()) + "-" + month_number + "%' ORDER BY lesson_student DESC, lesson_date"
        print(sql)
        c.execute(sql)
        rows = c.fetchall()
        for row in rows:
            # print(row)
            l_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def get_choosen_line(self, event):
        self.selected = event.widget.selection()

    def delete_lesson(self, lesson_ID):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        if len(lesson_ID) == 0:
            print("nothing choosen")
        else:
            number_of_lessons = "lekce"
            # Create cursor
            c = conn.cursor()
            if len(lesson_ID) == 1:
                number_of_lessons = "lekci"

            response = messagebox.askyesno("Lekce", "Chcete opravdu {num} odstranit z databáze?".format(num=number_of_lessons))
            if response == 1:
                # delete record
                for id in self.selected:
                    c.execute("DELETE from lesson WHERE oid=" + str(l_tree.item(id)["text"]))
                    print("Lekce byly odstraněny z databáze.")
            else:
                print("lekce nebyly odstraněny z databáze.")

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        self.show_lesson()

    def default_text_entry_student(self, event):
        student = s_entry.get("1.0", tk.END)
        if student == "Jméno studenta\n":
            s_entry.delete("1.0", tk.END)
        elif student == "\n":
            s_entry.insert("1.0", "Jméno studenta")

    def default_text_entry_lector(self, event):
        lector = t_entry.get("1.0", tk.END)
        print(lector)
        if lector == "Jméno lektora\n":
            t_entry.delete("1.0", tk.END)
        elif lector == "\n":
            t_entry.insert("1.0", "Jméno lektora")

    def filter_student_teacher_entry(self, event):
        student = s_entry.get("1.0", 'end-1c')
        print(student)
        teacher = t_entry.get("1.0", 'end-1c')
        print(teacher)
        self.filter_lesson(teacher, student)
        return 'break'
