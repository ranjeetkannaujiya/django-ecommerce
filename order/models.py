from django.db import models
from base.models import BaseModel
from accounts.models import Profile
from cart.models import Cart


# Order represents the transactional state after a cart is validated and a user
# proceeds to checkout. It keeps payments, statuses, and the selected address
# decoupled from the cart itself for clearer order tracking.
class Order(BaseModel):

    PAYMENT_STATUS = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )

    ORDER_STATUS = (
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        )
 
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    address = models.ForeignKey(
        "Address",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="orders"
    )

    order_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="PENDING"
    )

    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default="PENDING"
    )

    is_paid = models.BooleanField(
        default=False
    )

    payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        db_index=True
    )

    def __str__(self):
        return f"{self.order_id} ({self.order_status})"


# Address is a reusable shipping record associated with a profile. The business
# logic can default a user address during checkout without tightly coupling it to
# a single order instance.
class Address(BaseModel):

    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=15
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=6
    )

    is_default = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.full_name