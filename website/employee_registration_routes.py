from flask import render_template, request,flash
import smtplib
import ssl
from email.message import EmailMessage
import mysql.connector

class Employee_reg_Auth_Routes:
    def __init__(self, app):
        self.app = app
        self.route()



    def route(self):
        @self.app.route('/Register Employee', methods=['POST', 'GET'])

        def register_employee():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            if request.method == 'POST':
                register = request.form
                f_name = register['f_name']
                m_name = register['m_name']
                l_name = register['l_name']
                dob = register['dob']
                age = register['age']
                gender = register['gender']
                email = register['email']
                contact = register['contact']
                address = register['address']
                city = register['city']
                state = register['state']
                district = register['district']
                pin_code = register['pin_code']
                acc_holder_name = register['acc_holder_name']
                ifsc = register['ifsc']
                acc_number = register['acc_number']
                re_acc_number = register['re_acc_number']
                aadhar_no = register['aadhar_no']
                alt_number = register['alt_number']
                img=request.files['img']
                img.save('fofs_2/static/uploaded/' + img.filename)
                img_data = img.read()

                img_filename = img.filename
                sign=request.files['sign']
                sign.save('fofs_2/static/uploaded/' + sign.filename)
                sign_data = sign.read()
                sign_filename = sign.filename
                aadhar= request.files['aadhar']
                aadhar.save('fofs_2/static/uploaded/' + aadhar.filename)
                aadhar_data = aadhar.read()
                aadhar_filename = aadhar.filename




                mycursor.execute(
                    "INSERT INTO `employee_data` (`f_name`, `m_name`, `l_name`, `dob`, `age`, `gender`, `email`, `contact`, `address`, `city`, `state`, `district`, `pin_code`, `acc_holder_name`, `ifsc`, `acc_number`, `re_acc_number`, `aadhar_no`, `alt_number`,`img`,`sign`,`aadhar`)  VALUES (%s,%s,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (f_name, m_name, l_name, dob, age, gender, email, contact, address, city, state, district, pin_code,
                     acc_holder_name, ifsc, acc_number, re_acc_number, aadhar_no, alt_number,img_filename,sign_filename,aadhar_filename))
                mydb.commit()
                mycursor.close()


                email_sender =""
                email_sender_pas = ""

                email_receiver = ""

                subject = "Registration Employee info"

                body = (f"Full name :{f_name}{m_name} {l_name}\n"
                        f"Date of Birth :{dob}\n"
                        f"Age : {age}\n"
                        f"Gender : {gender}\n"
                        f"Email : {email}\n"
                        f"Contact number : {contact}\n"
                        f"Address : {address}\n"
                        f"City : {city}\n"
                        f"State : {state}\n"
                        f"District : {district}\n"
                        f"Pin code : {pin_code}\n"
                        f"Account holder name : {acc_holder_name}\n"
                        f"IFSC code : {ifsc}\n"
                        f"Account number : {acc_number}\n"
                        f"Aadhar number : {aadhar_no} \n"
                        f"Alternate number : {alt_number} \n"
                        )


                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['subject'] = subject
                em.set_content(body)

                context = ssl.create_default_context()
                # Attach the image to the email
                em.add_attachment(img_data, maintype='image', subtype='jpeg', filename=img_filename)
                em.add_attachment(sign_data, maintype='image', subtype='jpeg', filename=sign_filename)
                em.add_attachment(aadhar_data, maintype='image', subtype='jpeg', filename=aadhar_filename)

                try:
                    context = ssl.create_default_context()

                    # Attach image files to email
                    with open('fofs_2/static/uploaded/' + img.filename, 'rb') as img_file:
                        em.add_attachment(img_file.read(), maintype='image', subtype='png', filename=img.filename)

                    with open('fofs_2/static/uploaded/' + sign.filename, 'rb') as sign_file:
                        em.add_attachment(sign_file.read(), maintype='image', subtype='png', filename=sign.filename)

                    with open('fofs_2/static/uploaded/' + aadhar.filename, 'rb') as aadhar_file:
                        em.add_attachment(aadhar_file.read(), maintype='image', subtype='png',
                                          filename=aadhar.filename)

                    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                        smtp.login(email_sender, email_sender_pas)
                        smtp.sendmail(email_sender, email_receiver, em.as_string())
                        flash("You Have Successfully Registered , I will contact soon..", "success")
                except Exception as e:
                    return f"Error sending email: {e}"
                finally:
                    pass

                    # flash("You Have Successfully Registered , I will contact soon..", "error")
            return render_template("registration_employee.html")
