from flask import render_template, request,jsonify
import smtplib
import random
import os
from dotenv import load_dotenv

load_dotenv()


class GMAIL_OTP_SYSTEM:
    def __init__(self, app):
        self.app = app
        self.route()

    def route(self):
        sender_email = os.getenv("SENDER_Email_ID")
        sender_password = os.getenv("Password")
        @self.app.route('/send-otp-email', methods=['POST', 'GET'])
        def send_otp_email():
            email = request.json["email"]

            otp1 = random.randrange(100000, 1000000)

            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, f"Subject: OTP for FoFs\n\n"
                                                     f"Dear User,\n"
                                                     f"Your OTP for FoFs is {otp1}.\n"
                                                     f"This is valid for 15 minutes.\n"
                                                     f"Please do not share it with anyone.")
                server.quit()

                response = {"generated_otp": otp1}
                return jsonify(response), 200
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
                return jsonify({}), 500

        @self.app.route('/verify-otp-email', methods=['POST', 'GET'])
        def verify_otp_email():
            user_otp = int(request.form["otp1"])
            generated_otp = int(request.form["generated_otp"])

            if user_otp == generated_otp:
                return "Access Granted"
            else:
                return "Wrong OTP"