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