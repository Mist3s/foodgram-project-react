from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


REGEX_SIGNS = RegexValidator(r'^[\w.@+-]+\Z', 'Поддерживаемые символы.')
REGEX_ME = RegexValidator(r'[^m][^e]', 'Имя пользователя не может быть "me".')


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=150,
        validators=(REGEX_SIGNS, REGEX_ME),
        verbose_name='Никнейм пользователя',
        help_text='Укажите никнейм пользователя'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='E-mail пользователя',
        help_text='Укажите e-mail пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        help_text='Укажите имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя',
        help_text='Укажите фамилия пользователя'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
