from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import Book
from .forms import BookForm


def book_list(request):
    """
    Show all books. Supports a simple ?q=search query on title/author.
    """
    query = request.GET.get("q", "")
    books = Book.objects.all()
    if query:
        # icontains = case-insensitive "contains" — like a SQL LIKE '%query%'
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)

    return render(request, "books/book_list.html", {"books": books, "query": query})


def book_detail(request, pk):
    """
    Show a single book. get_object_or_404 fetches it or raises a 404
    automatically if no book with that primary key exists.
    """
    book = get_object_or_404(Book, pk=pk)
    return render(request, "books/book_detail.html", {"book": book})


@login_required
def book_create(request):
    """
    Add a new book. Only logged-in users can access this (see login_required).
    """
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'"{book.title}" was added.')
            return redirect("book-detail", pk=book.pk)
    else:
        form = BookForm()

    return render(request, "books/book_form.html", {"form": form, "action": "Add"})


@login_required
def book_update(request, pk):
    """
    Edit an existing book. Passing `instance=book` to the form pre-fills
    it with the book's current values instead of a blank form.
    """
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        # instance in the argument here indicate BookForm to just update the existing book 
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{book.title}" was updated.')
            return redirect("book-detail", pk=book.pk)
    else:
        form = BookForm(instance=book)

    return render(request, "books/book_form.html", {"form": form, "action": "Edit"})


@login_required
def book_delete(request, pk):
    """
    Delete a book, with a confirmation page first (don't delete on GET —
    that's a common security/accident mistake).
    """
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        title = book.title
        book.delete()
        messages.success(request, f'"{title}" was deleted.')
        return redirect("book-list")

    return render(request, "books/book_confirm_delete.html", {"book": book})