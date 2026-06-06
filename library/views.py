from django.core.paginator import Paginator
from django.db import models
from .models import Book, Category
from .models import Feedback
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

"""
Представления публичной части библиотеки:
- Главная страница с новыми поступлениями
- Каталог с поиском, фильтрацией и пагинацией
- Детальная страница книги
- Статические страницы (О библиотеке, Контакты)
- Форма обратной связи
"""

"""
Главная страница библиотеки.
Отображает 5 последних добавленных книг в блоке «Новые поступления».
"""
def home(request):
    recent_books = Book.objects.all().order_by('-created_at')[:5]
    return render(request, 'library/home.html', {'recent_books': recent_books})

"""
Каталог книг с поиском и фильтрацией.
Параметры GET:
    - q: поисковый запрос (по названию, автору, ISBN)
    - category: фильтр по ID категории
    - page: номер страницы (пагинация по 10 книг)
Поиск использует Q-объекты для поиска по трём полям одновременно.
"""
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

"""
Детальная страница книги.
Отображает полную информацию о книге, обложку, количество доступных экземпляров,
кнопку скачивания PDF и кнопку бронирования (для читателей).
"""
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    available_instances = book.instances.filter(status='available').count()
    return render(request, 'library/book_detail.html', {
        'book': book,
        'available_instances': available_instances,
    })

"""Статическая страница «О библиотеке»"""
def about(request):
    return render(request, 'library/about.html')

"""Статическая страница «Контакты» с адресом и телефоном"""
def contacts(request):
    return render(request, 'library/contacts.html')

"""
Форма обратной связи.
Принимает POST-запрос с полями: name, email, subject, message.
Создаёт запись в модели Feedback и перенаправляет на ту же страницу с сообщением.
"""
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