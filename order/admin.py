from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Order, Address
from .emails import (send_invoice_email, send_order_status_email, send_order_cancel_email,)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # =========================
    # Customer Name
    # =========================
    @admin.display(description="Customer")
    def customer_name(self, obj):
        full_name = obj.user.user.get_full_name()

        if full_name:
            return full_name

        return obj.user.user.email

    # =========================
    # Customer Details
    # =========================
    @admin.display(description="Customer Details")
    def customer_details(self, obj):

        profile = obj.user
        user = profile.user

        phone = getattr(profile, "phone_number", "Not Added")

        return mark_safe(f"""
        <div style="line-height:28px;">
            <b>Name :</b> {user.get_full_name()} <br>
            <b>Email :</b> {user.email} <br>
            <b>Username :</b> {user.username} <br>
            <b>Phone :</b> {phone}
        </div>
        """)

    # =========================
    # Ordered Products
    # =========================
    @admin.display(description="Ordered Products")
    def order_items(self, obj):

        html = ""

        total = 0

        for item in obj.cart.cart_items.all():

            image = ""

            if item.product.product_images.first():
                image = item.product.product_images.first().image.url

            total += item.get_total_price

            html += f"""
            <div style="
                border:1px solid #ddd;
                padding:15px;
                margin-bottom:15px;
                border-radius:8px;
                background:#fafafa;
            ">

                <img src="{image}"
                     width="80"
                     height="80"
                     style="border-radius:5px;margin-bottom:10px;">

                <br>

                <b>Product :</b> {item.product.product_name}<br>

                <b>Size :</b> {item.size_variant if item.size_variant else "-"}<br>

                <b>Quantity :</b> {item.quantity}<br>

                <b>Single Price :</b> ₹{item.get_single_price}<br>

                <b>Total Price :</b> ₹{item.get_total_price}

            </div>
            """

        html += f"""
        <hr>

        <h2 style="color:green;">
            Grand Total : ₹{total}
        </h2>
        """

        return mark_safe(html)

    # =========================
    # Admin Table
    # =========================

    list_display = (
        "order_id",
        "customer_name",
        "order_status",
        "payment_status",
        "is_paid",
        "created_at",
    )

    list_editable = (
        "order_status",
        "payment_status",
    )

    list_filter = (
        "order_status",
        "payment_status",
        "is_paid",
    )

    search_fields = (
        "order_id",
        "user__user__first_name",
        "user__user__last_name",
        "user__user__email",
    )

    readonly_fields = (
        "order_id",
        "payment_id",
        "created_at",
        "updated_at",
        "customer_details",
        "order_items",
    )

    fieldsets = (

        ("Order Information", {
            "fields": (
                "order_id",
                "order_status",
                "payment_status",
                "is_paid",
                "payment_id",
            )
        }),

        ("Customer Information", {
            "fields": (
                "user",
                "address",
                "customer_details",
            )
        }),

        ("Ordered Products", {
            "fields": (
                "cart",
                "order_items",
            )
        }),

        ("Dates", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),

    )

    list_select_related = (
        "user",
        "address",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )

    def save_model(self, request, obj, form, change):

        old_status = None
        old_payment = None

        if change:

            old = Order.objects.get(pk=obj.pk)

            old_status = old.order_status
            old_payment = old.payment_status

        super().save_model(request, obj, form, change)

        # Payment Successful
        if (
            change and
            old_payment != obj.payment_status and
            obj.payment_status == "SUCCESS"
        ):

            send_invoice_email(obj)

        # Order Cancelled
        if (
            change and
            old_status != obj.order_status and
            obj.order_status == "CANCELLED"
        ):

            send_order_cancel_email(obj)

        # Status Changed
        elif (
            change and
            old_status != obj.order_status
        ):

            send_order_status_email(obj)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "phone",
        "city",
        "state",
        "pincode",
    )

    search_fields = (
        "full_name",
        "phone",
        "city",
    )

    list_filter = (
        "state",
    )

    ordering = (
        "-created_at",
    )


# ==========================
# Django Admin Branding
# ==========================

admin.site.site_header = "R Ecommerce Admin"
admin.site.site_title = "R Ecommerce"
admin.site.index_title = "Welcome to R Ecommerce Dashboard"