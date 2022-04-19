import smtplib
# python -m pip install pywin32
import win32com.client as client
from email.message import EmailMessage
from tkinter import messagebox
import datetime
import pathlib
import variables as var
import os
import student as student


class Mail:
    """
        msg.set_content('This is a plain text email')

        msg.add_alternative(""\
        <!DOCTYPE html>
        <html>
            <body>
                <h1 style="color:SlateGray;">This is an HTML Email!</h1>
            </body>
        </html>
        "", subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

    messagebox.showinfo("Student", "Mail pro studenta {s} byl vygenerován a odeslán.".format(s=name))"""

    def send_student_mail(self, name, contact, mail_year_option):
        pdf_path = name + "_" + mail_year_option + ".pdf"
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.CreateItem(0)
        message.Display()

        message.To = contact
        now = datetime.date.today().strftime("%d.%m.%Y")

        message.Subject = 'Přehled lekcí a plateb ke dni {now}'.format(now=now)
        message.Body = 'Dobrý den,\nv příloze posíláme přehled plateb a lekcí.\n\nS přáním pěkného dne,\nTvoje Léňa'

        html_body = """
        <p>&nbsp;</p>
            <table border="0" width="100%" cellspacing="0" cellpadding="0">
                <tbody>
                    <tr>
                        <td style="padding: 10px 10 30px 0;">
                            <table style="border: 5px solid #cccccc; border-collapse: collapse; height: 500px;" border="0"
                                width="600" cellspacing="0" cellpadding="0" align="center">
                                <tbody>
                                    <tr>
                                        <td style="padding: 10px 10px 10px; color: #f5f1f0; font-size: 28px; font-weight: bold; "font-family: 'Georgia', sans-serif; width: 590px;"
                                            align="center" bgcolor="#f5f1f0"><img
                                                src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/368px-Google_2015_logo.svg.png" alt="" width="228"
                                                height="77" /></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px; width: 10px;" bgcolor="#ffffff">
                                            <table style="height: 100px;" border="0" width="600" cellspacing="0" cellpadding="0">
                                                <tbody>
                                                    <tr style="height: 10px;">
                                                        <td
                                                            style="color: #153643; font-family: Arial, sans-serif; font-size: 24px; width: 600px; height: 10px;">
                                                            <strong>Vyúčtování ke dni """ + now + """</strong></td>
                                                    </tr>
                                                    <tr style="height: 10px;">
                                                        <td
                                                            style="padding: 20px 0px 10px; color: #153643; "font-family: 'Georgia', sans-serif; font-size: 16px; line-height: 20px; width: 535.8px; height: 20px;">
                                                            <p>Dobrý den,<br>v příloze posíláme přehled plateb a lekcí. V případě
                                                                nedoplatku prosíme o zaplacení částky uvedené v příloze na účet
                                                                číslo: xxxx/0987654321<br><br>S přáním pěkného dne,<br>Tvoje Léňa</p>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px; width: 600px;" bgcolor="#a10d2d">
                                            <table border="0" width="100%" cellspacing="0" cellpadding="0">
                                                <tbody>
                                                    <tr>
                                                        <td style="color: #ffffff; "font-family: 'Georgia', sans-serif; font-size: 14px; width: 33%;" 
                                                        align="left"><span style="color: #ffffff;">""" + var.company_name + """</span></td>
                                                        <td style="color: #ffffff; "font-family: 'Georgia', sans-serif; font-size: 14px; width: 33%;" 
                                                        align="center"><span style="color: #ffffff;">""" + var.company_web + """</span></td>
                                                        <td style="color: #ffffff; "font-family: 'Georgia', sans-serif; font-size: 14px; width: 33%;" 
                                                        align="right"><span style="color: #ffffff;">""" + var.company_phone + """</span></td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
            <p>&nbsp;</p>"""

        html_body2 = """
            <div>
                <h1 style="font-family: 'Georgia'; font-size: 20; font-weight: bold; color: #9c1513;">
                    Měsíční přehled plateb a lekcí 
                </h1>
                <span style="font-family: 'Georgia'; font-size: 12; color: #423838;">
                    Dobrý den,<br>
                    v příloze posíláme přehled lekcí a plateb.<br><br>
                    S přáním pěkného dne,<br>
                    Tvoje Léňa
                </span>
            </div>"""

        message.HTMLBody = html_body

        pdf_file = pathlib.Path(pdf_path)
        pdf_file_absolute = str(pdf_file.absolute())
        print(pdf_file_absolute)

        # attach the file
        message.Attachments.Add(pdf_file_absolute)

    def send_lector_mail(self, name, contact, month, year):
        pdf_path = name + "_" + month + "_" + year + ".pdf"
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.CreateItem(0)
        message.Display()

        message.To = contact

        message.Subject = 'Přehled odučených lekcí ke dni {now}'.format(now=datetime.date.today().strftime("%d.%m.%Y"))
        message.Body = 'Dobrý den,\nv příloze posíláme přehled odučených lekcí.\n\nS přáním pěkného dne,\nTvoje Léňa'

        pdf_file = pathlib.Path(pdf_path)
        pdf_file_absolute = str(pdf_file.absolute())
        print(pdf_file_absolute)

        # attach the file
        message.Attachments.Add(pdf_file_absolute)
