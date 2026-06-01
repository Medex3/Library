from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# 1. Расширенная модель пользователя
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('librarian', 'Библиотекарь'),
        ('reader', 'Читатель'),
    ]
    middle_name = models.CharField(max_length=150, blank=True, verbose_name='Отчество')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader', verbose_name='Роль')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    group = models.CharField(max_length=50, blank=True, verbose_name='Группа (для студентов)')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'


# 2. Категория
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


# 3. Издательство
class Publisher(models.Model):
    name = models.CharField(max_length=300, unique=True, verbose_name='Название')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')

    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'

    def __str__(self):
        return self.name


# 4. Автор
class Author(models.Model):
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    middle_name = models.CharField(max_length=150, blank=True, verbose_name='Отчество')

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


# 5. Книга
class Book(models.Model):
    title = models.CharField(max_length=500, verbose_name='Название')
    isbn = models.CharField(max_length=20, unique=True, blank=True, verbose_name='ISBN')
    udc = models.CharField(max_length=50, blank=True, verbose_name='УДК')
    bbk = models.CharField(max_length=50, blank=True, verbose_name='ББК')
    authors = models.ManyToManyField(Author, through='BookAuthor', verbose_name='Авторы')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Издательство')
    year = models.IntegerField(null=True, blank=True, verbose_name='Год издания')
    pages = models.IntegerField(null=True, blank=True, verbose_name='Количество страниц')
    description = models.TextField(blank=True, verbose_name='Описание')
    cover_image = models.ImageField(upload_to='covers/', blank=True, verbose_name='Обложка')
    file = models.FileField(upload_to='books/', blank=True, verbose_name='Файл книги (PDF)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def __str__(self):
        return self.title


# 6. Связь Книга-Автор
class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    order = models.IntegerField(default=1, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Автор книги'
        verbose_name_plural = 'Авторы книг'
        ordering = ['order']


# 7. Экземпляр книги
class BookInstance(models.Model):
    STATUS_CHOICES = [
        ('available', 'В наличии'),
        ('borrowed', 'Выдана'),
        ('reserved', 'Забронирована'),
        ('repair', 'В ремонте'),
        ('lost', 'Утеряна'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='instances', verbose_name='Книга')
    inventory_number = models.CharField(max_length=50, unique=True, verbose_name='Инвентарный номер')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='Статус')
    location = models.CharField(max_length=100, blank=True, verbose_name='Место хранения')

    class Meta:
        verbose_name = 'Экземпляр'
        verbose_name_plural = 'Экземпляры'

    def __str__(self):
        return f'{self.book.title} — {self.inventory_number}'


# 8. Выдача/возврат
class Borrowing(models.Model):
    STATUS_CHOICES = [
        ('active', 'Выдана'),
        ('returned', 'Возвращена'),
        ('overdue', 'Просрочена'),
    ]
    book_instance = models.ForeignKey(BookInstance, on_delete=models.CASCADE, verbose_name='Экземпляр')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Читатель')
    borrowed_date = models.DateField(auto_now_add=True, verbose_name='Дата выдачи')
    due_date = models.DateField(verbose_name='Дата возврата')
    returned_date = models.DateField(null=True, blank=True, verbose_name='Фактическая дата возврата')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_borrowings', verbose_name='Выдал')

    class Meta:
        verbose_name = 'Выдача'
        verbose_name_plural = 'Выдачи'

    def __str__(self):
        return f'{self.book_instance} → {self.user}'


# 9. Бронирование
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('fulfilled', 'Выполнено'),
        ('cancelled', 'Отменено'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Читатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата бронирования')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'


# 10. Уведомление
class Notification(models.Model):
    TYPE_CHOICES = [
        ('due_reminder', 'Напоминание о возврате'),
        ('overdue', 'Просрочка'),
        ('reservation_ready', 'Книга доступна'),
        ('system', 'Системное'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name='Тип')
    message = models.TextField(verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


# 11. Лог действий
class ActionLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Вход'),
        ('logout', 'Выход'),
        ('borrow', 'Выдача'),
        ('return', 'Возврат'),
        ('add_book', 'Добавление книги'),
        ('edit_book', 'Редактирование книги'),
        ('delete', 'Удаление'),
        ('report', 'Формирование отчёта'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, verbose_name='Действие')
    description = models.TextField(blank=True, verbose_name='Описание')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'