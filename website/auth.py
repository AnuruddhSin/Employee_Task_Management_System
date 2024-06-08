from flask import Blueprint,Flask,render_template, request,redirect,session,flash
import mysql.connector
import mysql


from .employee_registration_routes import Employee_reg_Auth_Routes
from .student_registration_routes import Student_reg_Auth_Routes
from .client_register_routes import Client_reg_Auth_Routes
from .gmail_otp_auth import GMAIL_OTP_SYSTEM
from .mobile_otp_system import MOBILE_OTP_SYSTEM
from .department_management_admin import DEPARTMENT_MANAGEMENT_ADMIN_AUTH
from .employee_management_admin import EMPLOYEE_MANAGEMENT_ADMIN_AUTH
from .task_management_admin import TASK_MANAGEMENT_ADMIN_AUTH
from .employee_assign_task import TASK_MANAGEMENT_EMPLOYEE_AUTH
from .task_action_management import TASK_ACT_MANAGEMENT

auth=Blueprint('auth',__name__)

# Client registration database calling logic here
register_client_auth_routes = Client_reg_Auth_Routes(auth)

# Employee registration database calling logic here
register_employee_auth_routes = Employee_reg_Auth_Routes(auth)

# Student registration database Calling logic here
register_student_auth_routes = Student_reg_Auth_Routes(auth)




# Mobile OTP SYSTEM CALL HERE
mobile_otp = MOBILE_OTP_SYSTEM(auth)

# Gmail OTP SYSTEM CALL HERE
gmail_otp = GMAIL_OTP_SYSTEM(auth)


@auth.route('/Login Client')
def login_client():
    return render_template("client_login.html")

#MySQL configurations
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "fces_dash"
}

def connect_to_db():
    return mysql.connector.connect(**db_config)

@auth.route('/loginemp', methods=['POST', 'GET'])
def login_employee():
    if request.method == 'POST':
        employeeId = request.form['employeeId']
        password = request.form['password']

        mydb = connect_to_db()
        mycursor = mydb.cursor()

        # mycursor.execute(
        #     "SELECT * FROM add_employee WHERE employeeId=%s AND password=%s" ,
        #     (employeeId, password)
        # )
        mycursor.execute(
            "SELECT employeeId, employeeName FROM employee_data WHERE employeeId=%s AND password=%s",
            (employeeId, password)
        )
        employee_data = mycursor.fetchone()
        r = mycursor.fetchall()
        count = mycursor.rowcount

        # r = mycursor.fetchall()
        # count = mycursor.rowcount

        if employee_data:
            session['employeeId'] = employee_data[0]
            session['employeeName'] = employee_data[1]
            session['is_employee'] = True
            if session['is_employee']:
                return emp_dashboard()
            # session['employeeId'] = employeeId
        elif count > 1:
            return 'More than one user found'
        else:
            flash("Invalid Employee ID or password", "error")

    return render_template("employee_login.html")

@auth.route('/emp_dashboard')
def emp_dashboard():
    if 'employeeId' in session:
        employeeId = session['employeeId']
        mydb = connect_to_db()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM task WHERE employeeId=%s AND (creator_type = 'is_employee'  )", (employeeId,))
        tasks = mycursor.fetchall()



        mycursor.close()
        mydb.close()

        return render_template("Employee_dashboard/assign_by_me.html", tasks=tasks)
    else:
        return redirect('/loginemp')


@auth.route('/logout')
def logout():
    session.pop('employeeId', None)
    return redirect('/Employee')

@auth.route('/assign')
def emp_assign():
    return render_template("Employee_dashboard/assign_to_me.html")


# ======= EMPLOYEE CALLING FUNCTION HERE ===========#


emp_assingn_task_auth = TASK_MANAGEMENT_EMPLOYEE_AUTH(auth)

task_action_manage= TASK_ACT_MANAGEMENT(auth)


# ========ADMIN DASHBOARD============== #

# =========login admin=========

@auth.route('/Admin', methods=['POST', 'GET'])
def admin_Login():
    mydb = mysql.connector.Connect(
        host='localhost',
        user='root',
        password='',
        database='fces_dash'
    )
    mycursor = mydb.cursor()
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        password = request.form['password']

        mydb = connect_to_db()
        mycursor = mydb.cursor()

        mycursor.execute(
            "SELECT admin_id FROM admin_dash WHERE admin_id=%s AND password=%s",
            (admin_id, password)
        )
        admin_data = mycursor.fetchone()
        count = mycursor.rowcount

        if admin_data:
            session['admin_id'] = admin_data[0]
            session['is_admin'] = True
            if session['is_admin']:
                return admin_dashboard()

        else:
            flash("Invalid admin ID or password", "error")
    mydb.commit()
    mycursor.close()

    return render_template("admin_dashboard/admin_login.html")

@auth.route('/Admin Dashboard')
def admin_dashboard():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='fces_dash'
    )
    mycursor = mydb.cursor()

    # Define default values
    num_departments = 0
    num_employees = 0
    num_tasks = 0
    num_projects = 0
    num_reg_employee=0

    try:
        # Fetch counts from respective tables
        mycursor.execute("SELECT COUNT(*) FROM team")
        num_departments = mycursor.fetchone()[0]

        mycursor.execute("SELECT COUNT(*) FROM employee_data WHERE updated_by='admin'")
        num_employees = mycursor.fetchone()[0]

        mycursor.execute("SELECT COUNT(*) FROM task WHERE creator_type = 'admin_id' ")
        num_tasks = mycursor.fetchone()[0]

        mycursor.execute("SELECT COUNT(*) FROM employee_data WHERE updated_by != 'admin'")
        num_reg_employee=mycursor.fetchone()[0]


    except Exception as e:
        print("Error:", str(e))

    finally:
        mycursor.close()

    return render_template("admin_dashboard/dashboard.html",
                           num_departments=num_departments,
                           num_employees=num_employees,
                           num_tasks=num_tasks,
                           num_projects=num_projects,num_reg_employee=num_reg_employee)

#=================== ADMIN DASHBOARD CALLING FUNCTION  ===============================#

department_management_route= DEPARTMENT_MANAGEMENT_ADMIN_AUTH(auth)

emplyees_management_auth= EMPLOYEE_MANAGEMENT_ADMIN_AUTH(auth)

task_management_auth=TASK_MANAGEMENT_ADMIN_AUTH(auth)

@auth.route('/joinsinger')
def join_singer():
    return render_template("singer.html")
@auth.route('/joinmusician')
def join_musician():
    return render_template("musian.html")