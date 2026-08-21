from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import uuid

from accounts.models import Profile
from cart.models import Cart
from .models import Address, Order

from .emails import (
    send_invoice_email,
    send_admin_new_order_email,
)


# =========================================================
# ORDER PAGE
# =========================================================

@login_required
def order_page(request):

    profile = Profile.objects.get(user=request.user)

    cart = Cart.objects.filter(
        user=profile,
        is_paid=False
    ).first()

    addresses = Address.objects.filter(
        user=profile
    )

    context = {
        "cart": cart,
        "addresses": addresses,
    }

    return render(
        request,
        "order/order_page.html",
        context
    )


# =========================================================
# ADDRESS LIST
# =========================================================

@login_required
def address(request):

    profile = Profile.objects.get(
        user=request.user
    )

    addresses = Address.objects.filter(
        user=profile
    )

    context = {
        "addresses": addresses
    }

    return render(
        request,
        "order/address.html",
        context
    )


# =========================================================
# ADD ADDRESS
# =========================================================

@login_required
def add_address(request):

    if request.method == "POST":

        profile = Profile.objects.get(
            user=request.user
        )

        Address.objects.create(
            user=profile,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
        )

        messages.success(
            request,
            "Address added successfully."
        )

        return redirect("address")

    return render(
        request,
        "order/add_address.html"
    )


# =========================================================
# PLACE ORDER
# =========================================================
# This is the critical checkout stage where the current cart is converted into a
# real order. The system validates ownership, prevents duplicate unpaid orders,
# and stores the current order ID in session for the next checkout step.
@login_required
def place_order(request):

    # Direct URL access prevent
    if request.method != "POST":
        return redirect("address")

    profile = Profile.objects.get(
        user=request.user
    )

    # Get current unpaid cart
    cart = Cart.objects.filter(
        user=profile,
        is_paid=False
    ).first()

    if not cart:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    # Selected address
    address_id = request.POST.get("address")

    if not address_id:

        messages.error(
            request,
            "Please select a delivery address."
        )

        return redirect("address")

    # Make sure address belongs to current user
    address = get_object_or_404(
        Address,
        uid=address_id,
        user=profile
    )

    # Prevent duplicate unpaid order
    existing_order = (
        Order.objects
        .filter(
            user=profile,
            cart=cart,
            is_paid=False,
        )
        .exclude(
            order_status="CANCELLED"
        )
        .first()
    )

    if existing_order:

        request.session["current_order"] = str(
            existing_order.uid
        )

        return redirect("checkout")

    # Create order
    order = Order.objects.create(

        user=profile,

        cart=cart,

        address=address,

        order_id=str(uuid.uuid4()),

        payment_status="PENDING",

        order_status="PENDING"
    )

    # Save current order in session
    request.session["current_order"] = str(
        order.uid
    )

    # =====================================================
    # ADMIN EMAIL
    # =====================================================

    try:

        send_admin_new_order_email(order)

    except Exception as e:

        # Email failure should NOT cancel/crash the order
        print(
            "Admin Order Email Error:",
            e
        )

    return redirect("checkout")


# =========================================================
# CHECKOUT
# =========================================================

@login_required
def checkout(request):

    profile = Profile.objects.get(
        user=request.user
    )

    order_uid = request.session.get(
        "current_order"
    )

    if not order_uid:

        return redirect("order_page")

    order = get_object_or_404(
        Order,
        uid=order_uid,
        user=profile
    )

    context = {
        "order": order
    }

    return render(
        request,
        "order/checkout.html",
        context
    )


# =========================================================
# PAYMENT PAGE
# =========================================================

@login_required
def payment_page(request):

    profile = Profile.objects.get(
        user=request.user
    )

    order_uid = request.session.get(
        "current_order"
    )

    if not order_uid:

        return redirect("order_page")

    order = get_object_or_404(
        Order,
        uid=order_uid,
        user=profile
    )

    # Cancelled order cannot continue
    if order.order_status == "CANCELLED":

        request.session.pop(
            "current_order",
            None
        )

        messages.error(
            request,
            "This order has been cancelled. Please place a new order."
        )

        return redirect("cart")

    context = {
        "order": order
    }

    return render(
        request,
        "order/payment.html",
        context
    )


# =========================================================
# PAYMENT SUCCESS
# =========================================================

@login_required
def payment_success(request):

    profile = Profile.objects.get(
        user=request.user
    )

    # Get current order from session
    order_uid = request.session.get(
        "current_order"
    )

    if not order_uid:

        return redirect("index")

    order = get_object_or_404(
        Order,
        uid=order_uid,
        user=profile
    )

    # =====================================================
    # ALREADY PAID
    # =====================================================

    if order.is_paid:

        return redirect(
            "order_success",
            order_id=order.order_id
        )

    # =====================================================
    # 1. UPDATE ORDER
    # =====================================================

    order.is_paid = True

    order.payment_status = "SUCCESS"

    order.order_status = "CONFIRMED"

    order.payment_id = str(
        uuid.uuid4()
    )

    order.save()

    order.refresh_from_db()

    # =====================================================
    # 2. UPDATE CART
    # =====================================================

    cart = order.cart

    cart.is_paid = True

    cart.save()

    # =====================================================
    # 3. CREATE NEW EMPTY CART
    # =====================================================

    Cart.objects.create(
        user=profile
    )

    # =====================================================
    # 4. CUSTOMER INVOICE EMAIL
    # =====================================================

    try:

        send_invoice_email(order)

        print(
            "Customer Invoice Sent"
        )

    except Exception as e:

        # Email failure should NOT break order success
        print(
            "Customer Invoice Error:",
            e
        )

    # =====================================================
    # 5. CLEAR CURRENT ORDER SESSION
    # =====================================================

    request.session.pop(
        "current_order",
        None
    )

    # =====================================================
    # 6. SUCCESS MESSAGE
    # =====================================================

    messages.success(
        request,
        "Payment Successful."
    )

    # =====================================================
    # 7. REDIRECT
    # =====================================================

    return redirect(
        "order_success",
        order_id=order.order_id
    )


# =========================================================
# ORDER SUCCESS
# =========================================================

@login_required
def order_success(request, order_id):

    profile = Profile.objects.get(
        user=request.user
    )

    order = get_object_or_404(

        Order.objects
        .select_related(
            "address",
            "cart"
        )
        .prefetch_related(
            "cart__cart_items__product",
            "cart__cart_items__size_variant"
        ),

        user=profile,

        order_id=order_id
    )

    context = {
        "order": order
    }

    return render(
        request,
        "order/order_success.html",
        context
    )


# =========================================================
# PAYMENT FAILED
# =========================================================

@login_required
def payment_failed(request):

    profile = Profile.objects.get(
        user=request.user
    )

    order_uid = request.session.get(
        "current_order"
    )

    if not order_uid:

        return redirect("order_page")

    order = get_object_or_404(
        Order,
        uid=order_uid,
        user=profile
    )

    order.payment_status = "FAILED"

    order.save()

    messages.error(
        request,
        "Payment Failed! Please try again."
    )

    return redirect("payment")


# =========================================================
# MY ORDERS
# =========================================================

@login_required
def my_order(request):

    profile = Profile.objects.get(
        user=request.user
    )

    orders = (

        Order.objects

        .filter(
            user=profile
        )

        .select_related(
            "cart"
        )

        .prefetch_related(
            "cart__cart_items__product__product_images"
        )

        .order_by(
            "-created_at"
        )
    )

    context = {
        "orders": orders
    }

    return render(
        request,
        "order/my_order.html",
        context
    )


# =========================================================
# ORDER DETAIL
# =========================================================

@login_required
def order_detail(request, order_id):

    profile = Profile.objects.get(
        user=request.user
    )

    order = get_object_or_404(

        Order.objects
        .select_related(
            "address",
            "cart"
        )
        .prefetch_related(
            "cart__cart_items__product",
            "cart__cart_items__size_variant"
        ),

        user=profile,

        order_id=order_id
    )

    context = {
        "order": order
    }

    return render(
        request,
        "order/order_detail.html",
        context
    )


# =========================================================
# CANCEL ORDER
# =========================================================

@login_required
def cancel_order(request, order_id):

    profile = Profile.objects.get(
        user=request.user
    )

    order = get_object_or_404(
        Order,
        user=profile,
        order_id=order_id
    )

    # Only pending/confirmed orders can be cancelled
    if order.order_status not in [
        "PENDING",
        "CONFIRMED"
    ]:

        messages.error(
            request,
            "This order cannot be cancelled."
        )

        return redirect(
            "my_orders"
        )

    # Update status
    order.order_status = "CANCELLED"

    order.save()

    # Clear current order session if required
    if request.session.get(
        "current_order"
    ) == str(order.uid):

        request.session.pop(
            "current_order",
            None
        )

    messages.success(
        request,
        "Order cancelled successfully."
    )

    return redirect(
        "my_orders"
    )

