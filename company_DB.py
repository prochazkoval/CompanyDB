from builtins import print

try:
    # Python2
    import Tkinter as tk
    import ttk
except ImportError:
    # Python3
    import tkinter as tk
    import tkinter.ttk as ttk
from tkinter import font as tkfont
from tkinter import messagebox
import sqlite3
import menu, student, lector, payment, lesson, info
import variables as var
import utils as utils
import os

import win32com.client as client
import pathlib

from tkcalendar import DateEntry

from reportlab.lib.units import mm
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, TableStyle, Spacer, Paragraph
from reportlab.platypus.tables import Table
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import subprocess

# TODO: tkcalendar import


class Login:
    def __init__(self, root):
        global login_master
        self.login_master = root
        self.login_master.title("Firemní databáze")
        self.login_master.iconbitmap(var.icon)
        self.login_master.resizable(False, False)
        self.login_master.geometry('360x150')
        self.login_frame = tk.Frame(self.login_master)
        # self.login_frame.config(bg="violet")
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        # self.frame.grid(row=0, column=0, sticky="nsew")

        global Username, Userpasswd

        Username = tk.StringVar()
        Userpasswd = tk.StringVar()

        topLoginFrame = tk.Frame(self.login_frame)
        topLoginFrame.pack(side=tk.TOP, fill=tk.X, expand=True)

        userLoginFrame = tk.Frame(self.login_frame)
        userLoginFrame.pack(fill=tk.BOTH, expand=True)

        passwdLoginFrame = tk.Frame(self.login_frame)
        passwdLoginFrame.pack(fill=tk.BOTH, expand=True)

        bottomtopLoginFrame = tk.Frame(self.login_frame)
        bottomtopLoginFrame.pack(fill=tk.X, expand=True)

        lblTitle = tk.Label(topLoginFrame, text="Přihlášení do firemní databáze", font=("DejaVu Sans", 12, "bold"), bg=var.dark, fg=var.white)
        lblTitle.pack(fill=tk.BOTH, expand=True, ipady=5)

        lblUsername = tk.Label(userLoginFrame, text="Uživatelské jméno:")
        lblUsername.pack(side=tk.LEFT, pady=5, padx=10)

        EntryUsername = tk.Entry(userLoginFrame, textvariable=Username, width=35)
        EntryUsername.pack(side=tk.RIGHT, pady=5, padx=10)

        lblUsername = tk.Label(passwdLoginFrame, text="Uživatelské heslo:")
        lblUsername.pack(side=tk.LEFT, pady=5, padx=10)

        EntryUserpasswd = tk.Entry(passwdLoginFrame, textvariable=Userpasswd, show="*", width=35)
        EntryUserpasswd.pack(side=tk.RIGHT, pady=5, padx=10)

        btnLogin = ttk.Button(bottomtopLoginFrame, text="Přihlásit", width=15, command=self.login_menu)
        btnLogin.pack(side=tk.LEFT, expand=True, pady=10)
        btnLogin.bind('<Return>', lambda event: self.login_menu())

        btnReset = ttk.Button(bottomtopLoginFrame, text="Smazat údaje", width=15, command=self.delete_login_content)
        btnReset.pack(side=tk.LEFT, expand=True, pady=10)
        btnReset.bind('<Return>', lambda event: self.delete_login_content())

        btnQuit = ttk.Button(bottomtopLoginFrame, text="Ukončit aplikaci", width=15, command=self.exit_login_window)
        btnQuit.pack(side=tk.LEFT, expand=True, pady=10)
        btnQuit.bind('<Return>', lambda event: self.exit_login_window())

    def login_menu(self):
        user = Username.get()
        passwd = Userpasswd.get()
        if user == str(1) and passwd == "1":
            self.Login_Window()
        else:
            messagebox.showerror("Firemní databáze", "Přihlášení do firemní databáze se nezdařilo. Překontrolujte správnost přihlašovacích údajů")
            Username.set("")
            Userpasswd.set("")

    def Login_Window(self):
        # self.SystemWindow = tk.Toplevel(self.login_master)
        Main(self.login_master)
        self.login_master.resizable(True, True)
        self.login_master.geometry("850x560")
        self.login_master.minsize(850, 560)
        self.login_frame.destroy()

    def delete_login_content(self):
        Username.set("")
        Userpasswd.set("")

    def exit_login_window(self):
        exit = messagebox.askyesno("Firemní databáze", "Chcete aplikaci opravdu ukončit?")
        if exit:
            self.login_master.destroy()
            return


class Main():
    def __init__(self, root):
        print(os.path.expanduser('~'))

        #############################################################
        # CREATE DATABASE
        #############################################################
        # Create folder CompDB
        if not os.path.exists(var.db_folder):
            os.makedirs(var.db_folder)

        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        conn.execute("PRAGMA foreign_keys = ON")
        # Create cursor
        my_cursor = conn.cursor()

        # Create students database
        my_cursor.execute("""CREATE TABLE IF NOT EXISTS student (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                	student_name TEXT,
                	student_mail TEXT,
                	student_phone TEXT, 
                	student_level TEXT,	
                	student_course TEXT,
                	student_is_adult TEXT,
                	student_parent_mail TEXT,
                	student_parent_phone TEXT,
                	student_info TEXT (100))""")

        # Create teachers database
        my_cursor.execute("""CREATE TABLE IF NOT EXISTS teacher (
                    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                	teacher_name TEXT,
                	teacher_mail TEXT,
                	teacher_phone TEXT,
                	teacher_birthday TEXT,
                	teacher_info TEXT)""")

        # my_cursor.execute("""DROP TABLE payment""")
        my_cursor.execute("""CREATE TABLE IF NOT EXISTS payment (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                	payment_student TEXT NOT NULL,
                	payment_value INT NOT NULL, 
                	payment_date TEXT NOT NULL,
                	payment_type TEXT NOT NULL,
                	payment_info TEXT,
                	FOREIGN KEY(payment_student) REFERENCES student (student_name) ON DELETE SET NULL)""")
        #

        # my_cursor.execute("""DROP TABLE lesson""")
        my_cursor.execute("""CREATE TABLE IF NOT EXISTS lesson (
                    lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
                	lesson_student TEXT,
                	lesson_teacher TEXT,
                	lesson_date TEXT,
                	lesson_type TEXT,
                	lesson_duration TEXT,
                	lesson_student_price INT,
                	lesson_teacher_price INT,
                	lesson_info TEXT,
                	FOREIGN KEY(lesson_student) REFERENCES student(student_name),
                    FOREIGN KEY(lesson_teacher) REFERENCES teacher(teacher_name))""")

        # my_cursor.execute("""DROP TABLE rate""")
        # Create teachers database
        my_cursor.execute("""CREATE TABLE IF NOT EXISTS rate (
                    rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                	rate_teacher_name TEXT,
                	rate_time TEXT,
                	rate_student_money TEXT,
                	rate_teacher_money TEXT)""")

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()

        # ===================================
        # import os
        # if os.path.exists(r"C:\Users\42073\Desktop\DP\var.db"):
        #   os.remove(r"C:\Users\42073\Desktop\DP\var.db")
        # ==================================

        self.root = root
        self.root.title("Firemní databáze")
        self.title_header_font = tkfont.Font(size=18, weight="bold")
        self.title_text_font = tkfont.Font(size=8)
        self.root.resizable(True, True)
        self.root.geometry("850x560")
        self.root.minsize(850, 560)
        self.root.iconbitmap(var.icon)

        self.container = tk.Frame(root)
        # self.container.configure(bg=var.white)
        self.container.pack(side="top", fill="both", expand=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frames["MenuPage"] = menu.MenuPage(parent=self.container, controller=self)
        self.frames["LectorPage"] = lector.LectorPage(parent=self.container, controller=self)
        self.frames["StudentPage"] = student.StudentPage(parent=self.container, controller=self)
        self.frames["LessonPage"] = lesson.LessonPage(parent=self.container, controller=self)
        self.frames["PaymentPage"] = payment.PaymentPage(parent=self.container, controller=self)
        self.frames["InfoPage"] = info.InfoPage(parent=self.container, controller=self)

        self.frames["MenuPage"].grid(row=0, column=0, sticky="nsew")
        # self.frames["MenuPage"].configure(bg="#FBF3F2")
        self.frames["LectorPage"].grid(row=0, column=0, sticky="nsew")
        # self.frames["LectorPage"].configure(bg="#FBF3F2")
        self.frames["StudentPage"].grid(row=0, column=0, sticky="nsew")
        # self.frames["StudentPage"].configure(bg="#FBF3F2")
        self.frames["LessonPage"].grid(row=0, column=0, sticky="nsew")
        # self.frames["LessonPage"].configure(bg="#FBF3F2")
        self.frames["PaymentPage"].grid(row=0, column=0, sticky="nsew")
        # self.frames["PaymentPage"].configure(bg="#FBF3F2")
        self.frames["InfoPage"].grid(row=0, column=0, sticky="nsew")
        # self.frames["InfoPage"].configure(bg="#FBF3F2")

        self.raise_frame("MenuPage")

        top_menu = tk.Menu(root)
        menuApp = tk.Menu(top_menu, tearoff=0)
        menuApp.add_command(label="Menu", command=lambda: self.raise_frame("MenuPage"))
        menuApp.add_command(label="Vygenerovat přehled", command=lambda: self.generate_summary())
        # menuApp.add_command(label="Uložit", command=None)
        menuApp.add_command(label="Vytvořit zálohu", command=lambda: self.zip_choose_pasword())
        menuApp.add_command(label="Informace o aplikaci", command=lambda: [self.raise_frame("InfoPage"), self.resize()])
        menuApp.add_separator()
        menuApp.add_command(label="Odhlásit se", command=self.logout_menu)
        menuApp.add_command(label="Ukončit aplikaci", command=self.exit_main_window)
        top_menu.add_cascade(label="Aplikace", menu=menuApp)

        menuLektor = tk.Menu(top_menu, tearoff=0)
        menuLektor.add_command(label="Výpis lektorů", command=lambda: [self.raise_frame("LectorPage"), self.resize(), lector.LectorPage.show_lectors(
            self.root)])
        menuLektor.add_command(label="Přidat lektora", command=lambda: None)
        menuLektor.add_command(label="Najít lektora", command=None)
        top_menu.add_cascade(label="Lektoři", command=lambda: [self.raise_frame("LectorPage"), self.resize(), lector.LectorPage.show_lectors(
            self.root), lector.LectorPage.show_lectors_money(self.root)])

        menuStudent = tk.Menu(top_menu, tearoff=0)
        menuStudent.add_command(label="Výpis studentů", command=lambda: [self.raise_frame("StudentPage"), self.resize()])
        menuStudent.add_command(label="Přidat studenta", command=lambda: None)
        menuStudent.add_command(label="Najít studenta", command=None)
        top_menu.add_cascade(label="Studenti", command=lambda: [self.raise_frame("StudentPage"), self.resize(), student.StudentPage.show_students(self.root), student.StudentPage.show_students_money(
            self.root)])

        menuLekce = tk.Menu(top_menu, tearoff=0)
        menuLekce.add_command(label="Výpis lekcí", command=lambda: [self.raise_frame("LessonPage"), self.resize()])
        menuLekce.add_command(label="Přidat lekce", command=lambda: None)
        menuLekce.add_command(label="Poslat výpis lekcí", command=None)
        top_menu.add_cascade(label="Lekce", command=lambda: [self.raise_frame("LessonPage"), self.resize(), lesson.LessonPage.show_lesson(self.root)])

        menuPlatby = tk.Menu(top_menu, tearoff=0)
        menuPlatby.add_command(label="Výpis plateb", command=lambda: [self.raise_frame("PaymentPage"), self.resize()])
        menuPlatby.add_command(label="Přidat platby", command=None)
        menuPlatby.add_command(label="Poslat výpis plateb", command=None)
        top_menu.add_cascade(label="Platby", command=lambda: [self.raise_frame("PaymentPage"), self.resize(), payment.PaymentPage.show_payment(self.root)])

        root.config(menu=top_menu)

        utils.Utils.load_students(self.root)
        utils.Utils.load_teachers(self.root)

        return

    def raise_frame(self, frame_name):
        """
            Show a frame for the given name
        """
        frame = self.frames[frame_name]
        frame.tkraise()

    def resize(self):
        if not var.resized:
            print("resize")
            # self.root.state('zoomed')
            var.resized = True

    def exit_main_window(self):
        exit = messagebox.askyesno("Firemní databáze", "Chcete aplikaci opravdu ukončit?")
        print(exit)
        if exit:
            self.root.destroy()

    def logout_menu(self):
        # self.SystemWindow = tk.Toplevel(self.login_master)
        logout = messagebox.askyesno("Firemní databáze", "Chcete se opravdu odhlásit?")
        print(logout)
        if logout:
            emptyMenu = tk.Menu(root)
            root.config(menu=emptyMenu)
            self.root.geometry("360x150")
            self.root.minsize(360, 150)
            self.root.maxsize(360, 150)
            self.root.resizable(False, False)
            print("resize")
            Login(self.root)
            self.container.destroy()

    def create_report(self, type, date):
        begining_date = ""
        ending_date = ""
        sql = ""

        if date == 1:
            begining_date = str(var.year_date) + "-" + str(var.month_date) + "-01"
            ending_date = str(var.year_date) + "-" + str(var.month_date) + "-31"
            print(begining_date, ending_date)
        elif date == 2:
            school_year = utils.Utils.get_school_year(self)
            begining_date = str(school_year[0:4]) + "-09-01"
            ending_date = str(school_year[5:9]) + "-08-31"
            print(begining_date, ending_date)
        elif date == 3:
            begining_date = calstart.get_date()
            ending_date = calstop.get_date()
            print(begining_date, ending_date)

        if type not in [1, 2, 3, 4]:
            messagebox.showerror("Firemní databáze", "Chyba při generování přehledu. Některý z údajů nebyl zvolen správně.")
        else:
            print(sql)
            self.print_summary_PDF(type, begining_date, ending_date)

    def generate_summary(self):
        """
            Open new window to generate summary (lesson, lector...)
        """
        # generovani prehledu na zaklade pozadavku, vyledek je vygenerovane PDF
        # je mozno zvolit, zda chceme vygenerovat za zvoleny mesic prehled vsech plateb, leci a nebo lektory a studenty

        global choose_summary
        self.choose_summary = tk.Toplevel()
        # self.choose_summary.geometry("500x250")
        self.choose_summary.resizable(False, False)
        self.choose_summary.title("Firemní databáze")
        self.choose_summary.iconbitmap(var.icon)

        sum_top = tk.Frame(self.choose_summary, bg=var.dark)
        sum_center = tk.Frame(self.choose_summary)
        sum_bottom = tk.Frame(self.choose_summary)

        sum_top.pack(fill="x", expand=False)
        sum_center.pack(fill=tk.BOTH, expand=True)
        sum_bottom.pack(fill="x", expand=False)

        sum_center_left = tk.Frame(sum_center)
        sum_center_left.pack(side="left", fill=tk.BOTH, expand=True)
        sum_center_right = tk.Frame(sum_center)
        sum_center_right.pack(side="left", fill=tk.BOTH, expand=True)

        sum_top_lbl = tk.Label(sum_top, text="Zvolte parametry pro vygenerování přehledu", font=("DejaVu Sans", 12, "bold"), bg=var.dark, fg=var.white)
        sum_top_lbl.pack(ipady=10)

        # global option_choosen
        option_group_choosen = tk.IntVar()

        option_lbl = tk.Label(sum_center_left, text="Zvolte požadovanou skupinu", font=("DejaVu Sans", 9, "bold"))
        option_lbl.pack(padx=10, anchor=tk.W)

        radiobutton_option = tk.Radiobutton(sum_center_left, text="Lektoři", value=1, variable=option_group_choosen, tristatevalue=0, command=self.dissable_button)
        radiobutton_option.pack(padx=10, anchor=tk.W)

        radiobutton_option1 = tk.Radiobutton(sum_center_left, text="Studenti", value=2, variable=option_group_choosen, tristatevalue=0, command=self.dissable_button)
        radiobutton_option1.pack(padx=10, anchor=tk.W)

        radiobutton_option2 = tk.Radiobutton(sum_center_left, text="Lekce", value=3, variable=option_group_choosen, tristatevalue=0, command=self.enable_button)
        radiobutton_option2.pack(padx=10, anchor=tk.W)

        radiobutton_option3 = tk.Radiobutton(sum_center_left, text="Platby", value=4, variable=option_group_choosen, tristatevalue=0, command=self.enable_button)
        radiobutton_option3.pack(padx=10, anchor=tk.W)

        option_group_choosen.set(1)

        option_month_choosen = tk.IntVar()

        option_lbl2 = tk.Label(sum_center_right, text="Zvolte požadované období", font=("DejaVu Sans", 9, "bold"))
        option_lbl2.pack(padx=10, anchor=tk.W)

        global calstart, calstop
        calstart = DateEntry(sum_center_right, width=12, background=var.light, foreground=var.white, borderwidth=2)
        calstop = DateEntry(sum_center_right, width=12, background=var.light, foreground=var.white, borderwidth=2)

        global radiobutton_option4, radiobutton_option5, radiobutton_option6
        radiobutton_option5 = tk.Radiobutton(sum_center_right, text="Aktuální měsíc a rok", value=1, variable=option_month_choosen, tristatevalue=0)
        radiobutton_option5.pack(padx=10, anchor=tk.W)

        radiobutton_option4 = tk.Radiobutton(sum_center_right, text="Aktuální školní rok", value=2, variable=option_month_choosen, tristatevalue=0)
        radiobutton_option4.pack(padx=10, anchor=tk.W)

        radiobutton_option6 = tk.Radiobutton(sum_center_right, text="Vlastní časové období", value=3, variable=option_month_choosen, tristatevalue=0, command=self.appear_date)
        radiobutton_option6.pack(padx=10, anchor=tk.W)

        radiobutton_option4.configure(state=tk.DISABLED)
        radiobutton_option5.configure(state=tk.DISABLED)
        radiobutton_option6.configure(state=tk.DISABLED)

        option_month_choosen.set(1)

        submit_btn = ttk.Button(sum_bottom, text="Vygenerovat soubor", command=lambda: [print(option_group_choosen.get(), option_month_choosen.get()), self.create_report(option_group_choosen.get(),
                                                                                                                                                                          option_month_choosen.get())])
        submit_btn.pack(padx=10, pady=10, ipady=2, ipadx=2)

    def appear_date(self):
        calstart.pack(pady=1)
        calstop.pack(pady=1)

    def dissable_button(self):
        radiobutton_option4.configure(state=tk.DISABLED)
        radiobutton_option5.configure(state=tk.DISABLED)
        radiobutton_option6.configure(state=tk.DISABLED)

    def enable_button(self):
        radiobutton_option4.configure(state=tk.NORMAL)
        radiobutton_option5.configure(state=tk.NORMAL)
        radiobutton_option6.configure(state=tk.NORMAL)

    def zip_choose_pasword(self):
        global set_pswd
        self.set_pswd = tk.Toplevel()
        self.set_pswd.minsize(100, 100)
        self.set_pswd.resizable(False, False)
        self.set_pswd.iconbitmap(var.icon)
        self.set_pswd.title("Firemní databáze")

        top_pswd = tk.Frame(self.set_pswd, bg=var.dark)
        top_pswd.pack(fill=tk.BOTH, anchor=tk.W, expand=False)
        center_pswd = tk.Frame(self.set_pswd)
        center_pswd.pack(fill=tk.BOTH, anchor=tk.W, expand=True)
        bottom_pswd = tk.Frame(self.set_pswd)
        bottom_pswd.pack(fill=tk.BOTH, anchor=tk.W, expand=False)

        center_pswd_left = tk.Frame(center_pswd)
        center_pswd_left.pack(fill=tk.BOTH, anchor=tk.W, expand=True)
        center_pswd_right = tk.Frame(center_pswd)
        center_pswd_right.pack(fill=tk.BOTH, anchor=tk.W, expand=True)

        pswdlblTitle = tk.Label(top_pswd, text="Zvolte heslo k souboru se zálohou", font=("DejaVu Sans", 12, "bold"), bg=var.dark, fg=var.white)
        pswdlblTitle.pack(fill=tk.BOTH, expand=True, ipady=5)

        pswdlblUsername = tk.Label(center_pswd_left, text="Zvolené heslo:")
        pswdlblUsername.pack(side=tk.LEFT, pady=5, padx=10)

        pswdEntryUserpasswd = tk.Entry(center_pswd_left, show="*", width=35)
        pswdEntryUserpasswd.pack(side=tk.RIGHT, pady=5, padx=10)

        pswdlblUsername2 = tk.Label(center_pswd_right, text="Kontrola hesla:")
        pswdlblUsername2.pack(side=tk.LEFT, pady=5, padx=10)

        pswdEntryUserpasswd2 = tk.Entry(center_pswd_right, show="*", width=35)
        pswdEntryUserpasswd2.pack(side=tk.RIGHT, pady=5, padx=10)

        pswdbutton = ttk.Button(bottom_pswd, text="Poslat zálohu", command=lambda: self.zip_check_pswd(pswdEntryUserpasswd.get(), pswdEntryUserpasswd2.get()))
        pswdbutton.pack(pady=10, padx=10, ipadx=5)
        pswdbutton.bind('<Return>', lambda event: self.zip_check_pswd(pswdEntryUserpasswd.get(), pswdEntryUserpasswd2.get()))

    def zip_check_pswd(self, pswd1, pswd2):
        if pswd1 == pswd2:
            self.set_pswd.destroy()
            self.zip_database_and_send(pswd1)
        else:
            messagebox.showerror("Vytvořit zálohu",
                                 "Zvolená hesla se neshodují. Zálohu nebylo možné vytvořit.\n\nZadejte hesla znovu a stisknětě tlačítko 'Poslat zálohu'.")
            self.set_pswd.lift()

    def zip_database_and_send(self, pasword):
        zip_filename = str(datetime.date.today()) + "_db_zaloha.zip"
        zip_filepath = os.path.join(var.db_folder, zip_filename)

        # zip -P password -r F.zip F
        # 7z a -p Fdirectory.7z /path/to/F
        cmd = ['zip', '-P', pasword, '-r', zip_filepath, var.db]
        subprocess.call(cmd)

        outlook = client.Dispatch('Outlook.Application')
        message = outlook.CreateItem(0)
        message.Display()

        message.Subject = 'Záloha databáze ke dni {now}'.format(now=datetime.date.today().strftime("%d.%m.%Y"))

        pdf_file = pathlib.Path(zip_filepath)
        pdf_file_absolute = str(pdf_file.absolute())

        # attach the file
        message.Attachments.Add(pdf_file_absolute)

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
        text = "Strana č. %s" % page_num
        canvas.setFont("georgia", 10)

        # canvas.drawRightString(280*mm, 20*mm, text) 112
        canvas.drawRightString(200 * mm, 5 * mm, text)

    def print_summary_PDF(self, type, begining_date, ending_date, show_info=True):
        # Connect to database or create database
        conn = sqlite3.connect(var.db)

        # Create cursor
        c = conn.cursor()

        date = str(datetime.date.today())
        type_info = ""
        title = ""

        if type == 1:
            type_info = "prehled_lektori"
            title = "Přehled lektorů ke dni: {d}".format(d=date)
        elif type == 2:
            type_info = "prehled_studenti"
            title = "Přehled studentů ke dni: {d}".format(d=date)
        elif type == 3:
            type_info = "prehled_lekce"
            title = "Přehled lekcí za období {b} - {e} ke dni: {d}".format(e=ending_date, b=begining_date, d=date)
        elif type == 4:
            type_info = "prehled_platby"
            title = "Přehled plateb za období {b} - {e} ke dni: {d}".format(e=ending_date, b=begining_date, d=date)

        fileName = "{d}_{t}.pdf".format(d=date, t=type_info)

        elements = []

        pdfmetrics.registerFont(
            TTFont('georgia', 'Georgia.ttf')
        )

        titlestyle = ParagraphStyle(
            name='Title',
            fontName='georgia',
            fontSize=10,
            textColor="#fefffe"
        )

        normal = ParagraphStyle(
            name='left',
            fontName='georgia',
            fontSize=10,
        )

        partInfo = [[Paragraph(title, style=titlestyle)]]
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

        line3 = []
        sql = ""

        if type == 1:
            print("lector")
            sql = "SELECT * FROM teacher ORDER BY teacher_name"
            line3 = [Paragraph("Jméno", style=normal), Paragraph("Mail", style=normal), Paragraph("Telefonní číslo", style=normal),
                     Paragraph("Informace", style=normal)]
        elif type == 2:
            print("student")
            sql = "SELECT * FROM student ORDER BY student_name"
            line3 = [Paragraph("Jméno", style=normal), Paragraph("Mail", style=normal), Paragraph("Telefonní číslo", style=normal),
                     Paragraph("Úroveň", style=normal), Paragraph("Kurz", style=normal), Paragraph("Věková skupina", style=normal), Paragraph("Informace", style=normal)]
        elif type == 3:
            print("lekce")
            sql = "SELECT * FROM lesson WHERE lesson_date >= '" + str(begining_date) + "' AND lesson_date <= '" + str(ending_date) + "' ORDER BY lesson_date"
            print(sql)
            line3 = [Paragraph("Student", style=normal), Paragraph("Lektor", style=normal), Paragraph("Datum", style=normal),
                     Paragraph("Typ lekce", style=normal), Paragraph("Délka lekce", style=normal), Paragraph("Cena pro studenta (Kč)", style=normal), Paragraph("Výdělek lektora (Kč)", style=normal),
                     Paragraph("Informace", style=normal)]
        elif type == 4:
            print("platby")
            sql = "SELECT * FROM payment WHERE payment_date >= '" + str(begining_date) + "' AND payment_date <= '" + str(ending_date) + "' ORDER BY payment_date"
            line3 = [Paragraph("Student", style=normal), Paragraph("Částka (Kč)", style=normal), Paragraph("Datum", style=normal),
                     Paragraph("Typ platby", style=normal), Paragraph("Informace", style=normal)]

        data = [line3]

        c.execute(sql)
        records = c.fetchall()
        temp = []

        for row in records:
            print(row)
            if type == 1:
                temp = [row[1], row[2], row[3], row[4]]
            elif type == 2:
                temp = [row[1], row[2], row[3], row[4], row[5], row[6], row[7]]
            elif type == 3:
                temp = [row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]
            elif type == 4:
                temp = [row[1], row[2], row[3], row[4], row[5]]

            data.append(temp)

        table = Table(data, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), "#dfc8cb"),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'georgia'),
            ('LINEBELOW', (0, -1), (0, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(20, 20))

        try:
            doc = SimpleDocTemplate(fileName, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20, allowSplitting=1,
                                    title="Přehled", author="LENKA© corporation",
                                    showBoundary=0)
            doc.build(elements, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)
            messagebox.showinfo("Generování přehledu", "PDF soubor byl vygenerován.")
            self.choose_summary.destroy()
        except Exception as e:
            messagebox.showerror("Generování přehledu",
                                 "PDF soubor se nepodařilo vygenerovat. Zkuste to prosím znovu.\n\nRADA: Pravděpodobně máte PDF soubor otevřený a nepodařilo se ho přepsat. "
                                 "\n\nERROR: {e}".format(e=e))

        # Commit changes
        conn.commit()

        # disconnect to database
        conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    application = Login(root)
    root.mainloop()
