from flask import render_template,request
import mysql.connector

generated_uuids = set()
from flask import session, redirect

class TASK_ACT_MANAGEMENT:
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

    def get_last_querry_numeric(self, prefix):
        try:
            with open(f'Query_task_{prefix}_task_id.txt', 'r') as file:
                last_task_id = int(file.read().strip())
        except FileNotFoundError:
            last_task_id = 0  # Start from 0 if the file doesn't exist
        return last_task_id

    def generate_unique_queryId(self):
        last_task_id = self.get_last_querry_numeric('QT')
        new_task_id_numeric = last_task_id + 1
        new_numeric_part = str(new_task_id_numeric).zfill(4)
        new_task_id = "QT" + new_numeric_part
        self.update_last_querry_numeric('QT', new_task_id_numeric)
        return new_task_id

    def update_last_querry_numeric(self, prefix, new_value):
        with open(f'Query_task_{prefix}_task_id.txt', 'w') as file:
            file.write(str(new_value))

    def update_added_task(self):
        updated_by = "updates"
        return updated_by

    def route(self):
        @self.app.route('/add_task_issue', methods=['POST', 'GET'])
        def tack_issue_add():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )

            mycursor = mydb.cursor()

            if request.method == 'POST':
                is_employee = True
                add_task = request.form
                task_idss = add_task['task_idss']
                task_issue = add_task['task_issue']
                task_querry_id = self.generate_unique_queryId()



                employeeId = session.get('employeeId')
                creator_by = 'is_employee' if is_employee else 'admin_id'
                asss_by = session.get('is_employee')

                task_action_query = "INSERT INTO task_action (`task_idss`, `taskNamess`, `task_issue`, `task_querry_id`, `employeeId`,`creator_by`,`creator_type`,`description`,`asss_by`) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s)"

                mycursor.execute("SELECT employeeId,taskName,creator_type,description FROM task WHERE task_id = %s", (task_idss,))
                task_info = mycursor.fetchone()

                if task_info:
                    assigned_employee_ids = task_info[0].split(',')
                    taskNamess = task_info[1]
                    creator_type = task_info[2]
                    description=task_info[3]

                    task_action_values = [
                        (task_idss, taskNamess, task_issue, task_querry_id, ' ,'.join(assigned_employee_ids),
                         creator_by, creator_type, description, asss_by)]
                    self.mycursor.executemany(task_action_query, task_action_values)
                    self.mydb.commit()


                    if employeeId in assigned_employee_ids:
                        em_task_query = "INSERT INTO `em_task_action` (`task_querry_id`,`task_idss`, `employeeId`) VALUES (%s,%s, %s)"
                        em_task_values = [(task_querry_id,task_idss, employee_id) for employee_id in assigned_employee_ids]
                        self.mycursor.executemany(em_task_query, em_task_values)
                        self.mydb.commit()
                    else:
                        return "You are not authorized to add tasks for this assignment."

                mycursor.close()
                return redirect("unsolved_quaries")

            mycursor = mydb.cursor()
            employeeId = session.get('employeeId')
            mycursor.execute(
                "SELECT DISTINCT ta.task_id, ta.taskName FROM task ta INNER JOIN em_task et ON ta.task_id = et.task_id WHERE et.employeeId = %s",
                (employeeId,))
            task_data = mycursor.fetchall()
            return render_template("Employee_dashboard/add_task_issue.html", task_data=task_data)

        @self.app.route('/manage_task_quaries')
        def emp_task_report():
            return render_template("Employee_dashboard/manage_task_quaries.html")

        @self.app.route('/manage_task_quaries_by_admin')
        def emp_task_report_to_admin():
            return render_template("admin_dashboard/manage_task_quaries_by_admin.html")

        @self.app.route('/unsolved_quaries')
        def unsolved_quaries():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            if 'employeeId' in session:
                mycursor = mydb.cursor()
                employee_id = session['employeeId']
                # Modify your SQL query to join the task_action and task tables
                qert="SELECT task_action.* FROM task_action JOIN em_task_action ON task_action.task_querry_id=em_task_action.task_querry_id WHERE em_task_action.employeeId=%s AND task_updates!='updates'  "
                mycursor.execute(qert, (employee_id,))
                task_querry = mycursor.fetchall()
                mycursor.close()
                return render_template("Employee_dashboard/unsolved_quaries.html" ,task_querry=task_querry)

        @self.app.route('/unsolved_quaries_by_admin')
        def unsolved_quaries_by_admin():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )

            mycursor = mydb.cursor()
                # employee_id = session['employeeId']

            qert = "SELECT * FROM task_action  WHERE task_updates!='updates' AND creator_type='admin_id' "
            mycursor.execute(qert)
            task_querry = mycursor.fetchall()
            mycursor.close()
            return render_template("admin_dashboard/unsolved_quaries.html", task_querry=task_querry)

        @self.app.route('/solved_queries')
        def solved_queries():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            employee_id = session['employeeId']
            # Modify your SQL query to join the task_action and task tables
            qert = "SELECT task_action.* FROM task_action JOIN em_task_action ON task_action.task_querry_id=em_task_action.task_querry_id WHERE em_task_action.employeeId=%s AND task_updates='updates' "
            mycursor.execute(qert, (employee_id,))
            task_querry = mycursor.fetchall()
            mycursor.close()
            return render_template("Employee_dashboard/solved_queries.html",task_querry=task_querry)

        @self.app.route('/solved_queries_by_admin')
        def solved_queries_by_admin():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            # employee_id = session['employeeId']
            qert = "SELECT * FROM task_action WHERE task_updates='updates' AND creator_type='admin_id' "
            mycursor.execute(qert)
            task_querry = mycursor.fetchall()
            mycursor.close()
            return render_template("admin_dashboard/solved_queries.html", task_querry=task_querry)

        @self.app.route('/update_quarries', methods=['GET', 'POST'])
        def update_quarries():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            is_employee=True
            mycursor = mydb.cursor()
            if request.method == 'GET':
                task_querry_id = request.args.get('task_querry_id')
                print("Received department name:", task_querry_id)
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM task_action WHERE task_querry_id = %s", (task_querry_id,))
                data = mycursor.fetchone()
                if data:
                    print("Retrieved data:", data)
                    return render_template("Employee_dashboard/update_quarries.html",data=data)


            if request.method == 'POST' :
                update_issue_task=request.form
                task_querry_id=update_issue_task['task_querry_id']
                task_idss=update_issue_task['task_idss']
                task_issue=update_issue_task['task_issue']
                task_solution=update_issue_task['task_solution']
                creator_by = 'is_employee' if is_employee else 'admin_id'
                asss_by = session.get('is_employee')
                task_updates=self.update_added_task()

                task_update_query=("UPDATE task_action SET task_idss=%s ,task_issue=%s,creator_by=%s, asss_by=%s,task_solution=%s,task_updates=%s WHERE task_querry_id=%s " )

                task_values_update=(task_idss,task_issue,creator_by,asss_by,task_solution,task_updates,task_querry_id)

                mycursor.execute(task_update_query,task_values_update)
                mydb.commit()
                em_task_update_query = (
                    "UPDATE em_task_action SET  task_idss=%s WHERE task_querry_id=%s"
                )

                em_task_values_update = (task_idss, task_querry_id)

                mycursor.execute(em_task_update_query, em_task_values_update)
                mydb.commit()

            mycursor.close()

            return redirect('/solved_queries')

        @self.app.route('/update_quarries_by_admin', methods=['GET', 'POST'])
        def update_quarries_by_admin():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            is_employee = True
            mycursor = mydb.cursor()
            if request.method == 'GET':
                task_querry_id = request.args.get('task_querry_id')
                print("Received department name:", task_querry_id)
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM task_action WHERE task_querry_id = %s", (task_querry_id,))
                data = mycursor.fetchone()
                if data:
                    print("Retrieved data:", data)
                    return render_template("admin_dashboard/update_quarries.html", data=data)

            if request.method == 'POST':
                update_issue_task = request.form
                task_querry_id = update_issue_task['task_querry_id']
                task_idss = update_issue_task['task_idss']
                task_issue = update_issue_task['task_issue']
                task_solution = update_issue_task['task_solution']
                creator_by = 'is_employee' if is_employee else 'admin_id'
                asss_by = session.get('is_employee')
                task_updates = self.update_added_task()

                task_update_query = (
                    "UPDATE task_action SET task_idss=%s ,task_issue=%s,creator_by=%s, asss_by=%s,task_solution=%s,task_updates=%s WHERE task_querry_id=%s ")

                task_values_update = (
                task_idss, task_issue, creator_by, asss_by, task_solution, task_updates, task_querry_id)

                mycursor.execute(task_update_query, task_values_update)
                mydb.commit()
                em_task_update_query = (
                    "UPDATE em_task_action SET  task_idss=%s WHERE task_querry_id=%s"
                )

                em_task_values_update = (task_idss, task_querry_id)

                mycursor.execute(em_task_update_query, em_task_values_update)
                mydb.commit()

            mycursor.close()

            return redirect('/solved_queries_by_admin')

        @self.app.route('/view_action', methods=['GET', 'POST'])
        def view_quarries():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            if request.method == 'GET':
                task_querry_id = request.args.get('task_querry_id')
                print("Received department name:", task_querry_id)
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM task_action WHERE task_querry_id = %s AND task_updates!='updates'", (task_querry_id,))
                datass = mycursor.fetchone()
                if datass:
                    print("Retrieved data:", datass)
                    return render_template("Employee_dashboard/view_action.html", datass=datass)

        @self.app.route('/view_task_solution', methods=['GET', 'POST'])
        def view_task_solution():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            if request.method == 'GET':
                task_querry_id = request.args.get('task_querry_id')
                print("Received department name:", task_querry_id)
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM task_action WHERE task_querry_id = %s AND task_updates='updates' ", (task_querry_id,))
                datass = mycursor.fetchone()
                if datass:
                    print("Retrieved data:", datass)
                    return render_template("Employee_dashboard/view_task_solution.html", datass=datass)

        @self.app.route('/view_action_by_admin', methods=['GET', 'POST'])
        def view_action_by_admin():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            if request.method == 'GET':
                task_querry_id = request.args.get('task_querry_id')
                print("Received department name:", task_querry_id)
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM task_action WHERE task_querry_id = %s AND task_updates!='updates'",
                                 (task_querry_id,))
                datass = mycursor.fetchone()
                if datass:
                    print("Retrieved data:", datass)
                    return render_template("admin_dashboard/view_action_by_admin.html", datass=datass)

        @self.app.route('/view_task_solution_by_admin', methods=['GET', 'POST'])
        def view_task_solution_by_admin():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            if request.method == 'GET':
                task_querry_id = request.args.get('task_querry_id')
                print("Received department name:", task_querry_id)
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM task_action WHERE task_querry_id = %s AND task_updates='updates' ",
                                 (task_querry_id,))
                datass = mycursor.fetchone()
                if datass:
                    print("Retrieved data:", datass)
                    return render_template("admin_dashboard/view_task_solution_by_admin.html", datass=datass)





