from django import forms
from .models import ProductReview


class ProductReviewForm(forms.ModelForm):

    class Meta:
        model = ProductReview

        fields = [
            "rating",
            "review",
        ]

        widgets = {
            "rating": forms.Select(
                choices=[
                    (5, "⭐⭐⭐⭐⭐ (5)"),
                    (4, "⭐⭐⭐⭐ (4)"),
                    (3, "⭐⭐⭐ (3)"),
                    (2, "⭐⭐ (2)"),
                    (1, "⭐ (1)"),
                ],
                attrs={
                    "class": "form-control"
                }
            ),

            "review": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write your review..."
                }
            ),
        }