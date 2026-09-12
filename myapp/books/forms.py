from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # exclude timestamps - those are set automatically, not by the user
        fields = ["title", "author", "isbn", "price", "stock", "description", "published_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "published_date": forms.DateInput(attrs={"type": "date"}),
        }