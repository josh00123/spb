from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import connect
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sdfiweksdifwerijsdkfjiwe'

dbconn = None
connection = None

# 登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 角色导航处理器
@app.context_processor
def inject_user_role():
    if current_user.is_authenticated:
        return dict(current_user=current_user)
    return dict(current_user=None)

# 用户类
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    cursor = getCursor()
    cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user_row = cursor.fetchone()
    if user_row:
        return User(user_row[0], user_row[1], user_row[2])
    return None

# 登录页
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = getCursor()
        cursor.execute("SELECT id, username, password, role FROM users WHERE username = %s", (username,))
        user_row = cursor.fetchone()
        
        if user_row and user_row[2] == password:
            user = User(user_row[0], user_row[1], user_row[3])
            login_user(user)
            flash('登录成功！', 'success')
            return redirect(url_for('home'))
        flash('用户名或密码错误！', 'error')
    
    return render_template('login.html')

# 登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'success')
    return redirect(url_for('login'))

# 角色装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('需要管理员权限！', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

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
@login_required
def currentjobs():
    connection = getCursor()
    connection.execute("""SELECT j.job_id, 
       CONCAT(IFNULL(c.first_name, ''), ' ', IFNULL(c.family_name, '')) AS full_name, 
       j.job_date, j.total_cost
        FROM job j 
        JOIN customer c ON j.customer = c.customer_id 
        WHERE j.completed = 0 ORDER BY j.job_date;""")
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
            service_id = request.form.get('selected_service')
            part_id = request.form.get('selected_part')
            service_qty = request.form.get('service_qty')
            part_qty = request.form.get('part_qty')

            if service_id:
                if service_qty == '':
                    service_qty = 0
                connection.execute(
                    "INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s);", (job_id, service_id, service_qty))
            if part_id:
                if part_qty == '':
                    part_qty = 0
                connection.execute(
                    "INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s);", (job_id, part_id, part_qty))
                
            calculate_job_total_cost(job_id)
            return redirect(url_for('job_details', job_id=job_id))

    connection.execute("SELECT s.service_name, js.qty, s.cost FROM job_service js JOIN service s ON js.service_id = s.service_id WHERE js.job_id = %s;", (job_id,))
    services_used = connection.fetchall()

    connection.execute("SELECT p.part_name, jp.qty, p.cost FROM job_part jp JOIN part p ON jp.part_id = p.part_id WHERE jp.job_id = %s;", (job_id,))
    parts_used = connection.fetchall()

    connection.execute("SELECT * FROM service ORDER BY service_name;")
    services = connection.fetchall()

    connection.execute("SELECT * FROM part ORDER BY part_name;")
    parts = connection.fetchall()

    connection.execute("SELECT total_cost FROM job WHERE job_id=%s;", (job_id,))
    total_cost = connection.fetchone()

    return render_template("job_details.html", job=job, services=services, parts=parts, services_used=services_used, parts_used=parts_used, total_cost=total_cost)

@app.route('/mark_as_complete/<int:job_id>', methods=['POST'])
def mark_as_complete(job_id):
    connection = getCursor()
    connection.execute("UPDATE job SET completed = 1 WHERE job_id = %s;", (job_id,))
    return redirect(url_for('currentjobs'))

def calculate_job_total_cost(job_id):
    connection = getCursor()
    connection.execute("SELECT SUM(s.cost * js.qty) FROM job_service js JOIN service s ON js.service_id = s.service_id WHERE js.job_id = %s;", (job_id,))
    total_services_cost = connection.fetchone()[0] or 0

    connection.execute("SELECT SUM(p.cost * jp.qty) FROM job_part jp JOIN part p ON jp.part_id = p.part_id WHERE jp.job_id = %s;", (job_id,))
    total_parts_cost = connection.fetchone()[0] or 0

    total_cost = total_services_cost + total_parts_cost
    connection.execute("UPDATE job SET total_cost = %s WHERE job_id = %s;", (total_cost, job_id))
    return redirect(url_for('currentjobs'))

# ==================== 管理员路由全保护 ====================
@app.route('/admin')
@login_required
@admin_required
def admin_home():
    return redirect(url_for('admin_customers'))

@app.route('/admin/customers')
@login_required
@admin_required
def admin_customers():
    cursor = getCursor()
    search_term = request.args.get('search', '')
    if search_term:
        query = "SELECT first_name, family_name, email, phone FROM customer WHERE first_name LIKE %s OR family_name LIKE %s ORDER BY family_name, first_name;"
        cursor.execute(query, ('%' + search_term + '%', '%' + search_term + '%'))
    else:
        query = "SELECT first_name, family_name, email, phone FROM customer ORDER BY family_name, first_name;"
        cursor.execute(query)
    customers = cursor.fetchall()
    return render_template("admin_customers.html", customers=customers)

@app.route('/admin/customers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        family_name = request.form['family_name']
        email = request.form['email']
        phone = request.form['phone']
        if len(phone) > 11:
            flash("Phone number can't be longer than 11 characters.", "error")
            return redirect(url_for('add_customer'))
        cursor = getCursor()
        query = "INSERT INTO customer (first_name, family_name, email, phone) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (first_name, family_name, email, phone))
        return redirect(url_for('admin_customers'))
    return render_template('add_customer.html')

@app.route('/admin/service', methods=['GET', 'POST'])
@login_required
@admin_required
def service():
    if request.method == 'POST':
        service_name = request.form['service_name']
        service_cost = request.form['service_cost']
        cursor = getCursor()
        query = "INSERT INTO service (service_name, cost) VALUES (%s, %s)"
        cursor.execute(query, (service_name, service_cost))
        return redirect(url_for('service'))
    return render_template('add_service.html')

@app.route('/admin/part', methods=['GET', 'POST'])
@login_required
@admin_required
def part():
    if request.method == 'POST':
        part_name = request.form['part_name']
        part_cost = request.form['part_cost']
        cursor = getCursor()
        query = "INSERT INTO part (part_name, cost) VALUES (%s, %s)"
        cursor.execute(query, (part_name, part_cost))
        return redirect(url_for('part'))
    return render_template('add_part.html')

@app.route('/admin/schedulejob', methods=['GET', 'POST'])
@login_required
@admin_required
def schedule_job():
    cursor = getCursor()
    if request.method == 'POST':
        customer_id = request.form.get('customer')
        job_date = request.form.get('date')
        query = "INSERT INTO job (job_date, customer, completed, paid) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (job_date, customer_id, 0, 0))
        flash('The job is scheduled successfully', 'success')
        return redirect(url_for('schedule_job'))

    query = "SELECT customer_id, first_name, family_name FROM customer ORDER BY family_name, first_name;"
    cursor.execute(query)
    customers = cursor.fetchall()
    today = date.today()
    return render_template('schedule_job.html', customers=customers, today=today)

@app.route('/admin/bills')
@login_required
@admin_required
def admin_bills():
    cursor = getCursor()
    search_term = request.args.get('search', '')
    if search_term:
        query = "SELECT job.job_id, job.job_date, CONCAT(IFNULL(c.first_name, ''), ' ', IFNULL(c.family_name, '')) AS full_name, job.completed, job.total_cost FROM job JOIN customer c ON job.customer = c.customer_id WHERE job.paid = %s AND (c.first_name LIKE %s OR c.family_name LIKE %s) ORDER BY job.job_date, c.family_name, c.first_name;"
        cursor.execute(query, (0, '%' + search_term + '%', '%' + search_term + '%'))
    else:
        query = "SELECT job.job_id, job.job_date, CONCAT(IFNULL(c.first_name, ''), ' ', IFNULL(c.family_name, '')) AS full_name, job.completed, job.total_cost FROM job JOIN customer c ON job.customer = c.customer_id WHERE job.paid = %s ORDER BY job.job_date, c.family_name, c.first_name;"
        cursor.execute(query, (0,))
    bills = cursor.fetchall()
    return render_template('admin_bills.html', bills=bills)

@app.route('/admin/mark_as_paid')
@login_required
@admin_required
def mark_as_paid():
    bill_id = request.args.get('bill_id')
    cursor = getCursor()
    query = "UPDATE job SET paid=%s WHERE job_id=%s"
    cursor.execute(query, (1, bill_id))
    return redirect(url_for('admin_bills'))

@app.route('/admin/billing_history')
@login_required
@admin_required
def billing_history():
    cursor = getCursor()
    query = "SELECT customer_id, first_name, family_name, email FROM customer ORDER BY family_name, first_name;"
    cursor.execute(query)
    customers = cursor.fetchall()
    customer_details = []
    data = []
    for customer in customers:
        query = "SELECT j.job_date, j.total_cost, j.paid, CASE WHEN DATE_ADD(j.job_date, INTERVAL 14 DAY) < CURDATE() THEN 'red' ELSE 'black' END AS highlight_color FROM job j WHERE j.customer = %s ORDER BY j.job_date;"
        cursor.execute(query, (customer[0],))
        jobs = cursor.fetchall()
        if len(jobs) > 0:
            customer_details.append(customer)
            data.append(jobs)
    return render_template('billing_history.html', customers=customer_details, bills=data)

if __name__ == "__main__":
    app.run(debug=True)
