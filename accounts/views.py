from django.shortcuts import render , redirect
import uuid
from base.emails import send_account_activation_email
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required


# Login flow validates the user's identity against a Django auth user.
# If the email is not verified, the request is blocked before authentication.
def login_page(request):

    if request.method == 'POST':

        login_input = request.POST.get("login", "").strip()
        password = request.POST.get('password', '')

        user_obj = User.objects.filter(email__iexact=login_input).first()

        if not user_obj:
            user_obj = User.objects.filter(username__iexact=login_input).first()

        if not user_obj:
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)

        if not user_obj.profile.is_email_verified:
            try:
                send_account_activation_email(
                    user_obj.email,
                    user_obj.profile.email_token
                )
                messages.warning(
                    request,
                    'Your account is not verified. A new verification email was sent.'
                )
            except Exception:
                messages.error(
                    request,
                    'Your account is not verified and the verification email could not be sent. Please try again later.'
                )
            return HttpResponseRedirect(request.path_info)


        username = user_obj.username if user_obj else login_input
        user_obj = authenticate(
            username=username,
            password=password
        )

        if user_obj:
            login(request, user_obj)

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            
            return redirect('index')

        # Typo fixed
        messages.error(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')


def logout_page(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("index")   

# Registration creates the built-in Django User and then triggers the profile
# creation signal. This keeps auth and profile logic separated while still
# onboarding the customer smoothly.
def register_page(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get("username", '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return HttpResponseRedirect(request.path_info)

        if not username:
            messages.error(request, 'Username is required.')
            return HttpResponseRedirect(request.path_info)

        # ===========================
        # Password Validation
        # ===========================

        if len(password) < 8:
            messages.error(
                request,
                'Password must be at least 8 characters.'
            )
            return HttpResponseRedirect(request.path_info)

        # ===========================

        existing_user = User.objects.filter(email__iexact=email).first()
        if existing_user:
            if not existing_user.profile.is_email_verified:
                try:
                    send_account_activation_email(
                        existing_user.email,
                        existing_user.profile.email_token
                    )
                    messages.warning(
                        request,
                        'This email is already registered. A new verification email was sent.'
                    )
                except Exception:
                    messages.error(
                        request,
                        'This email is already registered, but the verification email could not be sent.'
                    )
            else:
                messages.warning(request, "Email already exists.")
            return HttpResponseRedirect(request.path_info)

        if User.objects.filter(username__iexact=username).exists():
            messages.warning(request, "Username already exists.")
            return HttpResponseRedirect(request.path_info)


        try:
            with transaction.atomic():
                user_obj = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password,
                )
                profile, _ = Profile.objects.get_or_create(user=user_obj)
                if not profile.email_token:
                    profile.email_token = str(uuid.uuid4())
                    profile.save(update_fields=["email_token"])
        except IntegrityError:
            messages.error(
                request,
                'This username or email was registered at the same time. Please try again with different details.'
            )
            return HttpResponseRedirect(request.path_info)
        except Exception:
            messages.error(
                request,
                'Registration could not be completed right now. Please try again later.'
            )
            return HttpResponseRedirect(request.path_info)

        try:
            send_account_activation_email(
                user_obj.email,
                profile.email_token
            )
        except Exception:
            messages.error(
                request,
                'Account created, but the verification email could not be sent. Please try registering again later.'
            )
            return HttpResponseRedirect(request.path_info)

        messages.success(
            request,
            'An activation email has been sent to your email address.'
        )

        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/register.html')


def activate_email(request, email_token):

    try:

        profile = Profile.objects.get(
            email_token=email_token
        )

        profile.is_email_verified = True
        profile.email_token = ""

        profile.save()

        messages.success(
            request,
            "Email verified successfully."
        )

        return redirect('login')

    except Exception:

        return HttpResponse('Invalid Email token')


@login_required
def profile_page(request):

    profile = request.user.profile

    context = {
        "profile": profile
    }

    return render(
        request,
        "accounts/profile.html",
        context
    )


@login_required
def edit_profile(request):

    profile = request.user.profile

    if request.method == "POST":

        request.user.first_name = request.POST.get("first_name")

        email = request.POST.get("email")
        if User.objects.exclude(id=request.user.id).filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("edit_profile")
        # Sirf tab jab email change hua ho
        if request.user.email != email:
            request.user.email = email
            profile.is_email_verified = False
            profile.email_token = str(uuid.uuid4())

            send_account_activation_email(
                 request.user.email,
                 profile.email_token
            )

        request.user.last_name = request.POST.get("last_name")

        # Username Update
        username = request.POST.get("username")

        if username:
            if User.objects.exclude(id=request.user.id).filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect("edit_profile")

            request.user.username = username

        # Phone
        profile.phone_number = request.POST.get("phone_number")

        # Profile Image
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        request.user.save()
        profile.save()

        if profile.is_email_verified:
            messages.success(
                request,
                "Profile updated successfully."
            )
        else:
            messages.success(
                request,
                "Profile updated. Please verify your new email address."
            )
        return redirect("profile")

    context = {
        "profile": profile
    }

    return render(
        request,
        "accounts/edit_profile.html",
        context
    )


@login_required
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(request, user)

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect("profile")

        else:

            messages.error(
                request,
                "Please correct the errors below."
            )

    else:

        form = PasswordChangeForm(request.user)

    context = {
        "form": form
    }

    return render(
        request,
        "accounts/change_password.html",
        context
    )