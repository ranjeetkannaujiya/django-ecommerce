from django.urls import path
from . import views

urlpatterns = [

    # Add Review
    path(
        "<slug:slug>/review/",
        views.add_review,
        name="add_review",
    ),

    # Product Detail
    path(
        "<slug:slug>/",
        views.get_product,
        name="get_product",
    ),

    # Edit Review
    path(
        "review/<uuid:uid>/edit/",
        views.edit_review,
        name="edit_review",
    ),

    # Delete Review
    path(
        "review/<uuid:uid>/delete/",
        views.delete_review,
        name="delete_review",
    ),
]