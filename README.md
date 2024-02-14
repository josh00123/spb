# SPB - Selwyn Panel Beaters

## COMP636 Assignment

### Introduction

Selwyn Panel Beaters has decided to upgrade their internal system from a text-based system to a web-based system. This task involves developing a small Web Application to assist in managing customers, jobs, services, parts, and billing. Additionally, a report will be written as part of this assignment.

In the current system, Selwyn Panel Beaters record multiple items (services, parts) by entering them multiple times. However, in the web system, they want to enter a single job for a vehicle and then record the quantities of services and parts within that job.

There are two types of users who will utilize the system:
- Technicians: Main users who update customer jobs with parts and services.
- Office Administrators: Responsible for booking jobs, adding customers, services, parts, billing customers, and entering payments.

### Functional Requirements

#### Technician Interface:
- **Current Jobs**: Modify the current jobs page to display the customer’s name, rather than just the ID. This page should only show jobs that are not completed.

#### Administrator Interface:
- **Customer List**: Display a list of customers ordered by surname, then by first name.
- **Customer Search**: Allow searching for customers by first name or surname, allowing partial text matches. Results should be ordered appropriately.
- **Add Customer**: Add a new customer to the system (surname, phone number, and email address are required fields).
- **Add Service**: Add a new service to the system (name and cost are required).
- **Add Part**: Add a new part to the system (name and cost are required).
- **Schedule Job**: Select a customer and a date for the job to be booked. The date must be today or in the future. Only the date is required; a time on that day is not required.
- **Unpaid Bills & Pay Bills**: Display all unpaid bills in date then customer order, which can be filtered by customer. A bill can then be selected to be marked as paid by the Admin. Paid bills should not show on the list.
- **Billing History & Overdue Bills**: Generate a report showing all bills, with bills unpaid more than 14 days after the date of the job highlighted in red. The display should include the customer details, date of the job, and total cost of the job. Bills should be grouped by customer, and customers should be shown in last name, first name order. Bills should be shown with the oldest bill first.

#### Additional Notes
- The Admin features must not be visible in any of the technician interfaces, apart from the Admin link in the menu.
- Security features like password protection are not required for this assessment.

### Tech Stack

- Python
- Flask
- Html
- Bootstrap


## Web Application Structure

### Routes & Functions:
The web application follows a typical Model-View-Template (MVT) architecture where routes and functions serve as the controller, templates represent the view, and data handling and interactions with the database constitute the model.

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

### Templates:
- `currentjoblist.html`
- `job_details.html`
- `admin_customers.html`
- `add_customer.html`
- `add_service.html`
- `add_part.html`
- `schedule_job.html`
- `admin_bills.html`
- `billing_history.html`
- `components/navbar.html` (Handles navigations for Technician and Admin interface)


# Application Design Decisions Report

## Introduction
This report outlines the design decisions made during the development of the application. It discusses various design options considered and the rationale behind the chosen design. The report covers aspects such as routes, templates, navigation, data handling, layout, and additional functionalities implemented.

## Database Connection Management
A single function `getCursor()` is utilized to manage the database connection and cursor. This function ensures that only one database connection is established for each request and allows easy access to the database cursor throughout the application. Global variables are used to store the connection and cursor, ensuring their availability across different routes.

## Routes
The application defines several routes to handle different functionalities:
- `/`: Redirects to the `/currentjobs` route.
- `/currentjobs`: Displays a list of current jobs fetched from the database.
- `/job/<int:job_id>`: Displays the details of a specific job identified by its ID. Supports both GET and POST requests for updating job details.
- `/mark_as_complete/<int:job_id>`: Marks a job as complete when a POST request is received.
- `/admin`: Redirects to the admin section of the application.
- `/admin/customers`: Displays a list of customers fetched from the database. Supports searching for customers by name.
- `/admin/customers/add`: Allows adding new customers to the database.
- `/admin/service`: Allows adding new services to the database.
- `/admin/part`: Allows adding new parts to the database. It handles both GET and POST requests.
- `/admin/schedulejob`: Facilitates scheduling new jobs. It handles both GET and POST requests.
- `/admin/bills`: Displays a list of unpaid bills. It handles GET requests and supports searching for bills by customer name.
- `/admin/mark_as_paid`: Used to mark bills as paid. It handles GET requests.
- `/admin/billing_history`: Displays the billing history for each customer. It handles GET requests.

## Templates
Templates are used to render HTML pages dynamically. Each route renders a specific template to display data fetched from the database. Jinja2 templating engine is utilized to pass dynamic data from the backend to HTML templates.

## Navigation
Navigation within the application is primarily handled through hyperlinks and forms. Users can navigate between different sections of the application using links provided in the templates. Forms are used for adding new customers and services, as well as for performing actions like marking a job as complete.

## Data Handling
Data is primarily fetched from the database using SQL queries. POST requests are used for actions that modify data, such as marking a job as complete or adding new customers/services. Flash messages are used to provide feedback to users, such as error messages when input validation fails. Data passed between routes and templates is managed using Flask's request and session objects.

## Layout
The layout of each HTML page is designed to be user-friendly and intuitive. Bootstrap or other CSS frameworks could be used to enhance the visual appeal and responsiveness of the application.

## Conclusion
The design decisions outlined in this report aim to ensure the application is structured, maintainable, and user-friendly. The chosen approach provides a seamless user experience while efficiently handling data retrieval, manipulation, and presentation. The additional functionalities enhance the application's capabilities, allowing for efficient management of parts, job scheduling, bill tracking, and billing history visualization.
