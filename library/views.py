from django.shortcuts import render
from .models import Book


def home(request):
    recent_books = Book.objects.all().order_by('-created_at')[:5]
    return render(request, 'library/home.html', {'recent_books': recent_books})


def catalog(request):
    books = Book.objects.all()
    return render(request, 'library/catalog.html', {'books': books})


def about(request):
    return render(request, 'library/about.html')


def contacts(request):
    return render(request, 'library/contacts.html')