from django.urls import path
from . import views

urlpatterns = [

    path("", views.order_page, name="order_page"),
    path("checkout/", views.checkout, name="checkout"),

    path("address/", views.address, name="address"),
    path("address/add/", views.add_address, name="add_address"),
    path("place-order/", views.place_order, name="place_order"),

    path("payment/", views.payment_page, name="payment"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("payment-failed/", views.payment_failed, name="payment_failed"),
    path("order-success/<str:order_id>/", views.order_success, name="order_success"),
    path("my-order/", views.my_order, name="my_orders"),
    path("my-order/<str:order_id>/", views.order_detail, name="order_detail"),
    path("cancel-order/<str:order_id>/", views.cancel_order, name="cancel_order"),

]