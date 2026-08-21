from django.shortcuts import render, get_object_or_404
from products.models import Product
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounts.models import Profile
from order.models import Order
from .models import ProductReview


def get_product(request, slug):

    product = get_object_or_404(
        Product.objects.prefetch_related(
            "product_images",
            "size_variant",
            "color_variant",
            "reviews__user__user",
        ),
        slug=slug
    )

    reviews = ProductReview.objects.filter(
        product=product
    ).select_related("user__user").order_by("-created_at")

    context = {
        "product": product,
        "reviews": reviews,
    }

    if request.GET.get("size"):

        size = request.GET.get("size")

        price = product.get_product_price_by_size(size)

        context["selected_size"] = size
        context["updated_price"] = price

    return render(
        request,
        "product/product.html",
        context
    )

@login_required
def add_review(request, slug):

    product = get_object_or_404(Product, slug=slug)
    profile = request.user.profile

    purchased = Order.objects.filter(
        user=profile,
        is_paid=True,
        cart__cart_items__product=product
    ).exclude(
        order_status="CANCELLED"
    ).exists()

    if not purchased:
        messages.error(request, "You can review only purchased products.")
        return redirect("get_product", slug=slug)

    if ProductReview.objects.filter(
        product=product,
        user=profile
    ).exists():

        messages.warning(request, "You already reviewed this product.")
        return redirect("get_product", slug=slug)

    if request.method == "POST":

        rating = int(request.POST.get("rating", 5))

        ProductReview.objects.create(
            product=product,
            user=profile,
            rating=rating,
            review=request.POST.get("review")
        )

        messages.success(request, "Review added successfully.")

    return redirect("get_product", slug=slug)


@login_required
def edit_review(request, uid):

    review = get_object_or_404(
        ProductReview,
        uid=uid,
        user=request.user.profile
    )

    if request.method == "POST":

        review.rating = int(request.POST.get("rating"))
        review.review = request.POST.get("review")
        review.save()

        messages.success(request, "Review updated successfully.")

        return redirect(
            "get_product",
            slug=review.product.slug
        )

    context = {
        "review": review
    }

    return render(
        request,
        "product/edit_review.html",
        context
    )


@login_required
def delete_review(request, uid):

    review = get_object_or_404(
        ProductReview,
        uid=uid,
        user=request.user.profile
    )

    slug = review.product.slug

    review.delete()

    messages.success(request, "Review deleted.")

    return redirect(
        "get_product",
        slug=slug
    )