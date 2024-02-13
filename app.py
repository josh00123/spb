from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import connect

app = Flask(__name__)

dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser,
                                         password=connect.dbpass, host=connect.dbhost,
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/")
def home():
    return redirect("/currentjobs")


@app.route("/currentjobs")
def currentjobs():
    connection = getCursor()
    connection.execute("""SELECT j.job_id, 
       CONCAT(IFNULL(c.first_name, ''), ' ', IFNULL(c.family_name, '')) AS full_name, 
       j.job_date, j.total_cost
        FROM job j 
        JOIN customer c ON j.customer = c.customer_id 
        WHERE j.completed = 0;
        """)
    jobList = connection.fetchall()
    return render_template("currentjoblist.html", job_list=jobList)


@app.route("/oldjobs")
def oldjobs():
    connection = getCursor()
    connection.execute("""SELECT j.job_id, 
       CONCAT(IFNULL(c.first_name, ''), ' ', IFNULL(c.family_name, '')) AS full_name, 
            j.job_date, j.total_cost
        FROM job j 
        JOIN customer c ON j.customer = c.customer_id 
        WHERE j.completed = 1;
        """)
    jobList = connection.fetchall()
    return render_template("currentjoblist.html", job_list=jobList)


@app.route("/job/<int:job_id>", methods=['GET', 'POST'])
def job_details(job_id):
    connection = getCursor()

    connection.execute(
        "SELECT j.job_id, CONCAT(IFNULL(c.first_name, ''), ' ', IFNULL(c.family_name, '')) AS full_name, j.job_date, j.completed FROM job j JOIN customer c ON j.customer = c.customer_id WHERE job_id = %s;", (job_id,))
    job = connection.fetchone()

    if request.method == 'POST':
        if not job[3]:
            # Add services and parts to the job
            service_id = request.form.get('selected_service')
            part_id = request.form.get('selected_part')
            qty = request.form.get('qty')

            if service_id:
                connection.execute(
                    "INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s);", (job_id, service_id, qty))
            if part_id:
                connection.execute(
                    "INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s);", (job_id, part_id, qty))

            # Mark the job as completed
            if request.form.get('complete_job'):
                connection.execute(
                    "UPDATE job SET completed = 1 WHERE job_id = %s;", (job_id,))
            # Calculate job total cost
            calculate_job_total_cost(job_id)

            return redirect(url_for('job_details', job_id=job_id))

    # Get services and parts used in the job
    connection.execute(
        "SELECT s.service_name, js.qty, s.cost FROM job_service js JOIN service s ON js.service_id = s.service_id WHERE js.job_id = %s;", (job_id,))
    services_used = connection.fetchall()

    connection.execute(
        "SELECT p.part_name, jp.qty, p.cost FROM job_part jp JOIN part p ON jp.part_id = p.part_id WHERE jp.job_id = %s;", (job_id,))
    parts_used = connection.fetchall()

    connection.execute("SELECT * FROM service;")
    services = connection.fetchall()

    connection.execute("SELECT * FROM part;")
    parts = connection.fetchall()

    return render_template("job_details.html", job=job, services=services, parts=parts, services_used=services_used, parts_used=parts_used)


def calculate_job_total_cost(job_id):
    connection = getCursor()
    # Calculate total cost for services
    connection.execute(
        "SELECT SUM(s.cost * js.qty) FROM job_service js JOIN service s ON js.service_id = s.service_id WHERE js.job_id = %s;", (job_id,))
    total_services_cost = connection.fetchone()[0] or 0

    # Calculate total cost for parts
    connection.execute(
        "SELECT SUM(p.cost * jp.qty) FROM job_part jp JOIN part p ON jp.part_id = p.part_id WHERE jp.job_id = %s;", (job_id,))
    total_parts_cost = connection.fetchone()[0] or 0

    # Update the job total cost
    total_cost = total_services_cost + total_parts_cost
    connection.execute(
        "UPDATE job SET total_cost = %s WHERE job_id = %s;", (total_cost, job_id))

    return redirect(url_for('oldjobs'))

@app.route("/admin")
@app.route("/admin/customers")
def admin_customers():
    cursor = getCursor()
    search_term = request.args.get('search', '')
    if not search_term == '':
        query = """
        SELECT customer_id, first_name, family_name,
        FROM customer 
        WHERE first_name LIKE %s OR family_name LIKE %s 
        ORDER BY family_name, first_name;
        """
        cursor.execute(query, ('%' + search_term +
                       '%', '%' + search_term + '%'))
    else:
        query = "SELECT customer_id, first_name, family_name, email, phone FROM customer ORDER BY family_name, first_name;"
        cursor.execute(query)

    customers = cursor.fetchall()
    return render_template("admin_customers.html", customers=customers)


@app.route('/admin/customers/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        family_name = request.form['family_name']
        email = request.form['email']
        phone = request.form['phone']
        cursor = getCursor()
        query = """
        INSERT INTO customer (first_name, family_name, email, phone) 
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (first_name, family_name, email, phone))
        return redirect(url_for('admin_customers'))
    return render_template('add_customer.html')


@app.route('/admin/service', methods=['GET', 'POST'])
def service():
    if request.method == 'POST':
        service_name = request.form['service_name']
        service_cost = request.form['service_cost']
        cursor = getCursor()
        query = """INSERT INTO service (service_name, cost) VALUES (%s, %s)"""
        cursor.execute(query, (service_name, service_cost))
        return redirect('service')
    return render_template('add_service.html')


@app.route('/admin/part', methods=['GET', 'POST'])
def part():
    if request.method == 'POST':
        part_name = request.form['part_name']
        part_cost = request.form['part_cost']
        cursor = getCursor()
        query = """INSERT INTO part (part_name, cost) VALUES (%s, %s)"""
        cursor.execute(query, (part_name, part_cost))
        return redirect('part')
    return render_template('add_part.html')


@app.route('/admin/schedulejob', methods=['GET', 'POST'])
def schedule_job():
    cursor = getCursor()
    if request.method == 'POST':
        customer_id = request.form.get('customer')
        job_date = request.form.get('date')

        query = "INSERT INTO job (job_date, customer, completed, paid) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (job_date, customer_id, 0, 0))

        return redirect(url_for('schedule_job'))

    query = "SELECT customer_id, first_name, family_name FROM customer ORDER BY family_name, first_name;"
    cursor.execute(query)

    customers = cursor.fetchall()
    today = date.today()
    return render_template('schedule_job.html', customers=customers, today=today)


@app.route('/admin/bills')
def admin_bills():
    cursor = getCursor()
    query = """
    SELECT job.job_date, job.job_id, c.customer_id, CONCAT(IFNULL(c.first_name, ''), ' ', IFNULL(c.family_name, '')) AS full_name, job.completed, job.total_cost FROM job JOIN customer c ON job.customer = c.customer_id WHERE job.paid = %s;"""
    cursor.execute(query, (0,))
    bills = cursor.fetchall()

    return render_template('admin_bills.html', bills=bills)


@app.route('/admin/mark_as_paid')
def mark_as_paid():
    bill_id = request.args.get('bill_id')
    cursor = getCursor()
    query = "UPDATE job SET paid=%s WHERE job_id=%s"
    cursor.execute(query, (1, bill_id))
    return redirect(url_for('admin_bills'))


@app.route('/admin/billing_history')
def billing_history():
    cursor = getCursor()
    query = """
    SELECT j.job_date, j.total_cost, j.paid, CONCAT(IFNULL(c.first_name, ''), ' ', IFNULL(c.family_name, '')) AS full_name, c.email, CASE WHEN DATE_ADD(j.job_date, INTERVAL 14 DAY) < CURDATE() THEN 'red' ELSE 'black' END AS highlight_color FROM job j JOIN customer c ON j.customer = c.customer_id ORDER BY c.family_name, c.first_name, j.job_date;
    """

    cursor.execute(query)
    data = cursor.fetchall()
    return render_template('billing_history.html', bills=data)


if __name__ == "__main__":
    app.run(debug=True)
