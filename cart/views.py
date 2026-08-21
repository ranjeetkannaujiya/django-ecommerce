from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Cart, CartItem, Coupon
from accounts.models import Profile
from products.models import Product, SizeVariant


# =========================================================
# CART PAGE
# =========================================================

@login_required(login_url="login")
def cart(request):

    profile = Profile.objects.get(user=request.user)

    cart = Cart.objects.filter(
        user=profile,
        is_paid=False
    ).first()

    context = {
        "cart": cart
    }

    return render(
        request,
        "cart/cart.html",
        context
    )


# =========================================================
# ADD PRODUCT TO CART
# =========================================================

@login_required(login_url="login")
def add_to_cart(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug
    )

    profile = Profile.objects.get(
        user=request.user
    )

    size = request.GET.get("size")

    size_variant = None

    if size:
        size_variant = get_object_or_404(
            SizeVariant,
            size_name=size,
            product=product
        )

    cart, created = Cart.objects.get_or_create(
        user=profile,
        is_paid=False
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size_variant=size_variant
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


# =========================================================
# REMOVE CART ITEM
# =========================================================

@login_required(login_url="login")
def remove_cart(request, cart_item_uid):

    profile = Profile.objects.get(
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        uid=cart_item_uid,
        cart__user=profile,
        cart__is_paid=False
    )

    cart_item.delete()

    messages.success(
        request,
        "Product removed from cart."
    )

    return redirect("cart")


# =========================================================
# UPDATE QUANTITY
# =========================================================

@login_required(login_url="login")
def update_quantity(request, uid):

    profile = Profile.objects.get(
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        uid=uid,
        cart__user=profile,
        cart__is_paid=False
    )

    try:
        quantity = int(
            request.GET.get("quantity", 1)
        )

    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart_item.quantity = quantity
    cart_item.save()

    return redirect("cart")


# =========================================================
# INCREASE QUANTITY
# =========================================================

@login_required(login_url="login")
def increase_quantity(request, uid):

    profile = Profile.objects.get(
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        uid=uid,
        cart__user=profile,
        cart__is_paid=False
    )

    cart_item.quantity += 1
    cart_item.save()

    return redirect("cart")


# =========================================================
# DECREASE QUANTITY
# =========================================================

@login_required(login_url="login")
def decrease_quantity(request, uid):

    profile = Profile.objects.get(
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        uid=uid,
        cart__user=profile,
        cart__is_paid=False
    )

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()

    return redirect("cart")


# =========================================================
# APPLY COUPON
# =========================================================

@login_required(login_url="login")
def apply_coupon(request):

    if request.method != "POST":
        return redirect("cart")

    coupon_code = request.POST.get(
        "coupon",
        ""
    ).strip()

    if not coupon_code:
        messages.error(
            request,
            "Please enter a coupon code."
        )
        return redirect("cart")

    profile = Profile.objects.get(
        user=request.user
    )

    cart = get_object_or_404(
        Cart,
        user=profile,
        is_paid=False
    )

    # -----------------------------------------------------
    # FIND COUPON
    # -----------------------------------------------------

    try:

        coupon = Coupon.objects.get(
            coupon_code__iexact=coupon_code,
            is_expired=False
        )

    except Coupon.DoesNotExist:

        messages.error(
            request,
            "Invalid Coupon Code."
        )

        return redirect("cart")

    # -----------------------------------------------------
    # CHECK SAME COUPON
    # -----------------------------------------------------

    if cart.coupon == coupon:

        messages.info(
            request,
            "This coupon is already applied."
        )

        return redirect("cart")

    # -----------------------------------------------------
    # MINIMUM ORDER AMOUNT
    # -----------------------------------------------------

    total = sum(
        item.get_total_price
        for item in cart.cart_items.all()
    )

    if total < coupon.minimum_amount:

        messages.warning(
            request,
            f"Minimum order should be ₹{coupon.minimum_amount}"
        )

        return redirect("cart")

    # -----------------------------------------------------
    # APPLY COUPON
    # -----------------------------------------------------

    cart.coupon = coupon
    cart.save()

    messages.success(
        request,
        f"{coupon.coupon_code} Applied Successfully."
    )

    return redirect("cart")


# =========================================================
# REMOVE COUPON
# =========================================================

@login_required(login_url="login")
def remove_coupon(request):

    profile = Profile.objects.get(
        user=request.user
    )

    cart = Cart.objects.filter(
        user=profile,
        is_paid=False
    ).first()

    if cart:

        cart.coupon = None
        cart.save()

        messages.success(
            request,
            "Coupon Removed Successfully."
        )

    return redirect("cart")