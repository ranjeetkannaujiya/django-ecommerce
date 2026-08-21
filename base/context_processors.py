from accounts.models import Profile
from cart.models import Cart


def cart_count(request):

    count = 0

    if request.user.is_authenticated:

        try:
            profile = Profile.objects.get(user=request.user)

            cart = Cart.objects.filter(
                user=profile,
                is_paid=False
            ).first()

            if cart:
                count = cart.cart_items.count()

        except Exception:
            pass

    return {
        "cart_count": count
    }