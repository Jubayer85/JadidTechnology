# myshop/utils.py

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User

def send_order_notification_to_admin(order):
    """Send order notification email to admin"""
    subject = f'🛒 New Order Received - #{order.order_number}'
    
    # Email context
    context = {
        'order': order,
        'order_items': order.items.all(),
        'site_name': 'Jadid Technology',
        'site_url': 'http://127.0.0.1:8000',
        'admin_url': f'http://127.0.0.1:8000/admin/myshop/order/{order.id}/change/',
    }
    
    # Render HTML template
    html_message = render_to_string('emails/admin_new_order.html', context)
    plain_message = strip_tags(html_message)
    
    # Send email to admin
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_message,
        fail_silently=False,
    )

def send_order_confirmation_to_customer(order):
    """Send order confirmation email to customer"""
    subject = f'✅ Order Confirmed - #{order.order_number}'
    
    # Email context
    context = {
        'order': order,
        'order_items': order.items.all(),
        'customer_name': order.customer.get_full_name() or order.customer.username,
        'customer_email': order.customer.email,
        'site_name': 'Jadid Technology',
        'site_url': 'http://127.0.0.1:8000',
        'order_tracking_url': f'http://127.0.0.1:8000/orders/{order.order_number}/track/',
    }
    
    # Render HTML template
    html_message = render_to_string('emails/customer_order_confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    # Send email to customer
    if order.customer.email:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            html_message=html_message,
            fail_silently=False,
        )

def send_order_status_update(order):
    """Send order status update email to customer"""
    status_display = dict(order.ORDER_STATUS).get(order.status, order.status)
    
    subject = f'📦 Order Status Update - #{order.order_number} - {status_display}'
    
    context = {
        'order': order,
        'status_display': status_display,
        'customer_name': order.customer.get_full_name() or order.customer.username,
        'site_name': 'Jadid Technology',
        'site_url': 'http://127.0.0.1:8000',
        'order_tracking_url': f'http://127.0.0.1:8000/orders/{order.order_number}/track/',
    }
    
    html_message = render_to_string('emails/customer_order_status_update.html', context)
    plain_message = strip_tags(html_message)
    
    if order.customer.email:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            html_message=html_message,
            fail_silently=False,
        )