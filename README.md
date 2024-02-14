## Web Application Structure  
  
The application is developed using Python Flask, Bootstrap, CSS for styling, and MySQL for data storage. The web application follows a typical Model-View-Template (MVT) architecture where routes and functions serve as the controller, templates represent the view, and data handling and interactions with the database constitute the model. It has different interfaces for technicians and administrators, enabling efficient handling of customer jobs, services, parts, and billing.  
  
### Routes & Functions  
  
- `/` (home)  
	- Function: Redirects to `/currentjobs` route.  
- `/currentjobs`  
	- Function: Retrieves list of current jobs from the database.  
	- Data Passed: List of jobs (`job_list`).  
	- Template: `currentjoblist.html`.  
- `/job/<int:job_id>`  
	- Function: Retrieves details of a specific job by its ID.  
	- Data Passed: Job details, services, parts, services used, parts used, total cost.  
	- Template: `job_details.html`.  
- `/mark_as_complete/<int:job_id>` (POST)  
	- Function: Marks a job as complete.  
	- Data Passed: Job ID.  
- `/admin`  
	- Function: Redirects to the admin section of the application.  
- `/admin/customers`  
	- Function: Retrieves list of customers from the database.  
	- Data Passed: List of customers.  
	- Template: `admin_customers.html`.  
- `/admin/customers/add` (GET, POST)  
	- Function: Allows adding new customers to the database.  
	- Data Passed: None (form data).  
	- Template: `add_customer.html`.  
- `/admin/service` (GET, POST)  
	- Function: Allows adding new services to the database.  
	- Data Passed: None (form data).  
	- Template: `add_service.html`.  
- `/admin/part` (GET, POST)  
	- Function: Allows adding new parts to the database.  
	- Data Passed: None (form data).  
	- Template: `add_part.html`.  
- `/admin/schedulejob` (GET, POST)  
	- Function: Allows scheduling new jobs.  
	- Data Passed: List of customers, today's date.  
	- Template: `schedule_job.html`.  
- `/admin/bills`  
	- Function: Retrieves list of unpaid bills from the database.  
	- Data Passed: List of unpaid bills.  
	- Template: `admin_bills.html`.  
- `/admin/mark_as_paid` (GET)  
	- Function: Marks bills as paid.  
	- Data Passed: Bill ID.  
- `/admin/billing_history`  
	- Function: Retrieves billing history for each customer.  
	- Data Passed: List of customers, billing history.  
	- Template: `billing_history.html`.  
  
## Design Decisions  
  
### GET vs. POST Methods  
- **GET Requests**: Used for data retrieval operations, such as listing current jobs or customer details, aligning with the HTTP standard for non-side-effect actions.  
- **POST Requests**: Used for actions that modify data, including adding customers, services, or parts, and marking jobs as complete, to maintain data integrity and adhere to web standards.  
  
### Use of Conditional Logic  
- Employed within templates (e.g., `job_details.html`) to switch between viewing and editing states. This approach reduces the need for additional pages for editing, streamlining the user experience by using a single template for related actions.  
  
### Bootstrap for Responsive Design  
- Chosen for its comprehensive collection of responsive design components, ensuring the application's accessibility across a variety of devices and screen sizes, thus enhancing user experience.  
  
### Consistent Navigation Bar  
- Implemented across all templates to provide direct access to the application's main sections, enhancing navigation and making the application more user-friendly and intuitive.  
  
## Database Questions  
### 1. The SQL statement creates the job table and defines its fields/columns:  
```sql  
CREATE TABLE IF NOT EXISTS job  
(  
job_id INT auto_increment PRIMARY KEY NOT NULL,  
job_date date NOT NULL,  
customer int NOT NULL,  
total_cost decimal(6,2) default null,  
completed tinyint default 0,  
paid tinyint default 0,  
  
FOREIGN KEY (customer) REFERENCES customer(customer_id)  
ON UPDATE CASCADE  
);  
```  
  
### 2. The line of SQL code sets up the relationship between the customer and job tables:  
  
```sql  
FOREIGN KEY (customer) REFERENCES customer(customer_id)  
```  
  
### 3. The lines of SQL code insert details into the parts table:  
  
```sql  
INSERT INTO part (`part_name`, `cost`) VALUES ('Windscreen', '560.65');  
INSERT INTO part (`part_name`, `cost`) VALUES ('Headlight', '35.65');  
INSERT INTO part (`part_name`, `cost`) VALUES ('Wiper blade', '12.43');  
INSERT INTO part (`part_name`, `cost`) VALUES ('Left fender', '260.76');  
INSERT INTO part (`part_name`, `cost`) VALUES ('Right fender', '260.76');  
INSERT INTO part (`part_name`, `cost`) VALUES ('Tail light', '120.54');  
INSERT INTO part (`part_name`, `cost`) VALUES ('Hub Cap', '22.89');  
```  
  
### 4. When the time and date a service or part was added to a job needed to be recorded, the below fields/columns need to added:  
  
- **Table Name:** `job_part`  
- **New Column Name:** `added_timestamp`  
- **Data Type:** `DATETIME`  
  
- **Table Name:** `job_service`  
- **New Column Name:** `added_timestamp`  
- **Data Type:** `DATETIME`  
  
### 5. Suppose logins were implemented. Why is it important for technicians and the office administrator to access different routes?  
  
Implementing different access routes for technicians and office administrators is mainly for security, privacy, and user efficiency. Below are two examples of problems that could occur if all of the web app facilities were available to everyone. :  
  
- **Unauthorized Data Access:** If all employees have unrestricted access to financial reports or sensitive customer information, it could lead to privacy breaches or misuse of data. For instance, a technician accidentally or intentionally sharing confidential customer data could result in privacy violations and legal repercussions.  
  
- **Financial loss:** If all employees can view and edit pricing details, it could lead to unauthorized discounts or changes in service rates. This could affect the business's pricing strategy and lead to severe financial loss.  
  
Thus, it is crucial to apply different levels of authority to access different information, especially some sensitive information should only be available to certain users.