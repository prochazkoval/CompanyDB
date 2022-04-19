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
import variables as var
from tkinter import messagebox
import re


class PaymentPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        header_payment = tk.Frame(self, bg=var.dark)
        content_payment = tk.Frame(self)
        footer_payment = tk.Frame(self)

        header_payment.pack(fill="x", expand=False)
        content_payment.pack(fill=tk.BOTH, expand=True)
        footer_payment.pack(fill="x", expand=False)

        label1 = tk.Label(master=header_payment, text="Platby", font=controller.title_header_font,
                          bg=var.dark, fg=var.white)
        label1.pack(side="left", fill="x", pady=10, padx=10)
        b3 = ttk.Button(header_payment, text="Filtrovat", command=lambda: self.filter_payment(entry.get("1.0", 'end-1c')))
        b3.pack(side="right", pady=10, padx=10)

        global entry
        entry = tk.Text(header_payment, width=16, height=1)
        entry.insert(tk.END, "Jméno studenta")
        entry.pack(side="right", pady=10, padx=10)
        entry.bind("<FocusIn>", self.default_text_entry)
        entry.bind("<FocusOut>", self.default_text_entry)
        entry.bind("<Return>", self.filter_payment_entry)

        global year_option
        year_option = ttk.Combobox(header_payment, value=var.year, state="readonly", width=5)
        year_option.current(var.year.index(var.year_date))
        year_option.pack(side="right", pady=10, padx=1)
        year_option.bind("<<ComboboxSelected>>", self.combobox_year_month_selected)

        global month_option
        month_option = ttk.Combobox(header_payment, value=var.month, state="readonly", width=10)
        month_option.current(var.month_index)
        month_option.pack(side="right", pady=10, padx=1)
        month_option.bind("<<ComboboxSelected>>", self.combobox_year_month_selected)

        b1 = ttk.Button(header_payment, text="Přidat platby", command=lambda: self.open_add_payment())
        b1.pack(side="left", pady=10, padx=10)

        self.selected = []

        b3 = ttk.Button(header_payment, text="Odstranit platby", command=lambda: self.delete_payment(self.selected))
        b3.pack(side="left", pady=10, padx=10)

        global p_tree
        p_scrollbar = ttk.Scrollbar(content_payment)
        p_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # ID, kdo, kolik, kdy, jak, info
        # TODO filtrování na základě jména + času
        p_tree = ttk.Treeview(content_payment, columns=("name", "amount", "date", "how", "info"), yscrollcommand=p_scrollbar.set)
        p_scrollbar.config(command=p_tree.yview)

        p_tree.bind("<<TreeviewSelect>>", self.get_choosen_line)
        p_tree.column("#0", width=45, minwidth=15, anchor="w", stretch="NO")
        p_tree.column("name", width=200, minwidth=25, anchor="w", stretch="NO")
        p_tree.column("amount", width=100, minwidth=25, anchor="w", stretch="NO")
        p_tree.column("date", width=130, minwidth=25, anchor="w", stretch="NO")
        p_tree.column("how", width=100, minwidth=25, anchor="w", stretch="NO")
        p_tree.column("info", width=200, minwidth=25, anchor="w", stretch="YES")

        p_tree.heading("#0", text="ID", anchor="w")
        p_tree.heading("name", text="Student", anchor="w")
        p_tree.heading("amount", text="Částka (Kč)", anchor="w")
        p_tree.heading("date", text="Datum", anchor="w")
        p_tree.heading("how", text="Způsob", anchor="w")
        p_tree.heading("info", text="Dodatečné informace", anchor="w")

        p_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        # footer
        label4 = tk.Label(footer_payment, text=var.version, font=controller.title_text_font)
        label4.pack(side="left", padx=10)
        label2 = tk.Label(footer_payment, text=var.company, font=controller.title_text_font)
        label2.pack(side="right", padx=10)

        return

    def get_choosen_line(self, event):
        self.selected = event.widget.selection()

    def print_payment(self, payment_entries):
        entry_list = list()
        final_entry_list = []
        i = 0
        global num_incorrect_entry
        num_incorrect_entry = 0

        for entry in payment_entries:
            if i % 5 == 4:
                entry_list.append(entry.get())
                if len(entry_list[0]) != 0 and len(entry_list[1]) != 0 and len(entry_list[2]) != 0 and len(entry_list[3]) != 0:
                    if entry_list[1].isnumeric() and len(entry_list[2]) == 10 and re.match("[0-9]{4}\-?[0-9]{2}\-?[0-9]{2}", entry_list[2]):
                        final_entry_list.append(tuple(entry_list))
                        print(final_entry_list)
                    else:
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
            self.add_payments.destroy()
            self.add_to_database(final_entry_list)
        else:
            messagebox.showerror("Chyba", "Všechny údaje o platbách nebyly vyplněny správně. Zkontorlujete jednotlivé informace a znovu platby uložte.")
            num_incorrect_entry = 0
            self.add_payments.lift()

    def add_to_database(self, final_entry_list):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        sql = "INSERT INTO payment (payment_id, payment_student, payment_value, payment_date, payment_type, payment_info) VALUES (NULL, ?, ?, ?, ?, ?)"
        c.executemany(sql, final_entry_list)

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        self.show_payment()

    def open_add_payment(self):
        """
            Open new window to add new payments
        """
        global add_payments
        self.add_payments = tk.Toplevel()
        # self.add_payments.geometry("700x300")
        self.add_payments.resizable(False, False)
        self.add_payments.title("Přidat platby")
        self.add_payments.iconbitmap(var.icon)

        header_add_payment = tk.Frame(self.add_payments, bg=var.dark)
        header_add_payment.grid(row=0, column=0, sticky="NEWS")
        content_add_payment = tk.Frame(self.add_payments)
        content_add_payment.grid(row=1, column=0, sticky="NEWS")

        header_add_payment.grid_columnconfigure(0, weight=1)
        header_add_payment.grid_columnconfigure(1, weight=1)
        header_add_payment.grid_columnconfigure(2, weight=1)
        header_add_payment.grid_columnconfigure(3, weight=1)
        header_add_payment.grid_columnconfigure(4, weight=1)

        l1 = tk.Label(header_add_payment, text="    Student   ", bg=var.dark, fg=var.white, font=("DejaVu Sans", 10, "bold"))
        l1.grid(row=0, column=0, pady=10, padx=10)
        l2 = tk.Label(header_add_payment, text="       Částka (Kč)", bg=var.dark, fg=var.white, font=("DejaVu Sans", 10, "bold"))
        l2.grid(row=0, column=1, pady=10, padx=10)
        l3 = tk.Label(header_add_payment, text="    Datum    ", bg=var.dark, fg=var.white, font=("DejaVu Sans", 10, "bold"))
        l3.grid(row=0, column=2, pady=10, padx=10)
        l4 = tk.Label(header_add_payment, text="       Způsob        ", bg=var.dark, fg=var.white, font=("DejaVu Sans", 10, "bold"))
        l4.grid(row=0, column=3, pady=10, padx=10)
        l5 = tk.Label(header_add_payment, text="Dodatečné info", bg=var.dark, fg=var.white, font=("DejaVu Sans", 10, "bold"))
        l5.grid(row=0, column=4, pady=10, padx=10)

        content_add_payment.grid_columnconfigure(0, weight=1)
        content_add_payment.grid_columnconfigure(1, weight=1)
        content_add_payment.grid_columnconfigure(2, weight=1)
        content_add_payment.grid_columnconfigure(3, weight=1)
        content_add_payment.grid_columnconfigure(4, weight=1)

        # ID, kdo, kolik, kdy, jak, info
        payment_entries = []
        global payment_combo_student, payment_combo_type

        # row loop
        for y in range(10):
            # column loop
            for x in range(5):
                if x == 0:
                    payment_combo_student = ttk.Combobox(content_add_payment, values=var.student_list, state="readonly")
                    payment_combo_student.grid(row=y, column=x, pady=2, padx=3)
                    payment_entries.append(payment_combo_student)
                elif x == 3:
                    payment_combo_type = ttk.Combobox(content_add_payment, values=var.payment_options, state="readonly")
                    payment_combo_type.grid(row=y, column=x, pady=2, padx=3)
                    payment_entries.append(payment_combo_type)
                else:
                    payment_entry = tk.Entry(content_add_payment)
                    payment_entry.grid(row=y, column=x, pady=2, padx=3)
                    payment_entries.append(payment_entry)

        entry_button = ttk.Button(content_add_payment, text="Uložte platby", command=lambda: [self.print_payment(payment_entries)])
        entry_button.grid(row=10, column=0, pady=10, padx=10, columnspan=5, ipadx=100)

    # TODO změnit na option menu pro filtrování podle roku + měsíce - defaultní nastavení aktuální měsíc
    def filter_payment(self, student):
        if student == "Jméno studenta":
            student = ""

        p_tree.delete(*p_tree.get_children())

        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        month = month_option.get()
        print(month)
        month_number = ""
        if not month == "vše":
            month = month_option.get()
            print(var.month.index(month) + 1)
            month_number = str(var.month.index(month)+ 1)
            if len(month_number) == 1:
                month_number = "0" + month_number
        print(month_number)

        sql = "SELECT * from payment WHERE payment_student LIKE '%" + student + "%' AND payment_date LIKE '%" + str(year_option.get()) + "-" + month_number + "%' ORDER BY payment_date"

        c.execute(sql)
        rows = c.fetchall()
        for row in rows:
            # print(row)
            p_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def default_text_entry(self, event):
        current = entry.get("1.0", tk.END)
        if current == "Jméno studenta\n":
            entry.delete("1.0", tk.END)
        elif current == "\n":
            entry.insert("1.0", "Jméno studenta")

    def show_payment(self):
        """
            Update payment list in p_tree
        """
        p_tree.delete(*p_tree.get_children())
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        month = month_option.get()
        print(month)
        month_number = ""
        if not month == "vše":
            month = month_option.get()
            print(var.month.index(month) + 1)
            month_number = str(var.month.index(month) + 1)
            if len(month_number) == 1:
                month_number = "0" + month_number
        print(month_number)

        c.execute("SELECT * from payment WHERE payment_date LIKE '%" + str(year_option.get()) + "-" + month_number + "%' ORDER BY payment_date")
        rows = c.fetchall()
        for row in rows:
            # print(row)
            p_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def delete_payment(self, payment_ID):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        if len(payment_ID) == 0:
            print("nothing choosen")
        else:
            number_of_payments="platby"
            # Create cursor
            c = conn.cursor()
            if len(payment_ID)==1:
                number_of_payments="platbu"

            response = messagebox.askyesno("Platba", "Chcete opravdu {num} odstranit z databáze?".format(num=number_of_payments))
            if response == 1:
                # delete record
                for id in self.selected:
                    c.execute("DELETE from payment WHERE oid=" + str(p_tree.item(id)["text"]))
                    print("Platby byly odstraněn z databáze.")
            else:
                print("Platby nebyly odstraněn z databáze.")

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        self.show_payment()

    def combobox_year_month_selected(self, *args):
        p_tree.delete(*p_tree.get_children())

        print(month_option.get())
        print(year_option.get())
        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        student = entry.get("1.0", 'end-1c')
        if student == "Jméno studenta":
            student = ""

        month = month_option.get()
        print(month)
        month_number = ""
        if not month == "vše":
            month = month_option.get()
            print(var.month.index(month) + 1)
            month_number = str(var.month.index(month) + 1)
            if len(month_number) == 1:
                month_number = "0" + month_number
        print(month_number)

        sql = "SELECT * from payment WHERE payment_student LIKE '%" + student + "%' AND payment_date LIKE '%" + str(year_option.get()) + "-" + month_number + "%' ORDER BY payment_date"
        c.execute(sql)
        print(sql)
        rows = c.fetchall()
        for row in rows:
            # print(row)
            p_tree.insert("", tk.END, text=row[0], values=(row[1], row[2], row[3], row[4], row[5]))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

    def filter_payment_entry(self, event):
        search = entry.get("1.0", 'end-1c')
        self.filter_payment(search)
        return 'break'
