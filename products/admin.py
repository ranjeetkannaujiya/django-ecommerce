from django.contrib import admin
from .models import *


# ===========================
# Category
# ===========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = [
        "category_name",
        "slug",
    ]

    search_fields = [
        "category_name",
    ]

    prepopulated_fields = {
        "slug": ("category_name",)
    }


# ===========================
# Product Images Inline
# ===========================

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage
    extra = 1


# ===========================
# Product
# ===========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = [
        "product_name",
        "category",
        "price",
        "stock",
        "created_at",
    ]

    search_fields = [
        "product_name",
        "category__category_name",
    ]

    list_filter = [
        "category",
        "created_at",
    ]

    prepopulated_fields = {
        "slug": ("product_name",)
    }

    inlines = [
        ProductImageAdmin
    ]


# ===========================
# Color Variant
# ===========================

@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):

    list_display = [
        "color_name",
        "price"
    ]


# ===========================
# Size Variant
# ===========================

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):

    list_display = [
        "size_name",
        "price"
    ]


# ===========================
# Product Review
# ===========================

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "user",
        "rating",
        "is_active",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_active",
    )

    search_fields = (
        "product__product_name",
        "user__user__username",
    )


# ===========================
# Product Images
# ===========================

admin.site.register(ProductImage)