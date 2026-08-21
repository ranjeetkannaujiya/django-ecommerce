from django.contrib import admin
from .models import *


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "is_paid",
        "created_at",
    )

    search_fields = (
        "user__user__username",
    )

    list_filter = (
        "is_paid",
    )


@admin.register(CartItem)
class CartItemsAdmin(admin.ModelAdmin):

    list_display = (
        "cart",
        "product",
        "quantity",
    )

    search_fields = (
        "product__product_name",
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "coupon_code",
        "discount_price",
    )