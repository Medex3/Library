from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db import models
from .models import Book, Category
from .models import Feedback
from django.contrib import messages


def home(request):
    recent_books = Book.objects.all().order_by('-created_at')[:5]
    return render(request, 'library/home.html', {'recent_books': recent_books})


def catalog(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    books = Book.objects.all()

    if query:
        books = books.filter(
            models.Q(title__icontains=query) |
            models.Q(authors__last_name__icontains=query) |
            models.Q(isbn__icontains=query)
        ).distinct()

    if category_id:
        books = books.filter(category_id=category_id)

    categories = Category.objects.all()

    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'library/catalog.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': int(category_id) if category_id else '',
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    available_instances = book.instances.filter(status='available').count()
    return render(request, 'library/book_detail.html', {
        'book': book,
        'available_instances': available_instances,
    })


def about(request):
    return render(request, 'library/about.html')


def contacts(request):
    return render(request, 'library/contacts.html')

def feedback(request):
    if request.method == 'POST':
        Feedback.objects.create(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            subject=request.POST.get('subject', ''),
            message=request.POST.get('message', ''),
        )
        messages.success(request, 'Ваше сообщение отправлено!')
        return redirect('feedback')
    return render(request, 'library/feedback.html')