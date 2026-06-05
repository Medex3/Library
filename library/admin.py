from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Feedback
from .models import User, Category, Publisher, Author, Book, BookAuthor, BookInstance, Borrowing, Reservation, Notification, ActionLog


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'last_name', 'first_name', 'middle_name', 'role', 'email')
    list_filter = ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('middle_name', 'role', 'phone', 'group')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name')


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'category', 'year')
    list_filter = ('category', 'year')
    search_fields = ('title', 'isbn')
    inlines = [BookAuthorInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'inventory_number', 'status', 'location')
    list_filter = ('status',)


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('book_instance', 'user', 'borrowed_date', 'due_date', 'status')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'created_at', 'status')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'is_read', 'created_at')


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read',)