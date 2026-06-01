from django import forms
from django.contrib.auth.forms import UserCreationForm
from library.models import User


class CustomUserCreationForm(UserCreationForm):
    middle_name = forms.CharField(max_length=150, required=False, label='Отчество')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')
    group = forms.CharField(max_length=50, required=False, label='Группа')

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'middle_name', 'email', 'phone', 'group', 'password1', 'password2')
        labels = {
            'username': 'Логин',
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'email': 'Email',
        }