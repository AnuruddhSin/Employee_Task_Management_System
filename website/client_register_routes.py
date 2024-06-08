from flask import render_template, request
import smtplib
import ssl
from email.message import EmailMessage
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class Client_reg_Auth_Routes:
    def __init__(self, app):
        self.app = app
        self.route()

    def route(self):
        @self.app.route('/Register Client', methods=['POST', 'GET'])
        def register_client():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            if request.method == 'POST':
                registerc = request.form
                full_name = registerc['full_name']
                dob = registerc['dob']
                age = registerc['age']
                gender = registerc['gender']
                email = registerc['email']
                mobileNumber = registerc['mobileNumber']
                address = registerc['address']
                city = registerc['city']
                state = registerc['state']
                district = registerc['district']
                pin_code = registerc['pin_code']
                mycursor.execute(
                    "INSERT INTO register_client(`full_name`, `dob`, `age`, `gender`, `email`, `mobileNumber`, `address`, `city`, `state`, `district`, `pin_code`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (full_name, dob, age, gender, email, mobileNumber, address, city, state, district, pin_code))
                mydb.commit()
                mycursor.close()

                email_sender = os.getenv("SENDER_Email_ID")
                email_sender_pas = os.getenv("Password")

                email_receiver = os.getenv("RECEIVER_Email_ID")

                subject = "Registration Employee info"

                body = (f"Full name :{full_name}\n"
                        f"Date of Birth :{dob}\n"
                        f"Age : {age}\n"
                        f"Gender : {gender}\n"
                        f"Email : {email}\n"
                        f"Contact number : {mobileNumber}\n"
                        f"Address : {address}\n"
                        f"City : {city}\n"
                        f"State : {state}\n"
                        f"District : {district}\n"
                        f"Pin code : {pin_code}\n")

                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['subject'] = subject
                em.set_content(body)

                context = ssl.create_default_context()

                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_sender_pas)
                    smtp.sendmail(email_sender, email_receiver, em.as_string())

                return "Mail Client Registration send successfully"

                return render_template('client_login.html')

            return render_template("registration_client.html")