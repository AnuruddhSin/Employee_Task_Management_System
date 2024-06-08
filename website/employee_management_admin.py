from flask import render_template,request,redirect
import mysql.connector
import MySQLdb.cursors
import os
class EMPLOYEE_MANAGEMENT_ADMIN_AUTH:
    def __init__(self, app):
        self.app = app
        self.route()

    def get_last_emp_numeric(self, prefix):
        try:
            with open(f'Emp_last_{prefix}_task_id.txt', 'r') as file:
                last_task_id = int(file.read().strip())
        except FileNotFoundError:
            last_task_id = 0  # Start from 0 if the file doesn't exist
        return last_task_id

    def generate_unique_employeeId(self):
        last_task_id = self.get_last_emp_numeric('FCES')
        new_task_id_numeric = last_task_id + 1
        new_numeric_part = str(new_task_id_numeric).zfill(7)
        new_task_id = "FCES" + new_numeric_part
        self.update_last_emp_numeric('FCES', new_task_id_numeric)
        return new_task_id

    def update_last_emp_numeric(self, prefix, new_value):
        with open(f'Emp_last_{prefix}_task_id.txt', 'w') as file:
            file.write(str(new_value))

    def update_emp_add_emp_id(self):
        assigned_by = "admin"
        return assigned_by

    def route(self):
        @self.app.route('/Admin add emp', methods=['POST', 'GET'])
        def add_employ_admin():
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
                img = request.files['img']
                img.save('fofs_2/static/uploaded/' + img.filename)
                img_filename = img.filename
                sign = request.files['sign']
                sign.save('fofs_2/static/uploaded/' + sign.filename)
                sign_filename = sign.filename
                aadhar = request.files['aadhar']
                aadhar.save('fofs_2/static/uploaded/' + aadhar.filename)
                aadhar_filename = aadhar.filename
                password = register['password']
                re_password = register['re_password']
                department = register['department']
                updated_by = self.update_emp_add_emp_id()
                employeeId = self.generate_unique_employeeId()
                employeeName = f_name + ' ' + l_name

                mycursor.execute(
                    "INSERT INTO `employee_data` (`f_name`, `m_name`, `l_name`, `dob`, `age`, `gender`,`email`, `contact`,"
                    " `address`, `city`, `state`, `district`, `pin_code`, `acc_holder_name`,"
                    " `ifsc`, `acc_number`, `re_acc_number`, `aadhar_no`, `alt_number`,`img`,`sign`,`aadhar`,`password`,`re_password`,"
                    "`department`,`updated_by`,`employeeId`,`employeeName`)"
                    "  VALUES (%s,%s,%s,%s,%s,%s,%s, %s, %s,%s,%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (f_name, m_name, l_name, dob, age, gender, email, contact, address, city, state, district, pin_code,
                     acc_holder_name, ifsc, acc_number, re_acc_number, aadhar_no, alt_number, img_filename,
                     sign_filename, aadhar_filename, password, re_password, department, updated_by, employeeId,employeeName))

                mydb.commit()
                mycursor.close()
                return redirect("/Admin mang emp")

            return render_template("admin_dashboard/add_employee.html")



        @self.app.route('/admin view employee', methods=['POST', 'GET'])
        def admin_view_emp():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            contact = request.args.get('contact')
            print("Received department name:", contact)

            # Fetch the image filename from the database based on 'contact'
            cursor = mydb.cursor()
            cursor.execute("SELECT img, sign, aadhar  FROM employee_data WHERE updated_by='admin' AND  contact = %s", (contact,))
            result = cursor.fetchone()
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("SELECT * FROM employee_data WHERE contact = %s", (contact,))
            data_f = mycursor.fetchone()

            if data_f:
                print("Retrieved data:", data_f)

            if result:
                img_filename = [f'fofs_2/static/uploaded/{result[0]}', f'fofs_2/static/uploaded/{result[1]}',
                                f'fofs_2/static/uploaded/{result[2]}']
                img_urls = []
                for img_filename in img_filename:
                    if os.path.isfile(img_filename):
                        img_urls.append('/static/uploaded/' + os.path.basename(img_filename))
                    else:
                        img_urls.append(None)

                view_profile_requests = {
                    'img_url': img_urls[0],
                    'sign_url': img_urls[1],
                    'aadhar_url': img_urls[2],
                    # Add other data you want to pass to the template
                }

                return render_template("admin_dashboard/view_employee.html",view_profile_requests=view_profile_requests,data_f=data_f)

        @self.app.route('/Admin mang emp', methods=['POST', 'GET'])
        def mang_employ_admin():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM employee_data WHERE updated_by='admin' ")
            data = mycursor.fetchall()
            mycursor.close()
            return render_template("admin_dashboard/manage_employee.html", manage_profile_request=data)

        @self.app.route("manage_profile_request")
        def manage_profile_request():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM employee_data WHERE updated_by != 'admin' ")
            manage_profile_request = mycursor.fetchall()
            mycursor.close()
            return render_template("admin_dashboard/manage_profile_request.html", manage_profile_request=manage_profile_request)

        @self.app.route('/view_profile_requests')
        def view_profile_requests():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            if request.method == 'GET':
                contact = request.args.get('contact')
                print("Received department name:", contact)

                # Fetch the image filename from the database based on 'contact'
                cursor = mydb.cursor()
                cursor.execute("SELECT img, sign, aadhar  FROM employee_data WHERE contact = %s", (contact,))
                result = cursor.fetchone()
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM employee_data WHERE contact = %s", (contact,))
                data_f = mycursor.fetchone()

                if data_f:
                    print("Retrieved data:", data_f)



                if result:
                    img_filename = [f'fofs_2/static/uploaded/{result[0]}', f'fofs_2/static/uploaded/{result[1]}',
                                     f'fofs_2/static/uploaded/{result[2]}']
                    img_urls = []
                    for img_filename in img_filename:
                        if os.path.isfile(img_filename):
                            img_urls.append('/static/uploaded/' + os.path.basename(img_filename))
                        else:
                            img_urls.append(None)

                    view_profile_requests = {
                        'img_url': img_urls[0],
                        'sign_url':img_urls[1],
                        'aadhar_url':img_urls[2],
                        # Add other data you want to pass to the template
                    }
                    return render_template("admin_dashboard/view_profile_requests.html",
                                           view_profile_requests=view_profile_requests,data_f=data_f)

                # Handle the case when the image does not exist or when there is an error
            return "Image not found", 404


        @self.app.route('/admin_add_emp_by_profile', methods=['POST', 'GET'])
        def admin_add_emp_by_profile():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            if request.method == 'GET':
                contact = request.args.get('contact')
                print("Received department name:", contact)


                # Fetch the image filename from the database based on 'contact'
                cursor = mydb.cursor()
                cursor.execute("SELECT img, sign, aadhar  FROM employee_data WHERE contact = %s", (contact,))
                result = cursor.fetchone()
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM employee_data WHERE contact = %s", (contact,))
                data = mycursor.fetchone()
                if data:
                    print("Retrieved data:", data)
                if result:
                        img_filename = [f'fofs_2/static/uploaded/{result[0]}', f'fofs_2/static/uploaded/{result[1]}',
                                        f'fofs_2/static/uploaded/{result[2]}']
                        img_urls = []
                        for img_filename in img_filename:
                            if os.path.isfile(img_filename):
                                img_urls.append('/static/uploaded/' + os.path.basename(img_filename))
                            else:
                                img_urls.append(None)

                        view_profile_requests = {
                            'img_url': img_urls[0],
                            'sign_url': img_urls[1],
                            'aadhar_url': img_urls[2],

                        }


                        return render_template("admin_dashboard/add_employee_by_profile.html", data=data,
                                               view_profile_requests=view_profile_requests)
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
                password = register['password']
                re_password = register['re_password']
                department = register['department']
                updated_by = self.update_emp_add_emp_id()
                employeeId = self.generate_unique_employeeId()
                employeeName=register['employeeName']

                mycursor.execute(
                    "UPDATE `employee_data` SET f_name=%s, m_name=%s, l_name=%s,"
                    " dob=%s, age=%s, gender=%s, email=%s, address=%s,"
                    " city=%s, state=%s, district=%s, pin_code=%s, acc_holder_name=%s,"
                    " ifsc=%s, acc_number=%s, re_acc_number=%s, aadhar_no=%s,"
                    " alt_number=%s, password=%s, re_password=%s, department=%s ,updated_by=%s,employeeId=%s,employeeName=%s WHERE contact=%s",
                    (f_name, m_name, l_name, dob, age, gender, email, address, city, state,
                     district, pin_code, acc_holder_name, ifsc, acc_number, re_acc_number,
                     aadhar_no, alt_number, password, re_password, department,updated_by,employeeId,employeeName, contact))

                mydb.commit()
                mycursor.close()
                if updated_by == 'admin':
                    return redirect("/Admin mang emp")
            mycursor.close()
            return redirect("/Admin mang emp")

