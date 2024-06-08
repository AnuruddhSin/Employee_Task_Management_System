from flask import render_template,request
import mysql.connector
import MySQLdb.cursors

from mysql.connector.errors import OperationalError
generated_uuids = set()
from flask import session, redirect

class TASK_MANAGEMENT_EMPLOYEE_AUTH:
    def __init__(self, app):
        self.app = app
        self.route()
        # Create a database connection
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='fces_dash'
        )
        self.mycursor = self.mydb.cursor()

    def get_last_task_id_numeric(self, prefix):
        try:
            with open(f'LNNEW_last_{prefix}_task_id.txt', 'r') as file:
                last_task_id = int(file.read().strip())
        except FileNotFoundError:
            last_task_id = 0
        return last_task_id

    def generate_unique_task_id(self):
        last_task_id = self.get_last_task_id_numeric('ET')
        new_task_id_numeric = last_task_id + 1
        new_numeric_part = str(new_task_id_numeric).zfill(7)
        new_task_id = "ET" + new_numeric_part
        self.update_last_task_id_numeric('ET', new_task_id_numeric)
        return new_task_id

    def update_last_task_id_numeric(self, prefix, new_value):
        with open(f'LNNEW_last_{prefix}_task_id.txt', 'w') as file:
            file.write(str(new_value))

    def execute_query_with_retry(self, query, values=None, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                self.mycursor.execute(query, values)
                self.mydb.commit()
                return
            except OperationalError as e:
                print(f"Lost connection to MySQL server. Retrying... ({retries + 1}/{max_retries})")
                retries += 1
                self.mydb.reconnect()

        print("Query execution failed after multiple retries.")

    def route(self):
            @self.app.route('/add task', methods=['POST', 'GET'])
            def emp_add():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'

                )
                is_employee=True
                mycursor = mydb.cursor()
                if request.method == 'POST':
                    add_task = request.form
                    taskName = add_task['taskName']
                    employeeIds = add_task.getlist('employeeId[]')
                    priority=add_task['priority']
                    deadline=add_task['deadline']
                    status=add_task['status']
                    description=add_task['description']
                    real_time_sh=add_task['real_time_sh']
                    task_id = self.generate_unique_task_id()
                    creator_type = 'employeeId' if is_employee else 'admin_id'

                    assigned_by = session.get('employeeId')
                    task_query = "INSERT INTO `task` (`task_id`, `taskName`,`employeeId`, `priority`, `deadline`, `status`, `description`, `real_time_sh`, `creator_type`, `assigned_by`,`assigned_to`) VALUES (%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s)"
                    task_values = (
                        task_id, taskName, ','.join(employeeIds), priority, deadline, status, description, real_time_sh,
                        creator_type, assigned_by,','.join(employeeIds))
                    self.mycursor.execute(task_query, task_values)
                    self.mydb.commit()
                    em_task_query = "INSERT INTO `em_task` (`task_id`, `employeeId`) VALUES (%s, %s)"
                    em_task_values = [(task_id, employee_id) for employee_id in employeeIds]
                    self.mycursor.executemany(em_task_query, em_task_values)
                    self.mydb.commit()
                    mycursor.close()
                    if status == 'Review':
                        return redirect('/new_task_by_me')
                    elif status == 'In-progress':
                        return redirect('/in_progess_task_by_me')
                    elif status == 'pending':
                        return redirect('/pending_task_by_me')
                    elif status == 'Completed':
                        return redirect('/completed_task_by_me')


                mycursor = mydb.cursor()
                mycursor.execute("SELECT employeeId, employeeName FROM employee_data WHERE updated_by='admin' ")
                employee_data = mycursor.fetchall()
                employees = [{"id": row[0], "name": row[1]} for row in employee_data]
                mycursor.close()
                return render_template("Employee_dashboard/add_tasks_emp.html", employees=employees)


            @self.app.route('/new_task_to_me', methods=['GET'])
            def new_task_assigned_to_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()
                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE task.status = 'Review' AND em_task.employeeId = %s AND  task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE task.status = 'Review' AND em_task.employeeId = %s"
                        mycursor.execute(query, (employee_id,))

                    new_task_to_me = mycursor.fetchall()
                    mycursor.close()
                    return render_template("Employee_dashboard/new_task_to_me.html",
                                           new_task_to_me=new_task_to_me)

            @self.app.route('/new_task_by_me', methods=['GET'])
            def new_task_assigned_by_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()
                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT * FROM task WHERE status = 'Review' AND assigned_by = %s AND  task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:

                        # Retrieve tasks assigned by the logged-in employee
                        query = "SELECT * FROM task WHERE status = 'Review' AND assigned_by = %s  "
                        mycursor.execute(query, (employee_id,))

                    new_task_by_me = mycursor.fetchall()
                    mycursor.close()
                    return render_template("Employee_dashboard/new_task_by_me.html",
                                           new_task_by_me=new_task_by_me)

            @self.app.route('/in_progess_task_by_me', methods=['GET'])
            def in_progess_task_by_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()
                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT * FROM task WHERE status = 'In-progress' AND assigned_by = %s AND  task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:
                        query = "SELECT * FROM task WHERE status = 'In-progress' AND assigned_by = %s"
                        mycursor.execute(query, (employee_id,))

                    in_progess_task_by_me = mycursor.fetchall()
                    mycursor.close()
                    return render_template("Employee_dashboard/in_progess_task_by_me.html",
                                           in_progess_task_by_me=in_progess_task_by_me)

            @self.app.route('/in_progess_task_to_me', methods=['GET'])
            def in_progess_task_to_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()
                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE task.status = 'In-progress' AND em_task.employeeId = %s AND  task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:
                        # Retrieve tasks assigned to the logged-in employee
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE task.status = 'In-progress' AND em_task.employeeId = %s"
                        mycursor.execute(query, (employee_id,))

                    in_progess_task_to_me = mycursor.fetchall()
                    mycursor.close()
                    return render_template("Employee_dashboard/in_progess_task_to_me.html",
                                           in_progess_task_to_me=in_progess_task_to_me)

            @self.app.route('/pending_task_by_me', methods=['GET'])
            def pending_task_by_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()
                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT * FROM task WHERE status = 'pending' AND assigned_by = %s AND  task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:
                        query = "SELECT * FROM task WHERE status = 'pending' AND assigned_by = %s"
                        mycursor.execute(query, (employee_id,))

                    pending_task_by_me = mycursor.fetchall()
                    mycursor.close()
                    return render_template("Employee_dashboard/pending_task_by_me.html",
                                           pending_task_by_me=pending_task_by_me)

            @self.app.route('/pending_task_to_me', methods=['POST', 'GET'])
            def pending_task_to_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()
                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE task.status = 'pending' AND em_task.employeeId = %s AND  task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE task.status = 'pending' AND em_task.employeeId = %s"

                        mycursor.execute(query, (employee_id,))

                    pending_task_to_me = mycursor.fetchall()
                    name_query = "SELECT employeeName FROM employee_data WHERE employeeId = %s "
                    mycursor.execute(name_query, (employee_id,))
                    employee_name = mycursor.fetchone()[0]

                    mycursor.close()
                    return render_template("Employee_dashboard/pending_task_to_me.html", pending_task_to_me=pending_task_to_me,
                                           employee_name=employee_name)

            @self.app.route('/completed_task_to_me', methods=['GET'])
            def completed_task_to_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()
                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE task.status = 'Completed' AND em_task.employeeId = %s AND  task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE task.status = 'Completed' AND em_task.employeeId = %s"
                        mycursor.execute(query, (employee_id,))

                    completed_task_to_me = mycursor.fetchall()
                    name_query = "SELECT employeeName FROM employee_data WHERE employeeId = %s "
                    mycursor.execute(name_query, (employee_id,))
                    employee_name = mycursor.fetchone()[0]
                    mycursor.close()

                    return render_template("Employee_dashboard/completed_task_to_me.html", completed_task_to_me=completed_task_to_me,
                                           employee_name=employee_name)

            @self.app.route('/completed_task_by_me', methods=['GET'])
            def completed_task_by_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()
                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT * FROM task WHERE status = 'Completed' AND assigned_by = %s AND  task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:
                        query = "SELECT * FROM task WHERE status = 'Completed' AND assigned_by = %s"
                        mycursor.execute(query, (employee_id,))

                    completed_task_by_me = mycursor.fetchall()
                    mycursor.close()
                    return render_template("Employee_dashboard/completed_task_by_me.html",
                                           completed_task_by_me=completed_task_by_me)

            @self.app.route('/emp_all_task_by_me', methods=['POST', 'GET'])
            def emp_all_task_by_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()

                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT * FROM task WHERE assigned_by = %s AND  task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:
                        task_query = "SELECT * FROM task WHERE assigned_by = %s"
                        mycursor.execute(task_query, (employee_id,))

                    emp_all_task_by_me = mycursor.fetchall()
                    name_query = "SELECT employeeName FROM employee_data WHERE employeeId = %s"
                    mycursor.execute(name_query, (employee_id,))
                    employee_name = mycursor.fetchone()[0]
                    # Store employeeName in the session
                    session['employeeName'] = employee_name
                    mycursor.close()
                    return render_template("Employee_dashboard/emp_all_task_by_me.html", emp_all_task_by_me=emp_all_task_by_me, employee_name=employee_name)

            @self.app.route('/emp_all_task_to_me', methods=['POST', 'GET'])
            def emp_all_task_to_me():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                if 'employeeId' in session:
                    mycursor = mydb.cursor()
                    employee_id = session['employeeId']
                    search_query = request.args.get('taskSearch')
                    if search_query:
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE em_task.employeeId = %s AND task.task_id LIKE %s"
                        mycursor.execute(query, (employee_id, '%' + search_query + '%'))
                    else:
                        query = "SELECT task.* FROM task JOIN em_task ON task.task_id = em_task.task_id WHERE em_task.employeeId = %s"
                        mycursor.execute(query, (employee_id,))

                    emp_all_task_to_me = mycursor.fetchall()
                    name_query = "SELECT employeeName FROM employee_data WHERE employeeId = %s "
                    mycursor.execute(name_query, (employee_id,))
                    employee_name = mycursor.fetchone()[0]
                    mycursor.close()

                    return render_template("Employee_dashboard/emp_all_task_to_me.html",
                                           emp_all_task_to_me=emp_all_task_to_me, employee_name=employee_name)

            @self.app.route('/em_edit_task', methods=['POST', 'GET'])
            def EMPLOYEE_edit_task_by_emp():
                try:
                    mydb = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database='fces_dash'
                    )
                    employee_id=True

                    mycursor = mydb.cursor()
                    if request.method == 'GET':
                        view_task_id = request.args.get('task_id')
                        mycursor.execute("SELECT * FROM task WHERE task_id = %s", (view_task_id,))
                        data = mycursor.fetchone()
                        # Fetch available employee data for rendering the form
                        mycursor.execute("SELECT employeeId, employeeName FROM employee_data")
                        employee_data = mycursor.fetchall()
                        employees = [{"id": row[0], "name": row[1]} for row in employee_data]
                        mycursor.close()
                        if data:
                            task_id = data[1]
                            taskName = data[2]
                            employeeId = data[3]
                            priority = data[4]
                            deadline = data[5]
                            status = data[6]
                            description = data[7]
                            real_time_sh = data[8]
                            assigned_by=data[11]
                            print("Retrieved data:", data)
                            return render_template("Employee_dashboard/edit_task.html", data=data, task_id=task_id,
                                                   taskName=taskName, employeeId=employeeId, priority=priority,
                                                   deadline=deadline,
                                                   status=status, description=description, real_time_sh=real_time_sh,assigned_by=assigned_by,
                                                   employees=employees)

                    if request.method == 'POST':
                        print("admin request")
                        admin_edit_task = request.form
                        task_id = admin_edit_task['task_id']
                        taskName = admin_edit_task['taskName']
                        employeeIds = admin_edit_task.getlist('employeeId[]')
                        priority = admin_edit_task['priority']
                        deadline = admin_edit_task['deadline']
                        status = admin_edit_task['status']
                        description = admin_edit_task['description']
                        real_time_sh = admin_edit_task['real_time_sh']
                        assigned_by = admin_edit_task['assigned_by']
                        creator_type = 'employee_id' if employee_id else 'admin_id'


                        task_update_query = (
                            "UPDATE task SET taskName=%s, employeeId=%s, priority=%s, deadline=%s, status=%s, "
                            "description=%s, real_time_sh=%s, creator_type=%s, assigned_by=%s, assigned_to=%s WHERE task_id=%s"
                        )

                        task_values_update = (
                            taskName, ','.join(employeeIds), priority, deadline, status, description, real_time_sh,
                            creator_type, assigned_by, ','.join(employeeIds), task_id
                        )
                        mycursor.execute(task_update_query, task_values_update)
                        # Fetch existing task assignments for the task being updated
                        mycursor.execute("SELECT employeeId FROM em_task WHERE task_id = %s", (task_id,))
                        existing_employeeIds = [row[0] for row in mycursor.fetchall()]

                        to_update = set(employeeIds) & set(existing_employeeIds)

                        # Update existing task assignments if needed (e.g., change employee ID)
                        em_task_query_update = "UPDATE `em_task` SET `employeeId` = %s WHERE `task_id` = %s AND `employeeId` = %s"
                        em_task_values_update = [(employee_id, task_id, employee_id) for employee_id in to_update]
                        mycursor.executemany(em_task_query_update, em_task_values_update)

                        mydb.commit()

                        if status == 'Review':
                            return redirect('/new_task_by_me')
                        elif status == 'In-progress':
                            return redirect('/in_progess_task_by_me')
                        elif status== 'pending':
                            return redirect('/pending_task_by_me')
                        elif status == 'Completed':
                            return redirect('/completed_task_by_me')

                except Exception as e:
                    return redirect("/error_page")

            @self.app.route('/EMPLOYEE_edit_task_to_me', methods=['POST', 'GET'])
            def EMPLOYEE_edit_task_to_me():
                try:
                    mydb = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database='fces_dash'
                    )

                    mycursor = mydb.cursor()
                    if request.method == 'GET':
                        view_task_id = request.args.get('task_id')
                        mycursor.execute("SELECT * FROM task WHERE task_id = %s", (view_task_id,))
                        data = mycursor.fetchone()
                        # Fetch available employee data for rendering the form
                        mycursor.execute("SELECT employeeId, employeeName FROM employee_data")
                        employee_data = mycursor.fetchall()
                        employees = [{"id": row[0], "name": row[1]} for row in employee_data]
                        mycursor.close()
                        if data:
                            task_id = data[1]
                            taskName = data[2]
                            employeeId = data[3]
                            priority = data[4]
                            deadline = data[5]
                            status = data[6]
                            description = data[7]
                            real_time_sh = data[8]
                            assigned_by = data[11]

                            print("Retrieved data:", data)

                            return render_template("Employee_dashboard/EMPLOYEE_edit_task_to_me.html", data=data, task_id=task_id,
                                                   taskName=taskName, employeeId=employeeId, priority=priority,
                                                   deadline=deadline,
                                                   status=status, description=description, real_time_sh=real_time_sh,
                                                   assigned_by=assigned_by,
                                                   employees=employees)

                    if request.method == 'POST':
                        print("Admin request")
                        admin_edit_task = request.form
                        task_id = admin_edit_task['task_id']
                        taskName = admin_edit_task['taskName']
                        employeeIds = admin_edit_task.getlist('employeeId[]')
                        priority = admin_edit_task['priority']
                        deadline = admin_edit_task['deadline']
                        status = admin_edit_task['status']
                        description = admin_edit_task['description']
                        real_time_sh = admin_edit_task['real_time_sh']
                        assigned_by = admin_edit_task['assigned_by']

                        mycursor.execute("SELECT creator_type FROM task WHERE task_id = %s", (task_id,))
                        original_creator_type = mycursor.fetchone()[0]


                        if original_creator_type == 'admin_id':
                            creator_type = 'admin_id'
                        else:

                            creator_type = 'employee_id'


                        task_update_query = (
                            "UPDATE task SET taskName=%s, employeeId=%s, priority=%s, deadline=%s, status=%s, "
                            "description=%s, real_time_sh=%s, creator_type=%s, assigned_by=%s, assigned_to=%s WHERE task_id=%s"
                        )

                        task_values_update = (
                            taskName, ','.join(employeeIds), priority, deadline, status, description, real_time_sh,
                            creator_type, assigned_by, ','.join(employeeIds), task_id
                        )
                        mycursor.execute(task_update_query, task_values_update)
                        # Fetch existing task assignments for the task being updated
                        mycursor.execute("SELECT employeeId FROM em_task WHERE task_id = %s", (task_id,))
                        existing_employeeIds = [row[0] for row in mycursor.fetchall()]

                        to_update = set(employeeIds) & set(existing_employeeIds)

                        # Update existing task assignments if needed (e.g., change employee ID)
                        em_task_query_update = "UPDATE `em_task` SET `employeeId` = %s WHERE `task_id` = %s AND `employeeId` = %s"
                        em_task_values_update = [(employee_id, task_id, employee_id) for employee_id in to_update]
                        mycursor.executemany(em_task_query_update, em_task_values_update)

                        mydb.commit()

                        if status == 'Review':
                            return redirect('/new_task_to_me')
                        elif status == 'In-progress':
                            return redirect('/in_progess_task_to_me')
                        elif status == 'pending':
                            return redirect('/pending_task_to_me')
                        elif status == 'Completed':
                            return redirect('/completed_task_to_me')

                except Exception as e:
                    return redirect("/error_page")

            @self.app.route('/emp_view_task')
            def emp_view_task():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                view_real_time_sh = request.args.get('task_id')
                print("Received department name:", view_real_time_sh)
                mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
                mycursor.execute("select * from task where task_id = %s", (view_real_time_sh,))
                data = mycursor.fetchone()
                # Fetch available employee data for rendering the form
                mycursor.execute("SELECT employeeId, employeeName FROM employee_data")
                employee_data = mycursor.fetchall()
                employees = [{"id": row[0], "name": row[1]} for row in employee_data]
                mycursor.close()
                if data:
                    task_id = data[1]
                    taskName = data[2]
                    employeeId = data[3]
                    priority = data[4]
                    deadline = data[5]
                    status = data[6]
                    description = data[7]
                    real_time_sh = data[8]
                    print(f"VIEW DATA {data}")
                    return render_template("Employee_dashboard/emp_view_task.html", data=data, task_id=task_id,
                                           taskName=taskName, employeeId=employeeId, priority=priority,
                                           deadline=deadline,
                                           status=status, description=description, real_time_sh=real_time_sh,
                                           employees=employees)

            def get_assigned_by_name(assigned_by_id):
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                mycursor = mydb.cursor()
                mycursor.execute("SELECT employeeName,employeeId FROM employee_data WHERE employeeId = %s", (assigned_by_id,))
                result = mycursor.fetchone()
                mycursor.close()
                if result:
                    return f"{result[0]} ({result[1]})"
                else:
                    return f"Anuj Singh (anuj123)"

            @self.app.route('/view_assigned_task_to_me_emp')
            def view_assigned_task_to_me_emp():
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                view_real_time_sh = request.args.get('task_id')
                print("Received department name:", view_real_time_sh)
                mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
                mycursor.execute("select * from task where task_id = %s", (view_real_time_sh,))
                data = mycursor.fetchone()

                if data:
                    task_id = data[1]
                    taskName = data[2]
                    assigned_by = data[11]
                    assigned_by_name = get_assigned_by_name(assigned_by)# Note: Revert to using assigned_by from your data
                    priority = data[4]
                    deadline = data[5]
                    status = data[6]
                    description = data[7]
                    real_time_sh = data[8]
                    print(f"VIEW DATA {data}")
                    return render_template("Employee_dashboard/view_assigned_task_to_me_emp.html", data=data,
                                           task_id=task_id,
                                           taskName=taskName, assigned_by=assigned_by_name, priority=priority,
                                           deadline=deadline,
                                           status=status, description=description, real_time_sh=real_time_sh,
                                        )
