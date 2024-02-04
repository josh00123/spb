from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@app.route("/")
def home():
    return redirect("/currentjobs")

@app.route("/currentjobs")
def currentjobs():
    connection = getCursor()
    connection.execute("SELECT j.job_id, c.first_name AS customer_name, j.job_date FROM job j JOIN customer c ON j.customer = c.customer_id;")
    jobList = connection.fetchall()
    return render_template("currentjoblist.html", job_list=jobList)

@app.route("/oldjobs")
def oldjobs():
    connection = getCursor()
    connection.execute("SELECT job_id, customer, job_date FROM job WHERE completed = 0;")
    jobList = connection.fetchall()
    return render_template("currentjoblist.html", job_list=jobList)

@app.route("/job/<int:job_id>", methods=['GET', 'POST'])
def job_details(job_id):
    connection = getCursor()
    connection.execute("SELECT job_id, customer, job_date, completed FROM job WHERE job_id = %s;", (job_id,))
    job = connection.fetchone()

    if request.method == 'POST':
        if not job['completed']:
            # Add services and parts to the job
            service_id = request.form.get('selected_service')
            part_id = request.form.get('selected_part')
            qty = request.form.get('qty')

            if service_id:
                connection.execute("INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s);", (job_id, service_id, qty))
            elif part_id:
                connection.execute("INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s);", (job_id, part_id, qty))

            # Mark the job as completed
            if request.form.get('complete_job'):
                connection.execute("UPDATE job SET completed = 1 WHERE job_id = %s;", (job_id,))
                # Calculate job total cost
                calculate_job_total_cost(job_id)

    # Get services and parts used in the job
    connection.execute("SELECT s.service_name, js.qty, s.cost FROM job_service js JOIN service s ON js.service_id = s.service_id WHERE js.job_id = %s;", (job_id,))
    services_used = connection.fetchall()

    connection.execute("SELECT p.part_name, jp.qty, p.cost FROM job_part jp JOIN part p ON jp.part_id = p.part_id WHERE jp.job_id = %s;", (job_id,))
    parts_used = connection.fetchall()

    return render_template("job_details.html", job=job, services_used=services_used, parts_used=parts_used)

def calculate_job_total_cost(job_id):
    connection = getCursor()
    # Calculate total cost for services
    connection.execute("SELECT SUM(s.cost * js.qty) FROM job_service js JOIN service s ON js.service_id = s.service_id WHERE js.job_id = %s;", (job_id,))
    total_services_cost = connection.fetchone()[0] or 0

    # Calculate total cost for parts
    connection.execute("SELECT SUM(p.cost * jp.qty) FROM job_part jp JOIN part p ON jp.part_id = p.part_id WHERE jp.job_id = %s;", (job_id,))
    total_parts_cost = connection.fetchone()[0] or 0

    # Update the job total cost
    total_cost = total_services_cost + total_parts_cost
    connection.execute("UPDATE job SET total_cost = %s WHERE job_id = %s;", (total_cost, job_id))

if __name__ == "__main__":
    app.run(debug=True)
