"""
URL configuration for Laundry_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login , name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('customer_list/', views.customer_list, name='customer_list'),
    path('generate_reports/', views.generate_reports, name='generate_reports'),
    path('machine_list/', views.machine_list, name='machine_list'),
    path('create_customer/', views.create_customer, name='create_customer'),
    path('view_bookings/', views.view_bookings, name='view_bookings'),
    path('about', views.about, name='about'),
    path('update_customer_details/<str:customer_id>/', views.update_customer_details, name='update_customer_details'),
    path('create_machine/', views.create_machine, name='create_machine'),
    path('machine_details/<str:machine_id>/', views.view_machine, name='view_machine'),
    path('create_booking/', views.create_booking, name="create_booking"),
    path('update_booking/<str:booking_id>', views.update_booking, name='update_booking'),
    path('payment_portal/<str:booking_id>', views.payment_portal, name="payment_portal"),
    path('handle_payment/<str:booking_id>',views.handle_payment, name="handle_payment"),
    path('invoice/<str:booking_id>', views.invoice_printer, name="invoice"),
]
