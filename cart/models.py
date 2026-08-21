from django.db import models
from accounts.models import Profile
from products.models import Product, SizeVariant
from base.models import BaseModel


# Coupon logic sits close to the cart because discounts are order-level business
# logic, not catalog logic. Keeping it in the cart domain makes total
# calculation and validation easier to maintain.
class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=100, unique=True)
    is_expired = models.BooleanField(default=False)
    discount_price = models.PositiveIntegerField (default=100)
    minimum_amount = models.PositiveIntegerField(default=500)

    def __str__(self):
        return self.coupon_code
    
    class Meta:
        ordering = ["created_at"]

# Cart is the shopping session container for a user. It aggregates cart items,
# optional coupon logic, and the final total calculation used during checkout.
class Cart(BaseModel):

    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="carts")

    is_paid = models.BooleanField(default=False)

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user} - {'Paid' if self.is_paid else 'Pending'}"

    @property
    def get_cart_total(self):

        total = sum(item.get_total_price for item in self.cart_items.all())

        if self.coupon:
            total -= self.coupon.discount_price

        return max(total,0)


# CartItem stores product-level quantity and variant data. The price is derived
# dynamically from base product pricing plus optional size adjustments.
class CartItem(BaseModel):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")

    size_variant = models.ForeignKey(
        SizeVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(default=1)

    def get_single_price(self):
        price = self.product.price

        if self.size_variant:
            price += self.size_variant.price

        return price

    @property
    def product_image(self):
        image = self.product.product_images.first()
 
        if image:
            return image.image.url
        return ""
    
    @property
    def get_total_price(self):
        return self.get_single_price() * self.quantity
    


