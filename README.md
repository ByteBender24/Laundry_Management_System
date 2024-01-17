
# Laundry Service Management System

## Overview

The Laundry Service Management System is a Web application developed for small-scale laundry service providers. It facilitates the management of customer details, bookings, machines, and financial transactions to streamline laundry service operations.

## Features

- **Login:**
  - Use the provided credentials to log in.
	  - Username: admin
	  - Password: 1234

- **Dashboard:**
  - View an interactive dashboard providing an overview of the laundry service.

- **Customer Management :**
  - Create, view, and update customer details.

- **Machine Management :**
  - View existing machines and create new machines.

- **Booking Management :**
  - Create, view, and update bookings.
  - Automatic allocation of clothes based on machine availability.

- **Payment Processing:**
  - Process customer payments.

- **Invoice Generation :**
  - Generate invoices after successful payment (optional).

- **Automatic Clothes Allocation :**
  - Automatically allocate clothes based on machine availability.

- **Machine Status Management :**
  - Change machine status manually or automatically.
  - Generate reports after changing machine status (optional).

- **Report Generation:**
  - Generate daily, monthly, and yearly reports.
  - 
## Static Files

-   **CSS:** Contains stylesheets for the application.
-   **img:** Holds images used in the application.
-   **js:** Includes JavaScript files for the application.
-   **reports:** Stores JSON files for generated reports.

## Templates

-   HTML templates for different views and functionalities.
## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/ByteBender24/Laundry_Management_System.git
   ```
2.  Navigate to the project directory:
    
    *``Make sure you activate virtual enviroment (using pipenv)``*
    
    ``cd <project_directory>``
    
3.  Install dependencies:
    
    `pip install -r requirements.txt` 
    
4.  Run the application:
    
    `python manage.py runserver` 
    
5.  Access the application in your web browser at http://localhost:8000.

## Contributing

If you would like to contribute to the development of this project, please follow the [Contribution Guidelines]()

## License

This project is licensed under the _[MIT License]()_.
   
