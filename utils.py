import sqlite3
import variables as var
import tkinter as tk
import tkinter.ttk as ttk


class Utils:
    def load_students(self):
        var.student_list = ()

        # Connect to database or create database
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()

        c.execute("SELECT DISTINCT student_name from student ORDER BY student_name")
        rows = c.fetchall()
        for row in rows:
            var.student_list=var.student_list + row

        # Commit changes
        conn.commit()
        # disconnect to database
        conn.close()

    def load_teachers(self):
        var.teacher_list = ()
        conn = sqlite3.connect(var.db)
        # Create cursor
        c = conn.cursor()
        c.execute("SELECT DISTINCT teacher_name from teacher ORDER BY teacher_name")
        rows = c.fetchall()
        for row in rows:
            var.teacher_list = var.teacher_list + row

        # Commit changes
        conn.commit()
        # disconnect to database
        conn.close()

    def get_school_year(self):
        year_now = var.year_date
        if var.month_date >= 9:
            current_school_year = "{yNow}-{yNext}".format(yNow=str(year_now), yNext=str(year_now+1))
        else:
            current_school_year = "{yBefore}-{yNow}".format(yNow=str(year_now), yBefore=str(year_now-1))

        return(current_school_year)






