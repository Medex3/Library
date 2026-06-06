from django.urls import path
from . import views

urlpatterns = [
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Читатель
    path('reader/', views.reader_dashboard, name='reader_dashboard'),
    path('reader/borrowings/', views.reader_borrowings, name='reader_borrowings'),
    path('reader/reservations/', views.reader_reservations, name='reader_reservations'),
    path('reader/reserve/<int:book_id>/', views.reader_reserve_book, name='reader_reserve_book'),
    path('reader/cancel-reservation/<int:reservation_id>/', views.reader_cancel_reservation,
         name='reader_cancel_reservation'),
    path('reader/profile/', views.reader_profile_edit, name='reader_profile_edit'),
    path('reader/history/', views.reader_history, name='reader_history'),
    path('reader/notifications/', views.reader_notifications, name='reader_notifications'),

    # Библиотекарь
    path('librarian/', views.librarian_dashboard, name='librarian_dashboard'),
    path('librarian/borrowings/', views.librarian_borrowings, name='librarian_borrowings'),
    path('librarian/issue/', views.librarian_issue_book, name='librarian_issue_book'),
    path('librarian/return/<int:borrowing_id>/', views.librarian_return_book, name='librarian_return_book'),
    path('librarian/overdue/', views.librarian_overdue, name='librarian_overdue'),
    path('librarian/reservations/', views.librarian_reservations, name='librarian_reservations'),
    path('librarian/fulfill-reservation/<int:reservation_id>/', views.librarian_fulfill_reservation,
         name='librarian_fulfill_reservation'),
    path('librarian/cancel-reservation/<int:reservation_id>/', views.librarian_cancel_reservation,
         name='librarian_cancel_reservation'),
    path('librarian/add-instance/', views.librarian_add_instance, name='librarian_add_instance'),


    # Отчёты (библиотекарь + админ)
    path('librarian/reports/', views.reports_index, name='reports_index'),
    path('librarian/reports/borrowings/', views.report_borrowings_view, name='report_borrowings'),
    path('librarian/reports/overdue/', views.report_overdue_view, name='report_overdue'),
    path('librarian/reports/categories/', views.report_category_view, name='report_categories'),

    # Администратор
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:user_id>/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/add-book/', views.admin_add_book, name='admin_add_book'),
    path('admin-panel/logs/', views.admin_logs, name='admin_logs'),
    path('admin-panel/references/', views.admin_references, name='admin_references'),

]