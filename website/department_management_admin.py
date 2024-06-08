from flask import render_template,request,redirect
import mysql.connector
import MySQLdb.cursors
class DEPARTMENT_MANAGEMENT_ADMIN_AUTH:
    def __init__(self, app):
        self.app = app
        self.route()

    def route(self):
        @self.app.route('/Admin add dep', methods=['POST', 'GET'])
        def add_depart_admin():
            if request.method == 'POST':
                try:

                    mydb = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database='fces_dash'
                    )
                    mycursor = mydb.cursor()


                    teamName = request.form['teamName']
                    teamAdmin = request.form['teamAdmin']
                    teamSubadmin = request.form.getlist('teamSubadmin')
                    employeeIds = request.form.getlist('employeeId[]')
                    description = request.form['description']


                    sql_query = "INSERT INTO `team` (`teamName`, `teamAdmin`, `teamSubadmin`, `employeeId`, `description`) VALUES (%s, %s, %s, %s, %s)"
                    values = [teamName, teamAdmin, ', '.join(teamSubadmin),  ', '.join(employeeIds), description]
                    mycursor.execute(sql_query, values)
                    mydb.commit()

                    mycursor.close()
                    return redirect("/Admin mang dep")
                except Exception as e:
                    print("Error:", e)
                    return "An error occurred while adding department."

            try:

                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                mycursor = mydb.cursor()
                mycursor.execute("SELECT employeeId, employeeName FROM employee_data")
                employee_data = mycursor.fetchall()
                employees = [{"id": row[0], "name": row[1]} for row in employee_data]
                mycursor.close()
                return render_template("admin_dashboard/add_department.html", employees=employees)
            except Exception as e:
                print("Error:", e)
                return "An error occurred while fetching employee data."


        @self.app.route('/Admin mang dep', methods=['POST', 'GET'])
        def mang_depart_admin():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM team")
            data = mycursor.fetchall()
            mycursor.close()

            return render_template("admin_dashboard/manage_department.html", team=data)

        @self.app.route('/deletes/<string:teamName_data>', methods=['POST', 'GET'])
        def delete_depart(teamName_data):
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )
            mycursor = mydb.cursor()
            mycursor.execute("DELETE FROM team WHERE teamName=%s", (teamName_data,))
            mydb.commit()
            return redirect("/Admin mang dep")

        @self.app.route('/admin_view_department', methods=['GET'])
        def admin_view_department():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='fces_dash'
            )

            view_department = request.args.get('teamName')

            mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
            mycursor.execute("SELECT * FROM team WHERE teamName = %s", (view_department,))
            data = mycursor.fetchone()
            # Fetch available employee data for rendering the form
            mycursor.execute("SELECT employeeId, employeeName FROM employee_data")
            employee_data = mycursor.fetchall()
            employees = [{"id": row[0], "name": row[1]} for row in employee_data]
            mycursor.close()

            print("Retrieved data:", data)
            teamName = data[1]
            teamAdmin = data[2]
            teamSubadmin = data[3]
            employeeId = data[4]
            description= data[5]

            return render_template("admin_dashboard/view_department.html", data=data,teamName=teamName,
                                   teamAdmin=teamAdmin,teamSubadmin=teamSubadmin,employeeId=employeeId,description=description,employees=employees)

        @self.app.route('/edit_department', methods=['POST', 'GET'])
        def edit_department():
            try:
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='fces_dash'
                )
                mycursor = mydb.cursor()

                if request.method == 'GET':
                    view_teamName = request.args.get('teamName')
                    mycursor.execute("SELECT * FROM team WHERE teamName = %s", (view_teamName,))
                    data = mycursor.fetchone()
                    print("KAttga")
                    # Fetch available employee data for rendering the form
                    mycursor.execute("SELECT employeeId, employeeName FROM employee_data")
                    employee_data = mycursor.fetchall()
                    employees = [{"id": row[0], "name": row[1]} for row in employee_data]
                    mycursor.close()

                    if data:
                        teamName = data[1]
                        teamAdmin = data[2]
                        teamSubadmin = data[3].split(', ')
                        employeeId = data[4].split(', ')
                        description = data[5]
                        print("emp data")

                        return render_template("admin_dashboard/edit_department.html", data=data, teamName=teamName,
                                               teamAdmin=teamAdmin, teamSubadmin=teamSubadmin,
                                               employeeId=employeeId, employees=employees,
                                               description=description)

                if request.method == 'POST':
                    print("Post data")
                    edited_data = request.form
                    teamName = edited_data['teamName']
                    teamAdmin = edited_data['teamAdmin']
                    teamSubadmin = edited_data.getlist('teamSubadmin')
                    employeeId = edited_data.getlist('employeeId')
                    description = edited_data['description']

                    mycursor.execute(
                        "UPDATE `team` SET teamAdmin=%s, teamSubadmin=%s, employeeId=%s, description=%s WHERE teamName=%s",
                        (teamAdmin, ', '.join(teamSubadmin), ', '.join(employeeId), description, teamName))
                    mydb.commit()
                    mycursor.close()

                    return redirect("/Admin mang dep")

            except Exception as e:
                print("Error:", e)
                return "An error occurred."

            return "Invalid request"

