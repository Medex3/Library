from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import CustomUserCreationForm
from library.models import Book, BookInstance, Borrowing, Reservation, ActionLog, User, Notification
from datetime import datetime, timedelta





def is_librarian(user):
    return user.role in ['librarian', 'admin']


def is_admin(user):
    return user.role == 'admin'


# ---------- Аутентификация ----------

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'reader'
            user.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    from django.contrib.auth.forms import AuthenticationForm
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            ActionLog.objects.create(
                user=user,
                action='login',
                description=f'Пользователь {user.username} вошёл в систему (роль: {user.get_role_display()})'
            )
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'librarian':
                return redirect('librarian_dashboard')
            return redirect('reader_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    if request.user.is_authenticated:
        ActionLog.objects.create(
            user=request.user,
            action='logout',
            description=f'Пользователь {request.user.username} вышел из системы'
        )
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')


# ---------- Читатель ----------

@login_required
def reader_dashboard(request):
    active_borrowings = Borrowing.objects.filter(user=request.user, status='active')
    reservations = Reservation.objects.filter(user=request.user, status='active')
    overdue_borrowings = active_borrowings.filter(due_date__lt=timezone.now().date())
    return render(request, 'accounts/reader/dashboard.html', {
        'active_borrowings': active_borrowings,
        'reservations': reservations,
        'overdue_borrowings': overdue_borrowings,
    })


@login_required
def reader_borrowings(request):
    borrowings = Borrowing.objects.filter(user=request.user).order_by('-borrowed_date')
    return render(request, 'accounts/reader/borrowings.html', {'borrowings': borrowings})

@login_required
def reader_history(request):
    history = Borrowing.objects.filter(
        user=request.user,
        status='returned'
    ).select_related('book_instance__book').order_by('-returned_date')
    return render(request, 'accounts/reader/history.html', {'history': history})

@login_required
def reader_notifications(request):
    from library.models import Notification
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:50]
    return render(request, 'accounts/reader/notifications.html', {'notifications': notifications})

@login_required
def reader_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/reader/reservations.html', {'reservations': reservations})


@login_required
def reader_reserve_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if Reservation.objects.filter(user=request.user, book=book, status='active').exists():
        messages.warning(request, 'Вы уже забронировали эту книгу.')
    else:
        Reservation.objects.create(user=request.user, book=book)
        messages.success(request, f'Книга "{book.title}" забронирована.')
    return redirect('reader_reservations')


@login_required
def reader_cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    reservation.status = 'cancelled'
    reservation.save()
    messages.success(request, 'Бронирование отменено.')
    return redirect('reader_reservations')


@login_required
def reader_profile_edit(request):
    if request.method == 'POST':
        request.user.email = request.POST.get('email', request.user.email)
        request.user.phone = request.POST.get('phone', request.user.phone)
        request.user.save()
        messages.success(request, 'Данные обновлены.')
        return redirect('reader_profile_edit')
    return render(request, 'accounts/reader/profile_edit.html')


# ---------- Библиотекарь ----------

@login_required
@user_passes_test(is_librarian)
def librarian_dashboard(request):
    active_borrowings = Borrowing.objects.filter(status='active').count()
    overdue_count = Borrowing.objects.filter(status='active', due_date__lt=timezone.now().date()).count()
    pending_reservations = Reservation.objects.filter(status='active').count()
    total_books = Book.objects.count()
    return render(request, 'accounts/librarian/dashboard.html', {
        'active_borrowings': active_borrowings,
        'overdue_count': overdue_count,
        'pending_reservations': pending_reservations,
        'total_books': total_books,
    })


@login_required
@user_passes_test(is_librarian)
def librarian_borrowings(request):
    borrowings = Borrowing.objects.select_related('book_instance__book', 'user').all().order_by('-borrowed_date')
    return render(request, 'accounts/librarian/borrowings.html', {'borrowings': borrowings})


@login_required
@user_passes_test(is_librarian)
def librarian_issue_book(request):
    if request.method == 'POST':
        instance_id = request.POST.get('instance_id')
        user_id = request.POST.get('user_id')
        instance = get_object_or_404(BookInstance, id=instance_id, status='available')
        from library.models import User
        user = get_object_or_404(User, id=user_id)
        instance.status = 'borrowed'
        instance.save()
        due_date = timezone.now().date() + timezone.timedelta(days=14)
        Borrowing.objects.create(
            book_instance=instance,
            user=user,
            due_date=due_date,
            issued_by=request.user
        )
        messages.success(request, f'Книга выдана пользователю {user}.')
        ActionLog.objects.create(
            user=request.user,
            action='borrow',
            description=f'Выдана книга "{instance.book.title}" пользователю {user} (до {due_date})'
        )
        return redirect('librarian_borrowings')

    from library.models import User
    available_instances = BookInstance.objects.filter(status='available').select_related('book')
    readers = User.objects.filter(role='reader')
    return render(request, 'accounts/librarian/issue_book.html', {
        'available_instances': available_instances,
        'readers': readers,
    })


@login_required
@user_passes_test(is_librarian)
def librarian_return_book(request, borrowing_id):
    borrowing = get_object_or_404(Borrowing, id=borrowing_id, status__in=['active', 'overdue'])
    if request.method == 'POST':
        borrowing.book_instance.status = 'available'
        borrowing.book_instance.save()
        borrowing.status = 'returned'
        borrowing.returned_date = timezone.now().date()
        borrowing.save()
        ActionLog.objects.create(
            user=request.user,
            action='return',
            description=f'Возврат книги "{borrowing.book_instance.book.title}" от {borrowing.user}'
        )
        messages.success(request, 'Книга возвращена.')
        return redirect('librarian_borrowings')
    return render(request, 'accounts/librarian/return_book.html', {'borrowing': borrowing})


@login_required
@user_passes_test(is_librarian)
def librarian_overdue(request):
    overdue_list = Borrowing.objects.filter(
        status='active', due_date__lt=timezone.now().date()
    ).select_related('book_instance__book', 'user')
    return render(request, 'accounts/librarian/overdue.html', {'overdue_list': overdue_list})

@login_required
@user_passes_test(is_librarian)
def librarian_reservations(request):
    reservations = Reservation.objects.filter(status='active').select_related('book', 'user').order_by('created_at')
    return render(request, 'accounts/librarian/reservations.html', {'reservations': reservations})


@login_required
@user_passes_test(is_librarian)
def librarian_fulfill_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, status='active')
    reservation.status = 'fulfilled'
    reservation.save()
    # Создаём уведомление
    Notification.objects.create(
        user=reservation.user,
        type='reservation_ready',
        message=f'Книга "{reservation.book.title}" теперь доступна для вас. Обратитесь к библиотекарю.'
    )
    messages.success(request, f'Бронирование для {reservation.user} выполнено.')
    return redirect('librarian_reservations')


@login_required
@user_passes_test(is_librarian)
def librarian_cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, status='active')
    reservation.status = 'cancelled'
    reservation.save()
    Notification.objects.create(
        user=reservation.user,
        type='system',
        message=f'Бронирование книги "{reservation.book.title}" отменено библиотекарем.'
    )
    messages.success(request, f'Бронирование для {reservation.user} отменено.')
    return redirect('librarian_reservations')

# ---------- Отчёты (библиотекарь + админ) ----------
from .reports import report_borrowings_by_period, report_overdue, report_category_stats
from datetime import datetime


@login_required
@user_passes_test(is_librarian)
def reports_index(request):
    """Страница-оглавление всех отчётов"""
    return render(request, 'accounts/librarian/reports.html')


@login_required
@user_passes_test(is_librarian)
def report_borrowings_view(request):
    """Генерация отчёта: выдачи за период"""
    today = timezone.now().date()
    start_str = request.GET.get('start', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_str = request.GET.get('end', today.strftime('%Y-%m-%d'))
    start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    ActionLog.objects.create(
        user=request.user,
        action='report',
        description=f'Сформирован отчёт "Выдачи за период": {start_date} – {end_date}'
    )
    return report_borrowings_by_period(start_date, end_date)


@login_required
@user_passes_test(is_librarian)
def report_overdue_view(request):
    ActionLog.objects.create(
        user=request.user,
        action='report',
        description='Сформирован отчёт "Должники"'
    )
    """Генерация отчёта: должники"""
    return report_overdue()


@login_required
@user_passes_test(is_librarian)
def report_category_view(request):
    ActionLog.objects.create(
        user=request.user,
        action='report',
        description='Сформирован отчёт "Статистика по категориям"'
    )
    """Генерация отчёта: статистика по категориям"""
    return report_category_stats()


# ---------- Администратор ----------

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    from library.models import User
    total_users = User.objects.count()
    total_readers = User.objects.filter(role='reader').count()
    total_librarians = User.objects.filter(role='librarian').count()
    total_books = Book.objects.count()
    return render(request, 'accounts/admin/dashboard.html', {
        'total_users': total_users,
        'total_readers': total_readers,
        'total_librarians': total_librarians,
        'total_books': total_books,
    })


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    from library.models import User
    users = User.objects.all().order_by('role', 'last_name')
    return render(request, 'accounts/admin/users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_user_edit(request, user_id):
    from library.models import User
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.role = request.POST.get('role', user.role)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.is_active = 'is_active' in request.POST
        user.save()
        messages.success(request, 'Пользователь обновлён.')
        return redirect('admin_users')
    return render(request, 'accounts/admin/user_edit.html', {'edit_user': user})


@login_required
@user_passes_test(is_admin)
def admin_add_book(request):
    from library.models import Category, Publisher, Author
    if request.method == 'POST':
        book = Book.objects.create(
            title=request.POST.get('title'),
            isbn=request.POST.get('isbn', ''),
            udc=request.POST.get('udc', ''),
            bbk=request.POST.get('bbk', ''),
            year=request.POST.get('year') or None,
            pages=request.POST.get('pages') or None,
            description=request.POST.get('description', ''),
            category_id=request.POST.get('category') or None,
            publisher_id=request.POST.get('publisher') or None,
        )
        ActionLog.objects.create(
            user=request.user,
            action='add_book',
            description=f'Добавлена книга "{book.title}" (ID: {book.id})'
        )
        messages.success(request, f'Книга "{book.title}" добавлена.')
        return redirect('admin_add_book')
    categories = Category.objects.all()
    publishers = Publisher.objects.all()
    authors = Author.objects.all()
    return render(request, 'accounts/admin/add_book.html', {
        'categories': categories,
        'publishers': publishers,
        'authors': authors,
    })


@login_required
@user_passes_test(is_admin)
def admin_logs(request):
    logs = ActionLog.objects.select_related('user').all().order_by('-timestamp')[:100]
    return render(request, 'accounts/admin/logs.html', {'logs': logs})