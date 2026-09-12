from django.db import models
from django.urls import reverse


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True, help_text="13-character ISBN")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    published_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # set once, on creation
    updated_at = models.DateTimeField(auto_now=True)      # updated every save

    class Meta:
        ordering = ["title"]  # default sort order when querying

    def __str__(self):
        # what shows up in Django admin / shell, e.g. "Dune by Frank Herbert"
        return f"{self.title} by {self.author}"

    def get_absolute_url(self):
        # lets templates/redirects do book.get_absolute_url() instead of
        # hardcoding the URL — handy after create/update actions
        return reverse("book-detail", kwargs={"pk": self.pk})

    @property
    def in_stock(self):
        return self.stock > 0