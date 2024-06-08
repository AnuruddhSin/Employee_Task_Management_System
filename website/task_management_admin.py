from flask import render_template,request,redirect,session
import mysql.connector
import MySQLdb.cursors
from mysql.connector.errors import OperationalError

class TASK_MANAGEMENT_ADMIN_AUTH:
    def __init__(self, app):
        self.app = app
        self.route()
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
        last_task_id = self.get_last_task_id_numeric('AT')
        new_task_id_numeric = last_task_id + 1
        new_numeric_part = str(new_task_id_numeric).zfill(7)
        new_task_id = "AT" + new_numeric_part
        self.update_last_task_id_numeric('AT', new_task_id_numeric)
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
        @self.app.route('/Admin add task', methods=['POST', 'GET'])
        def add_task_admin():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'

            )
            is_admin = True
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

                creator_type = 'admin_id' if is_admin else 'employee_id'
                assigned_by = session.get('admin_id')

                task_query = "INSERT INTO `task` (`task_id`, `taskName`,`employeeId`, `priority`, `deadline`, `status`, `description`, `real_time_sh`, `creator_type`, `assigned_by`) VALUES (%s,%s,%s,%s, %s, %s, %s, %s, %s, %s)"
                task_values = (
                    task_id, taskName, ','.join(employeeIds), priority, deadline, status, description, real_time_sh,
                    creator_type, assigned_by)
                self.mycursor.execute(task_query, task_values)
                self.mydb.commit()

                em_task_query = "INSERT INTO `em_task` (`task_id`, `employeeId`) VALUES (%s, %s)"
                em_task_values = [(task_id, employee_id) for employee_id in employeeIds]
                self.mycursor.executemany(em_task_query, em_task_values)
                self.mydb.commit()

                return redirect('/Admin mang task')


            mycursor = mydb.cursor()


            mycursor.execute("SELECT employeeId, employeeName FROM employee_data WHERE updated_by='admin' ")
            employee_data = mycursor.fetchall()
            employees = [{"id": row[0], "name": row[1]} for row in employee_data]
            mycursor.close()
            return render_template("admin_dashboard/add_task.html", employees=employees)

        @self.app.route('/Admin mang task', methods=['POST', 'GET'])
        def mang_task_admin():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            search_query = request.args.get('taskSearch')
            if search_query:
                query = "SELECT * FROM task WHERE creator_type = 'admin_id' AND task_id LIKE %s"
                mycursor.execute(query, ('%' + search_query + '%',))
            else:
                mycursor.execute("SELECT * FROM task WHERE creator_type = 'admin_id'")

            task = mycursor.fetchall()
            mycursor.close()
            return render_template("admin_dashboard/manage_task.html", task=task)

        @self.app.route('/admin_edit_task', methods=['POST', 'GET'])
        def update_task_by_admin():
            try:
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                is_admin = True
                mycursor = mydb.cursor()
                if request.method == 'GET':
                    view_task_id = request.args.get('task_id')
                    mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
                    mycursor.execute("SELECT * FROM task WHERE task_id = %s", (view_task_id,))
                    data = mycursor.fetchone()
                    mycursor.execute("SELECT employeeId, employeeName FROM employee_data")
                    employee_data = mycursor.fetchall()
                    employees = [{"id": row[0], "name": row[1]} for row in employee_data]
                    mycursor.close()
                    if data:
                        task_id=data[1]
                        taskName = data[2]
                        employeeId = data[3]
                        priority = data[4]
                        deadline = data[5]
                        status = data[6]
                        description = data[7]
                        real_time_sh = data[8]

                        print("Retrieved data:", data)

                        return render_template("admin_dashboard/admin_edit_task.html", data=data,task_id=task_id,
                                           taskName=taskName,employeeId=employeeId,priority=priority,deadline=deadline,
                                           status=status,description=description,real_time_sh=real_time_sh,
                                               employees=employees)
                if request.method == 'POST':
                    admin_edit_task = request.form
                    task_id = admin_edit_task['task_id']
                    taskName = admin_edit_task['taskName']
                    employeeIds = admin_edit_task.getlist('employeeId[]')
                    priority = admin_edit_task['priority']
                    deadline = admin_edit_task['deadline']
                    status = admin_edit_task['status']
                    description = admin_edit_task['description']
                    real_time_sh = admin_edit_task['real_time_sh']

                    creator_type = 'admin_id' if is_admin else 'employee_id'
                    assigned_by = session.get('admin_id')

                    task_update_query = (
                        "UPDATE task SET taskName=%s, employeeId=%s, priority=%s, deadline=%s, status=%s, "
                        "description=%s, real_time_sh=%s, creator_type=%s, assigned_by=%s, assigned_to=%s WHERE task_id=%s"
                    )

                    task_values_update = (
                        taskName, ','.join(employeeIds), priority, deadline, status, description, real_time_sh,
                        creator_type, assigned_by, ','.join(employeeIds), task_id
                    )
                    mycursor.execute(task_update_query, task_values_update)
                    mycursor.execute("SELECT employeeId FROM em_task WHERE task_id = %s", (task_id,))
                    existing_employeeIds = [row[0] for row in mycursor.fetchall()]

                    to_update = set(employeeIds) & set(existing_employeeIds)

                    em_task_query_update = "UPDATE `em_task` SET `employeeId` = %s WHERE `task_id` = %s AND `employeeId` = %s"
                    em_task_values_update = [(employee_id, task_id, employee_id) for employee_id in to_update]
                    mycursor.executemany(em_task_query_update, em_task_values_update)

                    mydb.commit()

                mycursor.close()
                return redirect("/Admin mang task")

            except Exception as e:
                return redirect("/error_page")

        @self.app.route('/admin view task')
        def admin_view_task():
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
                return render_template("admin_dashboard/view_task.html", data=data, task_id=task_id,
                                       taskName=taskName, employeeId=employeeId, priority=priority, deadline=deadline,
                                       status=status, description=description, real_time_sh=real_time_sh,
                                       employees=employees)




