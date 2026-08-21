from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from .utils import render_to_pdf


# ===========================
# CUSTOMER PAYMENT SUCCESS
# ===========================

def send_invoice_email(order):
    print("Customer Email :", order.user.user.email)
    print("Customer Username :", order.user.user.username)

    try:
        if not order.user.user.email:
            print("Customer Email Not Found")
            return 

        html_message = render_to_string(
            "order/invoice_email.html",
            {
                "order": order,
                "cart_items": order.cart.cart_items.all(),
                "grand_total": order.cart.get_cart_total,
            }
        )

        pdf = render_to_pdf(
            "order/invoice.html",
            {
                "order": order,
                "cart_items": order.cart.cart_items.all(),
                "grand_total": order.cart.get_cart_total,
            }
        )

        email = EmailMessage(
            subject=f"✅ Order Confirmed | {order.order_id}",
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.user.email],
        )

        email.content_subtype = "html"

        if pdf:
            email.attach(
                f"Invoice-{order.order_id}.pdf",
                pdf,
                "application/pdf"
            )

        email.send(fail_silently=False)

        print("Customer Invoice Sent")

    except Exception as e:
        print("Customer Invoice Error :", e)


# ===========================
# ADMIN NEW ORDER
# ===========================

def send_admin_new_order_email(order):

    html_message = render_to_string(
        "order/admin_order_email.html",
        {
            "order": order,
        }
    )

    email = EmailMessage(
        subject=f"🛒 New Order Received | {order.order_id}",
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.ADMIN_EMAIL],
    )

    email.content_subtype = "html"

    email.send(fail_silently=False)


# ===========================
# ADMIN PAYMENT SUCCESS
# ===========================

def send_admin_payment_success_email(order):

    try:

        html_message = render_to_string(
            "order/admin_payment_success_email.html",
            {
                "order": order,
            }
        )

        email = EmailMessage(
            subject=f"💰 Payment Received | {order.order_id}",
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
        )

        email.content_subtype = "html"

        email.send(fail_silently=False)

        print("Admin Payment Mail Sent")

    except Exception as e:
        print("Admin Payment Error :", e)


# ===========================
# CUSTOMER ORDER CANCELLED
# ===========================

def send_order_cancel_email(order):

    try:

        html_message = render_to_string(
            "order/order_cancel_email.html",
            {
                "order": order,
            }
        )

        email = EmailMessage(
            subject=f"❌ Order Cancelled | {order.order_id}",
            body=html_message,
            to=[order.user.user.email],
        )

        email.content_subtype = "html"

        email.send(fail_silently=False)

        print("Cancel Mail Sent")

    except Exception as e:
        print("Cancel Mail Error :", e)


# ===========================
# CUSTOMER STATUS UPDATE
# ===========================

def send_order_status_email(order):

    try:

        html_message = render_to_string(
            "order/order_status_email.html",
            {
                "order": order,
            }
        )

        email = EmailMessage(
            subject=f"📦 Order {order.order_status.title()} | {order.order_id}",
            body=html_message,
            to=[order.user.user.email],
        )

        email.content_subtype = "html"

        email.send(fail_silently=False)

        print("Status Email Sent")

    except Exception as e:
        print("Status Email Error :", e)