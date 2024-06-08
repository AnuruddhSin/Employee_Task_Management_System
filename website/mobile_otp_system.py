from flask import render_template, request,jsonify
import smtplib
import random
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class MOBILE_OTP_SYSTEM:
    def __init__(self, app):
        self.app = app
        self.route()

    def route(self):
        @self.app.route('/send-otp', methods=['POST', 'GET'])
        def send_otp_mobile():
            mobile_number = request.json['contactNumber']
            api_key = ""
            template_otp = random.randint(100000, 999999)
            template_id = str(template_otp)
            url = f"https://2factor.in/API/V1/{api_key}/SMS/{mobile_number}/{template_id}"

            response = requests.get(url)
            if response.status_code == 200:
                session_id = response.json().get('Details')
                return jsonify({'sessionID': session_id, 'otp': template_otp})
            else:
                return jsonify({'error': 'Failed to send OTP'})

        @self.app.route('/verify-otp', methods=['POST', 'GET'])
        def verify_otp_mobile():
            session_id = request.json['sessionID']
            entered_otp = request.json['enteredOTP']
            api_key = ""
            url = f"{api_key}/{session_id}/{entered_otp}"

            response = requests.get(url)
            if response.status_code == 200:
                return jsonify({'result': True})
            else:
                return jsonify({'result': False})