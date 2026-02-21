# FleetFlow – Fleet & Logistics Management System

FleetFlow is a full-stack Fleet and Logistics Management System built using Django.  
It provides operational management, financial analytics, and role-based access control (RBAC) for modern fleet operations.

---

## Features

### Authentication & Security
- Django-based authentication system
- Secure session handling
- CSRF protection
- Role-Based Access Control (RBAC)

### Role Management
System supports four roles:
- Fleet Manager
- Dispatcher
- Safety Officer
- Financial Analyst

Access to financial and reporting modules is restricted based on user roles.

---

## Dashboard
The main dashboard provides real-time KPIs:
- Active fleet count
- Maintenance alerts
- Pending cargo
- Total revenue
- Total operational cost
- Total profit

All values are dynamically aggregated from the database.

---

## Trip Management
- Create and manage trips
- Assign drivers and vehicles
- Track trip status (Draft, Dispatched, etc.)
- Relational linking between trips, vehicles, and drivers

---

## Driver Management
- Maintain driver records
- Compliance tracking
- Role-based access control

---

## Maintenance Module
- Log maintenance records
- Track maintenance costs
- Maintenance data impacts operational cost calculations

---

## Fuel Management
- Record fuel logs
- Monthly fuel cost aggregation
- Integrated into financial analytics

---

## Financial Analytics
Automatically calculates:
- Total revenue
- Total operational cost
- Total profit
- Profit margin

Uses Django ORM aggregation functions for accurate backend calculations.

---

## Operational Reports
Integrated with Chart.js to visualize:
- Monthly revenue trends
- Monthly fuel cost trends
- Monthly maintenance cost trends
- Top 5 costliest vehicles

---

## Tech Stack

- Python 3
- Django 6
- SQLite
- HTML / CSS
- Chart.js
- Django ORM
- Django Authentication System

---

## Project Structure
```
    config/
    apps/
    accounts/ 
    workflow/ 
    dashboard/
    templates/
    static/
```

---

## Installation & Setup

### 1.Clone the Repository
```bash
git clone https://github.com/your-username/fleetflow.git
cd fleetflow
```

### 2.Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
### 3.Install Dependencies
```bash
pip install -r requirements.txt
```
### 4.Apply Migrations
```bash
python manage.py migrate
```
### 5.Create Superuser
```bash
python manage.py createsuperuser
```
### 6.Run server
```bash
python manage.py runserver
```
### visit
```
http://127.0.0.1:8000/login/
```