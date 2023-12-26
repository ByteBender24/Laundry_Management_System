from datetime import datetime, timedelta
from django.db import models
from abc import ABC, abstractmethod
from django.core.serializers.json import DjangoJSONEncoder
import re
import random
import json
import string
from colorcode import Color, print_colored

def generate_customer_code(name, phone_number):
    name_prefix = re.sub(r'[^a-zA-Z]', '', name)[:3].upper()
    random_three_digits = str(random.randint(100, 999))
    last_three_digits = re.sub(r'[^0-9]', '', phone_number)[-3:]
    customer_code = f"{name_prefix}{random_three_digits}{last_three_digits}"

    return customer_code


def free_machines():
    
    with open(r'static\machines.json', 'r') as machine_list:
        machine_list_data = json.load(machine_list)

    dry_free = normal_free = 0

    for data in machine_list_data:
        if data['type'] == "dry_cleaning" and data['is_used'] == True:
            dry_free += 1
        if data['type'] == "normal" and data['is_used'] == True:
            normal_free += 1

    free_machines_data = {
        "dry_free": dry_free,
        "normal_free": normal_free
    }

    with open(r'static\free_machines.json', 'w') as free_machines:
        json.dump(free_machines_data, free_machines)

    with open(r'static\free_machines.json', 'r') as free_machines:
        free_machines_data = json.load(free_machines)

    return free_machines_data

def is_valid_customer_id(customer_id):
    pattern = re.compile(r'^[A-Z]{3}\d{3}\d{3}$')
    return bool(re.match(pattern, customer_id))

def validate_phone_number(phone_number):
    phone_pattern = re.compile(r'^\d{10}$')
    return bool(re.match(phone_pattern, phone_number))


def validate_email(email):
    email_pattern = re.compile(
        r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return bool(re.match(email_pattern, email))


def generate_booking_id(customer_id):
    first_two_digits = str(customer_id)[:2]

    random_digits = str(random.randint(1000, 9999))

    booking_id = f"{first_two_digits}{random_digits}"

    return booking_id


def price_list_return():
    with open(r'static\pricelist.json', 'r') as price_file:
        price_data = json.load(price_file)
    return price_data


def get_first_available_machine(machine_list):
    if machine_list:
        return machine_list[0]
    return None

def get_customer_by_id(customer_id):
    with open(r'static\customers.json', 'r') as f:
        customers = json.load(f)
    for cust in customers:
        if cust['id'] == customer_id:
            return cust
"""
FACTORY METHOD DESIGN PATTERN (DP)
"""


class CustomerFactory(ABC):
    @abstractmethod
    def create_customer(self, name, phone, email):
        pass


class BasicCustomerFactory(CustomerFactory):
    def create_customer(self, name, phone, email):
        id = generate_customer_code(name, phone)
        return {'id': id,
                'name': name,
                'phone_number': phone,
                'email': email,
                'status': "BASIC"}


class PremiumCustomerFactory(CustomerFactory):
    def create_customer(self, name, phone, email):
        id = generate_customer_code(name, phone)
        return {'id': id,
                'name': name,
                'phone_number': phone,
                'email': email,
                'status': "PREMIUM"}


"""
COMMAND DESIGN PATTERN (DP)
"""


class Command(ABC):
    @abstractmethod
    def execute(self, customer_data, data):
        pass

    @abstractmethod
    def undo(self, customer_data, data):
        pass


class UpdateNameCommand(Command):
    def __init__(self, original_name):
        self.original_name = original_name

    def execute(self, customer_data, data):
        self.original_name = customer_data['name']
        customer_data['name'] = data['name']

    def undo(self, customer_data, data):
        customer_data['name'] = self.original_name


class UpdatePhoneCommand(Command):
    def __init__(self, original_phone):
        self.original_phone = original_phone

    def execute(self, customer_data, data):
        self.original_phone = customer_data['phone_number']
        customer_data['phone_number'] = data['phone_number']

    def undo(self, customer_data, data):
        customer_data['phone_number'] = self.original_phone


class UpdateEmailCommand(Command):
    def __init__(self, original_email):
        self.original_email = original_email

    def execute(self, customer_data, data):
        self.original_email = customer_data['email']
        customer_data['email'] = data['email']

    def undo(self, customer_data, data):
        customer_data['email'] = self.original_email


class UpdateStatusCommand:
    def __init__(self, old_status):
        self.old_status = old_status

    def execute(self, customer_data, update_data):
        customer_data['status'] = update_data['status']

    def undo(self, customer_data, update_data):
        customer_data['status'] = self.old_status


class CustomerUpdater:
    def __init__(self):
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    def execute_commands(self, customer_data, data):
        for command in self.commands:
            command.execute(customer_data, data)

    def undo_commands(self, customer_data, data):
        for command in reversed(self.commands):
            command.undo(customer_data, data)


"""
SINGLETON DESIGN PATTERN (DP) &&&&&
OBSERVER DESIGN PATTERN (DP)
"""


class MachineManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(MachineManager, cls).__new__(cls)
            cls._instance.machines = cls._instance._load_machines()
            cls._instance.observers = []
        return cls._instance

    def add_machine(self, machine):
        self.machines[machine.machine_id] = machine.to_json()
        self._save_machines()

    def get_machines(self):
        return list(self.machines.values())

    def get_used_machines(self):
        used_machines = [
            machine for machine in self.machines.values() if machine['is_used']]
        return used_machines

    def _load_machines(self):
        try:
            with open('static/machines.json', 'r') as file:
                machines_data = json.load(file)
            return {machine['machine_id']: machine for machine in machines_data}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_machines(self):
        with open('static/machines.json', 'w') as file:
            machines_data = list(self.machines.values())
            json.dump(machines_data, file, cls=DjangoJSONEncoder, indent=2)

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, machine_id, is_used):
        for observer in self.observers:
            observer.update_notification(machine_id, is_used)

    def change_machine_status(self, machine_id, booking_id):
        if machine_id in self.machines:
            is_used_tf = self.machines[machine_id]['is_used']
            self.machines[machine_id]['is_used'] = not(is_used_tf) if is_used_tf is not False else booking_id
            is_used_tf = self.machines[machine_id]['is_used']
            self._save_machines()
            self.notify_observers(machine_id, is_used_tf)

    def get_free_machines(self):
        free_machines = {
            'dry_cleaning_free': [],
            'normal_cleaning_free': [],
        }

        for machine in self.machines.values():
            if not machine['is_used']:
                if machine['type'] == 'dry_cleaning':
                    free_machines['dry_cleaning_free'].append(machine['machine_id'])
                elif machine['type'] == 'normal':
                    free_machines['normal_cleaning_free'].append(machine['machine_id'])

        num = {"dry_cleaning_free": len(free_machines['dry_cleaning_free']),
               "normal_cleaning_free": len(free_machines['normal_cleaning_free'])}
        with open('static/free_machines.json', 'w') as f:
            json.dump(num, f)
        return free_machines
    
    

    def get_used_machines(self):
        used_machines = {
            'dry_cleaning_used': [],
            'normal_cleaning_used': [],
        }

        for machine in self.machines.values():
            if machine['is_used']:
                if machine['type'] == 'dry_cleaning':
                    used_machines['dry_cleaning_used'].append(machine['machine_id'])
                elif machine['type'] == 'normal':
                    used_machines['normal_cleaning_used'].append(machine['machine_id'])

        return used_machines

    def get_num_free_machines(self):
        with open('static/free_machines.json', 'r') as f:
            num_machines = json.load(f)
        return num_machines
    
    # TODO does it automatically update notifications, when is_used is changed

class NotificationObserver(ABC):
    @abstractmethod
    def update_notification(self, machine_id, is_used):
        pass


class NotificationBar(NotificationObserver):
    def __init__(self):
        self.notifications = []
        try:
            with open('static/notifications.json', 'r') as file:
                self.notifications = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.notifications = []

    def update_notification(self, machine_id, is_used):
        notification = f"Machine ID {machine_id} is {'free' if is_used else 'not free'}"
        self.notifications.append(notification)
        self._save_notifications()

    def get_notifications(self):
        return self.notifications

    def clear_notifications(self):
        self.notifications = []
        self._save_notifications()

    def _load_notifications(self):
        try:
            with open('static/notifications.json', 'r') as file:
                self.notifications = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.notifications = []

    def _save_notifications(self):
        with open('static/notifications.json', 'w') as file:
            json.dump(self.notifications, file, indent=2)


"""
FACTORY METHOD DESIGN PATTERN (DP)
"""


class Machine:
    def __init__(self, name, capacity, is_used, machine_id):
        self.name = name
        self.capacity = capacity
        self.is_used = is_used
        self.machine_id = machine_id


class DryCleaningMachine(Machine):
    def __init__(self, name, capacity, is_used, machine_id):
        super().__init__(name, capacity, is_used, machine_id)
        self.type = "dry_cleaning"
    
    def to_json(self):
        return {
            'name' : self.name,
            'capacity' : self.capacity,
            'is_used' : self.is_used,
            'machine_id' : self.machine_id,
            'type': self.type
        }


class NormalMachine(Machine):
    def __init__(self, name, capacity, is_used, machine_id):
        super().__init__(name, capacity, is_used, machine_id)
        self.type = "normal"

    def to_json(self):
        return {
            'name' : self.name,
            'capacity' : self.capacity,
            'is_used' : self.is_used,
            'machine_id' : self.machine_id,
            'type' : self.type
        }
    
class MachineFactory:
    def __init__(self):
        self.machine_manager = MachineManager()

    def create_machine(self, name, capacity, machine_type):
        machine_id = self.generate_machine_id(machine_type)
        if machine_type == 'dry_cleaning':
            machine = DryCleaningMachine(
                name, capacity, is_used=False, machine_id=machine_id)
        elif machine_type == 'normal':
            machine = NormalMachine(
                name, capacity, is_used=False, machine_id=machine_id)
        else:
            raise ValueError(f"Invalid machine type: {machine_type}")

        return machine

    def generate_machine_id(self, machine_type):
        prefix = machine_type.upper()
        random_suffix = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=3))
        return f"{prefix}_{random_suffix}"

"""
STATE DESIGN PATTERN (DP)
"""

class PaymentStatusState:
    def confirm_payment(self, booking):
        raise NotImplementedError()

    def cancel_payment(self, booking):
        raise NotImplementedError()


class PendingPaymentState(PaymentStatusState):
    def confirm_payment(self, booking):
        booking.payment_status = True
        return ConfirmedPaymentState()

    def cancel_payment(self, booking):
        return self


class ConfirmedPaymentState(PaymentStatusState):
    def confirm_payment(self, booking):
        return self

    def cancel_payment(self, booking):
        booking.payment_status = False
        return PendingPaymentState()

"""
STRATEGY DESIGN PATTERN (DP)
"""

class PaymentMethodStrategy:
    def calculate_total_cost(self, booking, price_rates):
        raise NotImplementedError()


class BasicPaymentStrategy(PaymentMethodStrategy):
    def calculate_total_cost(self, booking, price_rates):
        if isinstance(booking, dict):
            cost = (booking['dry_quantity'] * price_rates['dry_cleaning'] +
                    booking['clothes_quantity'] * price_rates['clothes'] +
                    booking['shoes_quantity'] * price_rates['shoes'] +
                    booking['bags_quantity'] * price_rates['bags'])
            return cost
        else:
            # Assuming booking is an object with attributes like dry_quantity, clothes_quantity, etc.
            cost = (booking.dry_quantity * price_rates['dry_cleaning'] +
                    booking.clothes_quantity * price_rates['clothes'] +
                    booking.shoes_quantity * price_rates['shoes'] +
                    booking.bags_quantity * price_rates['bags'])
            return cost


class PremiumPaymentStrategy(PaymentMethodStrategy):
    def calculate_total_cost(self, booking, price_rates):
        if isinstance(booking, dict):
            cost = 0.9 * (booking['dry_quantity'] * price_rates['dry_cleaning'] +
                          booking['clothes_quantity'] * price_rates['clothes'] +
                          booking['shoes_quantity'] * price_rates['shoes'] +
                          booking['bags_quantity'] * price_rates['bags'])
            return cost
        else:
            # Assuming booking is an object with attributes like dry_quantity, clothes_quantity, etc.
            cost = 0.9 * (booking.dry_quantity * price_rates['dry_cleaning'] +
                          booking.clothes_quantity * price_rates['clothes'] +
                          booking.shoes_quantity * price_rates['shoes'] +
                          booking.bags_quantity * price_rates['bags'])
            return cost


"""
DECORATOR PATTERN
"""


class DiscountDecorator(PaymentMethodStrategy):
    def __init__(self, decorated_strategy, discount_percentage):
        self.decorated_strategy = decorated_strategy
        self.discount_percentage = discount_percentage / 100

    def calculate_total_cost(self, booking, price_rates):
        base_cost = self.decorated_strategy.calculate_total_cost(
            booking, price_rates)
        return base_cost * (1 - self.discount_percentage)

    

"""
SINGLETON PATTERN
ITERATOR PATTERN
COMMAND PATTERN
"""


class Booking:
    def __init__(self, booking_id, customer_id, dry_quantity=0, clothes_quantity=0, shoes_quantity=0, bags_quantity=0, total_cost=0, payment_status=False, payment_method_strategy=None):
        self.booking_id = booking_id
        self.customer_id = customer_id
        self.dry_quantity = dry_quantity
        self.clothes_quantity = clothes_quantity
        self.shoes_quantity = shoes_quantity
        self.bags_quantity = bags_quantity
        self.total_cost = total_cost
        self.payment_status = payment_status
        self.payment_status_state = PendingPaymentState()  # Initial state
        self.booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Store the payment method strategy
        self.payment_method_strategy = DiscountDecorator(
            payment_method_strategy, discount_percentage=0)

    def confirm_payment(self):
        self.payment_status_state = self.payment_status_state.confirm_payment(
            self)

    def cancel_payment(self):
        self.payment_status_state = self.payment_status_state.cancel_payment(
            self)

    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'customer_id': self.customer_id,
            'dry_quantity': self.dry_quantity,
            'clothes_quantity': self.clothes_quantity,
            'shoes_quantity': self.shoes_quantity,
            'bags_quantity': self.bags_quantity,
            'total_cost': self.total_cost,
            'payment_status': self.payment_status,
            'booking_time': self.booking_time
        }


class BookingManager:
    _instance = None
    bookings = []

    def __new__(cls, total_cost_strategy=None, payment_method_strategy=None):
        if cls._instance is None:
            cls._instance = super(BookingManager, cls).__new__(cls)
            cls._instance.bookings = cls._instance._load_bookings()
            cls._instance.total_cost_strategy = total_cost_strategy or BasicPaymentStrategy()
            cls._instance.payment_method_strategy = payment_method_strategy or BasicPaymentStrategy()
        return cls._instance

    def add_booking(self, booking):
        self.bookings.append(booking.to_dict())
        self._save_bookings()

    def get_bookings(self):
        return self.bookings

    def get_booking_by_id(self, booking_id):
        for booking in self.bookings:
            if booking['booking_id'] == booking_id:
                return booking
        return None

    def update_booking(self, booking_id, new_booking):
        for i, booking in enumerate(self.bookings):
            if booking['booking_id'] == booking_id:
                self.bookings[i] = new_booking
                break
        self._save_bookings()

    def undo_last_booking(self):
        if self.bookings:
            last_booking = self.bookings.pop()
            self._save_bookings()
            return last_booking
        return None

    def _load_bookings(self):
        try:
            with open(r'static\bookings.json', 'r') as booking_json:
                return json.load(booking_json)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_bookings(self):
        with open(r'static\bookings.json', 'w') as booking_json:
            json.dump(self.bookings, booking_json, indent=4)

    # Iterator pattern
    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.bookings):
            result = self.bookings[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration

"""
STRATEGY PATTERN
"""


class ReportGeneratorStrategy:
    def generate_report_data(self, bookings):
        raise NotImplementedError(
            "Subclasses must implement generate_report_data")


class DailyReportGenerator(ReportGeneratorStrategy):
    def generate_report_data(self, bookings, start_date=None, end_date=None):
        today = datetime.now().date()
        if start_date is None:
            start_date = today
        if end_date is None:
            end_date = today

        # Convert dates to strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        filtered_bookings = [booking for booking in bookings if start_date <= datetime.strptime(
            booking['booking_time'], '%Y-%m-%d %H:%M:%S').date() <= end_date]

        total_bookings = len(filtered_bookings)
        total_cost = sum(booking['total_cost']
                         for booking in filtered_bookings)

        return {
            'report_type': 'Daily',
            'start_date': start_date_str,
            'end_date': end_date_str,
            'total_bookings': total_bookings,
            'total_cost': total_cost,
        }


class MonthlyReportGenerator(ReportGeneratorStrategy):
    def generate_report_data(self, bookings, start_date=None, end_date=None):
        today = datetime.now().date()

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m').date()
        else:
            start_date = today.replace(day=1)

        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m').date()
        else:
            end_date = (start_date + timedelta(days=32)
                        ).replace(day=1) - timedelta(days=1)

        # Convert dates to strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        filtered_bookings = [booking for booking in bookings if start_date <= datetime.strptime(
            booking['booking_time'], '%Y-%m-%d %H:%M:%S').date() <= end_date]

        total_bookings = len(filtered_bookings)
        total_cost = sum(booking['total_cost']
                         for booking in filtered_bookings)

        return {
            'report_type': 'Monthly',
            'start_date': start_date_str,
            'end_date': end_date_str,
            'total_bookings': total_bookings,
            'total_cost': total_cost,
        }


class YearlyReportGenerator(ReportGeneratorStrategy):
    def generate_report_data(self, bookings, start_date=None, end_date=None):
        today = datetime.now().date()

        if start_date:
            start_date = datetime.strptime(start_date, '%Y').date()
        else:
            start_date = today.replace(month=1, day=1)

        if end_date:
            end_date = datetime.strptime(end_date, '%Y').date()
        else:
            end_date = today.replace(month=12, day=31)

        # Convert dates to strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        filtered_bookings = [booking for booking in bookings if start_date <= datetime.strptime(
            booking['booking_time'], '%Y-%m-%d %H:%M:%S').date() <= end_date]

        total_bookings = len(filtered_bookings)
        total_cost = sum(booking['total_cost']
                         for booking in filtered_bookings)

        return {
            'report_type': 'Yearly',
            'start_date': start_date_str,
            'end_date': end_date_str,
            'total_bookings': total_bookings,
            'total_cost': total_cost,
        }

# context class that will use the strategy
class ReportContext:
    def __init__(self, strategy):
        self.strategy = strategy

    def generate_report_data(self, bookings, **kwargs):
        return self.strategy.generate_report_data(bookings, **kwargs)


