import os

version = "Beta version 0.1"
company = "Designed by Lenka"
icon = r"C:\Users\42073\Desktop\DP\logo_blue.ico"

db_folder = '%s\\CompDB\\' % os.environ['APPDATA']
db = '%scompanyDB.db' % db_folder

company_name = "Company Name"
company_web = "www.companyWeb.cz"
company_phone = "123 456 789"
company_address = "Company Address"
company_city = "Company Name"

# colors
white = "#FBF3F2"
light = "#1C768F"
dark = "#032539"
orange = "#FA991C"

# was size of window resized?
resized = False

# create lists
student_list = ()
teacher_list = ()

# knowledge level options
knowledge_level_option = [
    "Beginner (A1)",
    "Elementary (A2)",
    "Intermediate (B1)",
    "Upper-Intermediate (B2)",
    "Advanced (C1)",
    "Proficiency/Mastery (C2)",
    "Kids: Starters (Pre A1)",
    "Kids: Movers (A1)",
    "Kids: Flayers (A2)"
]

# age group options
age_group_options = [
    "Dítě",
    "Dospělý",
    "Senior",
]

# payment options
payment_options = [
    "Převodem",
    "Hotově",
    "Poukázkou",
    "Fakturou",
    "Zůstatek z předchozího roku"
]

# možnosti délky lekcí
lesson_type_options = ["individuál/45", "individuál/60", "individuál/90", "dvojice/45", "dvojice/60", "dvojice/90", "trojice/45", "trojice/60", "trojice/90",
                       "skupina/45", "skupina/60", "skupina/90", "CALL"]

year = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
school_year = ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025", "2025-2026", "2027-2028", "2028-2029", "2029-2030"]

month = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen", "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec", "vše"]

week_days = ["pondělí", "úterý", "středa", "čtvrtek", "pátek"]
hour = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
minutes = ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]

# ++++++++++++++ date ++++++++++++++
from datetime import *

now = datetime.now()
month_date = now.month
month_index = now.month-1
month_name = month[now.month-1]
year_date = now.year

"""print(month_date)
print(month_index)
print(month_name)
print(year_date)
"""

# +++++++++++++++++
clicked_tab=0