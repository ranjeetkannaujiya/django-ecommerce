from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from .models import Profile


@override_settings(
	STORAGES={
		"default": {
			"BACKEND": "django.core.files.storage.FileSystemStorage",
		},
		"staticfiles": {
			"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
		},
	}
)
class AccountFlowTests(TestCase):

	@patch("accounts.views.send_account_activation_email")
	def test_registration_normalizes_email(self, send_email):
		response = self.client.post(
			reverse("register"),
			{
				"first_name": "Test",
				"last_name": "User",
				"username": "testuser",
				"email": "  TEST@Example.COM ",
				"password": "StrongPassword123",
			},
		)

		self.assertRedirects(response, reverse("register"))
		user = User.objects.get(username="testuser")
		self.assertEqual(user.email, "test@example.com")
		send_email.assert_called_once()

	@patch("accounts.views.send_account_activation_email")
	def test_duplicate_unverified_email_resends_activation(self, send_email):
		user = User.objects.create_user(
			username="pending",
			email="pending@example.com",
			password="StrongPassword123",
		)
		user.profile.email_token = "token"
		user.profile.save(update_fields=["email_token"])

		self.client.post(
			reverse("register"),
			{
				"first_name": "Another",
				"last_name": "User",
				"username": "another",
				"email": "PENDING@EXAMPLE.COM",
				"password": "StrongPassword123",
			},
		)

		self.assertEqual(User.objects.filter(email="pending@example.com").count(), 1)
		send_email.assert_called_once()

	@patch("accounts.views.send_account_activation_email")
	def test_duplicate_email_recovers_missing_profile(self, send_email):
		user = User.objects.create_user(
			username="legacy",
			email="legacy@example.com",
			password="StrongPassword123",
		)
		user.profile.delete()

		self.client.post(
			reverse("register"),
			{
				"first_name": "Another",
				"last_name": "User",
				"username": "another",
				"email": "LEGACY@EXAMPLE.COM",
				"password": "StrongPassword123",
			},
		)

		self.assertTrue(Profile.objects.filter(user=user).exists())
		send_email.assert_called_once()

	@patch("accounts.views.send_account_activation_email")
	def test_unverified_login_resends_activation(self, send_email):
		user = User.objects.create_user(
			username="pending",
			email="pending@example.com",
			password="StrongPassword123",
		)
		user.profile.email_token = "token"
		user.profile.save(update_fields=["email_token"])

		response = self.client.post(
			reverse("login"),
			{"login": "PENDING@EXAMPLE.COM", "password": "StrongPassword123"},
		)

		self.assertRedirects(response, reverse("login"))
		send_email.assert_called_once()

	def test_verified_login_accepts_case_insensitive_email(self):
		user = User.objects.create_user(
			username="verified",
			email="verified@example.com",
			password="StrongPassword123",
		)
		user.profile.is_email_verified = True
		user.profile.save(update_fields=["is_email_verified"])

		response = self.client.post(
			reverse("login"),
			{"login": "VERIFIED@EXAMPLE.COM", "password": "StrongPassword123"},
		)

		self.assertRedirects(response, reverse("index"))
		self.assertTrue(response.wsgi_request.user.is_authenticated)
