from django.urls import path
from . import views

urlpatterns = [

    path("", views.cart, name="cart"),

    path("add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),

    path("remove/<uuid:cart_item_uid>/", views.remove_cart, name="remove_cart"),

    path("update/<uuid:uid>/", views.update_quantity, name="update_quantity"),

    path("increase/<uuid:uid>/",views.increase_quantity, name="increase_quantity"),
    path("decrease/<uuid:uid>/",views.decrease_quantity, name="decrease_quantity"),

    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    
    path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
    

]