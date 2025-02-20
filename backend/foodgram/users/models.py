from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_PERSONAL


class User(AbstractUser):
    """Модель описывающая Пользователя."""
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name='Почта',
        help_text='Введите Вашу почту',
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_PERSONAL,
        blank=False,
        null=False,
        verbose_name='Имя',
        help_text='Введите ваше имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_PERSONAL,
        blank=False,
        null=False,
        verbose_name='Фамилия',
        help_text='Введите вашу фамилию'
    )

    LOGIN_FIELDS = ('email',)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta(AbstractUser.Meta):
        ordering = ('email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='publisher',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'author',
                ],
                name='unique_subscribe'
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_unique_failture',
                check=~models.Q(user=models.F('author')),
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
