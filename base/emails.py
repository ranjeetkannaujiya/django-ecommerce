from django.conf import settings
from django.core.mail import send_mail, EmailMessage


# ===========================================
# CUSTOMER ORDER CONFIRMATION
# ===========================================

def send_order_confirmation_email(order):

    subject = f"✅ Order Confirmed | {order.order_id}"

    message = f"""
Hello {order.user.user.first_name},

Your order has been placed successfully.

Order ID :
{order.order_id}

Payment Status :
{order.payment_status}

Order Status :
{order.order_status}

Thank you for shopping with us.

R Ecommerce Team
"""

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.user.user.email],
    )

    email.send(fail_silently=False)


# ===========================================
# ADMIN NEW ORDER
# ===========================================

def send_admin_order_new_email(order):

    subject = f"🛒 New Order | {order.order_id}"

    message = f"""
New Order Received

Customer :
{order.user.user.get_full_name()}

Email :
{order.user.user.email}

Order ID :
{order.order_id}

Please login to the admin panel.

R Ecommerce
"""

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.ADMIN_EMAIL],
    )

    email.send(fail_silently=False)