from django.shortcuts import render
from django.db.models import Q
from products.models import Product


def index(request):

    products = Product.objects.select_related(
        "category"
    ).prefetch_related(
        "product_images"
    )

    search = request.GET.get("search", "").strip()

    if search:
        products = products.filter(
            Q(product_name__icontains=search) |
            Q(product_description__icontains=search) |
            Q(category__category_name__icontains=search)
        )

    sort = request.GET.get("sort")

    if sort == "low":
        products = products.order_by("price")

    elif sort == "high":
        products = products.order_by("-price")

    elif sort == "az":
        products = products.order_by("product_name")

    elif sort == "za":
        products = products.order_by("-product_name")

    elif sort == "latest":
        products = products.order_by("-created_at")

    context = {
        "products": products,
    }

    return render(request, "home/index.html", context)