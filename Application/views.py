from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import *
from colorcode import Color, print_colored
import os

def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        with open(r'static\login.json', 'r') as f:
            data = json.load(f)
        if data.get('username') == username and data.get('password') == password:
            return render(request, 'home.html')
        message = "Incorrect Credentials!"
        return render(request, 'login.html', {'messages': message})

def main_page(request):
    return render(request, 'home.html')

def dashboard(request):
    with open(r'static\notifications.json', 'r') as f:
        data = json.load(f)
    print (data)
    if data != []:
        return render(request, 'dashboard.html', {'messages' : data})
    else:
        return render(request, 'dashboard.html')



def about(request):
    return render(request, 'about.html')


def create_customer(request):
    if request.method == "GET":
        return render(request, 'create_customer.html')
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone_number')
        email = request.POST.get('email')
        customer_type = request.POST.get('customer_type')

        if not validate_phone_number(phone):
            context = {'customer_msg': "Invalid phone number"}
            return render(request, 'create_customer.html', context)

        if not validate_email(email):
            context = {'customer_msg': "Invalid email address"}
            return render(request, 'create_customer.html', context)

        # Usage of Factory Pattern
        if customer_type == 'basic':
            factory = BasicCustomerFactory()
        elif customer_type == 'premium':
            factory = PremiumCustomerFactory()
        else:
            context = {'customer_msg': "Invalid customer type"}
            return render(request, 'create_customer.html', context)

        # Use the factory to create the customer
        new_customer = factory.create_customer(name, phone, email)
        try:
            with open('static\customers.json', 'r') as file:
                customers = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            customers = []

        customers.append(new_customer)

        with open('static\customers.json', 'w') as file:
            json.dump(customers, file, indent=2)

        context = {'customer_msg': "Customer created Successfully!"}
        return render(request, 'dashboard.html', context)


def customer_list(request):

    if request.method == "GET":
        with open('static\customers.json', 'r') as file:
            customers = json.load(file)
        customer_msg = request.session.get('customer_msg')
        return render(request, 'view_customer.html', {'customers': customers, 'customer_msg': customer_msg})
    if request.method == "POST":
        with open('static\customers.json', 'r') as file:
            customers = json.load(file)


def update_customer_details(request, customer_id):
    try:
        with open('static\customers.json', 'r') as file:
            customers = json.load(file)

        customer_data = next(
            (customer for customer in customers if customer['id'] == customer_id), None)

        if not customer_data:
            request.session['customer_msg'] = "Customer not found"
            return render(request, 'dashboard.html', {'customer_msg': "Customer not found"})

        if request.method == "POST":
            update_data = {
                'name': request.POST.get('name'),
                'phone_number': request.POST.get('phone_number'),
                'email': request.POST.get('email'),
                'status': request.POST.get('status'),
            }

            updater = CustomerUpdater()
            updater.add_command(UpdateNameCommand(customer_data['name']))
            updater.add_command(UpdatePhoneCommand(
                customer_data['phone_number']))
            updater.add_command(UpdateEmailCommand(customer_data['email']))
            updater.add_command(UpdateStatusCommand(customer_data['status']))

            try:
                # Execute the commands
                updater.execute_commands(customer_data, update_data)

                # Find the index of the customer_data in the list
                index = next((index for index, customer in enumerate(
                    customers) if customer['id'] == customer_id), None)

                if index is not None:
                    # Update the customer data in the list
                    customers[index] = customer_data

                    with open('static\customers.json', 'w') as file:
                        json.dump(customers, file, indent=2)

                    context = {
                        'customer_msg': "Customer updated Successfully!"}
                    return redirect('customer_list')

                else:
                    context = {
                        'customer_msg': "Error updating customer details"}
                    return redirect('customer_list')

            except Exception as e:
                print(f"Error updating customer: {e}")

                # Undo the commands in case of an error
                updater.undo_commands(customer_data, update_data)

                context = {'customer_msg': "Error updating customer details"}

                return redirect('customer_list')

        else:
            context = {'customer_data': customer_data}
            return render(request, 'update_customer_details.html', context)

    except FileNotFoundError:
        context = {'customer_msg': "Customer data file not found"}
        return redirect('customer_list')

    except json.JSONDecodeError:
        context = {'customer_msg': "Error decoding customer data file"}
        return redirect('customer_list')

# -------------------------------------REGARDING MACHINES-----------------------------------------------


def machine_list(request):
    machine_manager = MachineManager()
    machines = machine_manager.get_machines()
    return render(request, 'view_machines.html', {'machines': machines})


def create_machine(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        capacity = int(request.POST.get('capacity'))
        machine_type = request.POST.get('machine_type')

        machine_factory = MachineFactory()
        machine = machine_factory.create_machine(name, capacity, machine_type)

        machine_manager = MachineManager()
        machine_manager.add_machine(machine)
        machine_manager._save_machines()
        print_colored(machine_manager.get_free_machines())

        return redirect('machine_list')

    return render(request, 'create_machine.html')


def view_machine(request, machine_id):
    machine_manager = MachineManager()
    machines = machine_manager.get_machines()

    # Find the machine with the given machine_id
    machine = next(
        (machine for machine in machines if machine['machine_id'] == machine_id), None)

    if machine:
        # Prepare the data for JSON response
        machine_data = {
            'name': machine['name'],
            'capacity': machine['capacity'],
            'is_used': machine['is_used'],
            'type': machine['type'],
            'machine_id': machine['machine_id'],
        }

        return JsonResponse({'machine': machine_data})
    else:
        # Machine not found
        return JsonResponse({'error': 'Machine not found'}, status=404)

# -------------------------------------REGARDING BOOKINGS-----------------------------------------------


def create_booking(request):
    price_data = price_list_return()
    machine_manager = MachineManager()
    free_num_machines = machine_manager.get_num_free_machines()
    free_machines = machine_manager.get_free_machines()

    booking_manager = BookingManager()
    bookings = booking_manager.get_bookings()
    today = datetime.now().date().strftime('%d/%m/%Y')

    context = {'price_data': price_data, 'free_machines': free_num_machines, 'today' : today}

    if request.method == 'POST':
        # Extract data from form submission
        customer_id = request.POST.get('customer_id')
        dry_quantity = int(request.POST.get('dry_quantity', 0))
        clothes_quantity = int(request.POST.get('clothes_quantity', 0))
        shoes_quantity = int(request.POST.get('shoes_quantity', 0))
        bags_quantity = int(request.POST.get('bags_quantity', 0))

        # Validate customer_id
        if not is_valid_customer_id(customer_id):
            return JsonResponse({'success': False, 'message': 'Invalid customer ID'})

        # Generate booking ID
        booking_id = generate_booking_id(customer_id)

        customer = get_customer_by_id(customer_id)
        if customer['status'].lower() == 'premium':
            payment_method_strategy = DiscountDecorator(
                PremiumPaymentStrategy(), discount_percentage=0)
        else:
            payment_method_strategy = DiscountDecorator(
                BasicPaymentStrategy(), discount_percentage=0)

        booking = Booking(
            booking_id, customer_id, dry_quantity, clothes_quantity, shoes_quantity, bags_quantity, total_cost=0,
            payment_status=False, payment_method_strategy=payment_method_strategy
        )

        # Calculate total cost
        booking.total_cost = booking.payment_method_strategy.calculate_total_cost(
            booking, price_data.get('price_rates'))

        # Confirm payment if selected
        if request.POST.get('confirm_payment') == 'on':
            booking.confirm_payment()

        # Add booking to BookingManager
        booking_manager = BookingManager()
        booking_manager.add_booking(booking)

        # Update machine status based on the booking
        # Update dry_cleaning machine status
        if dry_quantity > 0:
            dry_cleaning_machine_id = get_first_available_machine(
                free_machines['dry_cleaning_free'])
            machine_manager.change_machine_status(
                dry_cleaning_machine_id, booking_id)

        # Update normal cleaning machine status
        if clothes_quantity > 0:
            normal_cleaning_machine_id = get_first_available_machine(
                free_machines['normal_cleaning_free'])
            machine_manager.change_machine_status(
                normal_cleaning_machine_id, booking_id)

        return render(request, 'view_bookings.html', {'bookings': bookings})

    return render(request, 'create_booking.html', context)



def view_bookings(request):
    booking_manager = BookingManager()
    bookings = booking_manager.get_bookings()
    machine_manager = MachineManager()
    print_colored(machine_manager.get_free_machines())

    request.session['invoice_print'] = True
    return render(request, 'view_bookings.html', {'bookings': bookings})


def update_booking(request, booking_id):
    booking_manager = BookingManager()
    booking = booking_manager.get_booking_by_id(booking_id)

    if request.method == 'POST':
        # Extract updated data from the form submission
        updated_dry_quantity = int(request.POST.get('dry_quantity'))
        updated_clothes_quantity = int(request.POST.get('clothes_quantity'))
        updated_shoes_quantity = int(request.POST.get('shoes_quantity'))
        updated_bags_quantity = int(request.POST.get('bags_quantity'))

        # Update the booking with the new quantities
        booking['dry_quantity'] = updated_dry_quantity
        booking['clothes_quantity'] = updated_clothes_quantity
        booking['shoes_quantity'] = updated_shoes_quantity
        booking['bags_quantity'] = updated_bags_quantity

        # Recalculate total cost based on the updated quantities
        price_data = price_list_return()
        booking['total_cost'] = booking_manager.payment_method_strategy.calculate_total_cost(
            booking, price_data.get('price_rates'))

        # Confirm payment if selected
        if request.POST.get('confirm_payment') == 'on':
            booking.confirm_payment()

        # Update the booking in the booking manager
        booking_manager.update_booking(booking_id, booking)

        return redirect('view_bookings')

    return render(request, 'update_booking.html', {'booking': booking})

#------------------------------------------------------Payment-------------------------------------------------------------

def payment_portal(request, booking_id):
    booking_manager = BookingManager()

    if request.method == "GET":
        booking = booking_manager.get_booking_by_id(booking_id)
        if not booking:
            return JsonResponse({'success': False, 'message': 'Booking not found'})
        customer_id = booking['customer_id']
        with open('static\pricelist.json', 'r') as file:
            price_list = json.load(file)
        price_list = price_list["price_rates"]
        with open('static\customers.json', 'r') as file:
            customers = json.load(file)
        for cust in customers:
            print(cust['id'], customer_id)
            if cust['id'] == customer_id:
                booking_cust = cust

        totals = {
            "dry_cleaning": booking["dry_quantity"] * price_list["dry_cleaning"],
            "clothes": booking["clothes_quantity"] * price_list["clothes"],
            "shoes": booking["shoes_quantity"] * price_list["shoes"],
            "bags": booking["bags_quantity"] * price_list["bags"]
        }
        subtotal = sum(totals.values())
        invoice_id = generate_invoice_id(booking_id, customer_id)
        invoice_date = todate()

        invoice_print = request.session.get('invoice_print')
        return render(request, 'payment_portal.html', {'booking': booking, 'customer' : booking_cust, 'price_list' : price_list, 'totals' : totals, 'subtotal':subtotal, 'invoice_date' : invoice_date, 'invoice_number' : invoice_id, 'invoice_print' : invoice_print})

    elif request.method == "POST":
        # Extract data from the form submission
        payment_method = request.POST.get('payment_method')
        print_colored(request.POST , color=Color.RED)
        discount = request.POST.get('discount')
        # Retrieve the booking from the booking manager
        booking = booking_manager.get_booking_by_id(booking_id)

        if not booking:
            return JsonResponse({'success': False, 'message': 'Booking not found'})

        # Set payment method strategy based on form input
        if payment_method == 'premium':
            booking.payment_method_strategy = PremiumPaymentStrategy()
        else:
            booking.payment_method_strategy = BasicPaymentStrategy()

        # Calculate total cost
        price_data = price_list_return()
        booking.total_cost = booking.payment_method_strategy.calculate_total_cost(
            booking, price_data.get('price_rates'))

        # Confirm payment if selected
        if request.POST.get('confirm_payment') == 'on':
            booking.confirm_payment()

        # Update the booking in the booking manager
        booking_manager.update_booking(booking_id)

        return JsonResponse({'success': True, 'message': 'in post of payment portal'})

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


def handle_payment(request, booking_id):
    # Get the booking manager and booking details
    booking_manager = BookingManager()
    booking = booking_manager.get_booking_by_id(booking_id)
    bookings = booking_manager.get_bookings()
    discount = int(request.POST.get('discount'))
    print_colored(request.POST , color=Color.RED)

    if not booking:
        return render({'success': False, 'message': 'Booking not found'})

    # Check if the payment is already confirmed
    if booking['payment_status']:
        return render(request, 'view_bookings.html', {'bookings': bookings, 'message': 'Payment already confirmed'})

    # Get the customer details
    customer_id = booking['customer_id']
    customer = get_customer_by_id(customer_id)

    # Apply discount based on customer status
    if customer['status'].lower() == 'premium':
        payment_method_strategy = DiscountDecorator(
            PremiumPaymentStrategy(), discount_percentage=discount)
    else:
        payment_method_strategy = DiscountDecorator(
            BasicPaymentStrategy(), discount_percentage=discount)

    # Confirm the payment
    booking['payment_status'] = True
    print_colored(payment_method_strategy.calculate_total_cost(
        booking, price_list_return().get('price_rates')), color=Color.GREEN)
    booking['total_cost'] = payment_method_strategy.calculate_total_cost(
        booking, price_list_return().get('price_rates'))
    print_colored(booking)
    # Save the updated booking details
    booking_manager.update_booking(booking_id, booking)

    # Update machine status based on the booking
    machine_manager = MachineManager()

    # Update dry_cleaning machine status
    print_colored(booking, color=Color.BLUE)
    if booking['dry_quantity'] > 0:
        dry_cleaning_machine_id = get_first_available_machine(
            machine_manager.get_used_machines()['dry_cleaning_used'])
        print_colored(dry_cleaning_machine_id)
        machine_manager.change_machine_status(
            dry_cleaning_machine_id, booking_id)

    # Update normal cleaning machine status
    if booking['clothes_quantity'] > 0:
        normal_cleaning_machine_id = get_first_available_machine(
            machine_manager.get_used_machines()['normal_cleaning_used'])

        machine_manager.change_machine_status(
            normal_cleaning_machine_id, booking_id)

    print_colored(machine_manager.get_free_machines())
    # Return success response
    return render(request, 'view_bookings.html', {'bookings': bookings, 'message': 'Payment Successfully confirmed'})


def invoice_printer(request, booking_id):
    request.session['invoice_print'] = False
    booking_manager = BookingManager()
    if request.method == "GET":
        booking = booking_manager.get_booking_by_id(booking_id)
        if not booking:
            return JsonResponse({'success': False, 'message': 'Booking not found'})
        customer_id = booking['customer_id']
        with open('static\pricelist.json', 'r') as file:
            price_list = json.load(file)
        price_list = price_list["price_rates"]
        with open('static\customers.json', 'r') as file:
            customers = json.load(file)
        for cust in customers:
            print(cust['id'], customer_id)
            if cust['id'] == customer_id:
                booking_cust = cust

        totals = {
            "dry_cleaning": booking["dry_quantity"] * price_list["dry_cleaning"],
            "clothes": booking["clothes_quantity"] * price_list["clothes"],
            "shoes": booking["shoes_quantity"] * price_list["shoes"],
            "bags": booking["bags_quantity"] * price_list["bags"]
        }
        subtotal = sum(totals.values())
        invoice_id = generate_invoice_id(booking_id, customer_id)
        invoice_date = todate()

        invoice_print = request.session.get('invoice_print')
        return render(request, 'payment_portal.html', {'booking': booking, 'customer': booking_cust, 'price_list': price_list, 'totals': totals, 'subtotal': subtotal, 'invoice_date': invoice_date, 'invoice_number': invoice_id, 'invoice_print': invoice_print})
    return render(request, 'payment_portal.html', {'booking': booking, 'customer': booking_cust, 'price_list': price_list, 'totals': totals, 'subtotal': subtotal, 'invoice_date': invoice_date, 'invoice_number': invoice_id, 'invoice_print': invoice_print})

# ----------------------------------------------------------------Report Generation-------------------------------------------------------


def save_report_to_json(report_data):
    # Create a directory if it doesn't exist
    os.makedirs('static/reports', exist_ok=True)

    # Generate a unique filename based on the current timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'static/reports/report_{timestamp}.json'

    # Save the report data to the JSON file
    with open(filename, 'w') as report_json:
        json.dump(report_data, report_json, indent=2)

def generate_reports(request):

    json_file_path = 'static/bookings.json'
    with open(json_file_path, 'r') as booking_json:
        bookings = json.load(booking_json)
    
    report_type = request.POST.get('report_type', None)
    print_colored(request.POST)
    strategy = DailyReport() #default
    if report_type == 'daily':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        report_context = ReportContext(strategy)
        report_data, complete_booking_report_data = report_context.generate_report_data(
            bookings, start_date, end_date)
        
    elif report_type == 'monthly':

        selected_month = request.POST.get('selected_month', None)

        strategy = MonthlyReport()
        month = selected_month
        print_colored(month, color=Color.GREEN)
        report_context = ReportContext(strategy)
        report_data, complete_booking_report_data = report_context.generate_report_data(
            bookings, month)
    elif report_type == 'yearly':
 
        selected_year = request.POST.get('selected_year', None)
     
        strategy = YearlyReport()
        year = selected_year
        report_context = ReportContext(strategy)
        report_data, complete_booking_report_data = report_context.generate_report_data(
            bookings, year)
    else:
        start_date = None
        end_date = None
        report_context = ReportContext(strategy)
        report_data, complete_booking_report_data = report_context.generate_report_data(
            bookings, start_date, end_date)

    print_colored(report_data, color=Color.RED)
    save_report_to_json(complete_booking_report_data)
    return render(request, 'reports.html', {'report_data': report_data})
    
    
