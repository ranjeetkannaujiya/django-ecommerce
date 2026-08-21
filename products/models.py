from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
from accounts.models import Profile


# Category acts as the top-level product grouping, and slug generation keeps the
# URL layer human-readable while maintaining uniqueness in the database.
class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to="categories")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.category_name


class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.size_name


# Product is the core catalog entity. Variant data is separated from the base
# product so pricing and stock logic can be extended without tightly coupling
# product identity to a single size or color configuration.
class Product(BaseModel):
    product_name = models.CharField(
        max_length=100,
        db_index=True
    )

    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    price = models.PositiveIntegerField(
        db_index=True
    )

    product_description = models.TextField()

    color_variant = models.ManyToManyField(
        ColorVariant,
        blank=True
    )

    size_variant = models.ManyToManyField(
        SizeVariant,
        blank=True
    )

    stock = models.PositiveIntegerField(
        default=10
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.product_name

    def get_product_price_by_size(self, size):
        size_obj = self.size_variant.filter(
            size_name=size
        ).first()

        if size_obj:
            return self.price + size_obj.price

        return self.price


class ProductImage(BaseModel):
    Product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_images"
    )

    image = models.ImageField(
        upload_to="product"
    )

    def __str__(self):
        return self.Product.product_name


# Product reviews are stored per user and per product to enforce a clean
# one-review-per-customer workflow while allowing the store to show ratings.
class ProductReview(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField(
        default=5
    )

    review = models.TextField()

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        unique_together = ("product", "user")

    def __str__(self):
        return f"{self.user.user.username} - {self.product.product_name}"