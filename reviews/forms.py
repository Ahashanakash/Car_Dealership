from django import forms
from .models import Review
from .constants import STAR_CHOICES

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['rating', 'body']

        widgets = {
            "rating": forms.RadioSelect(),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Write your review..."
            })
        }