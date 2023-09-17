from django.contrib.auth.models import (
                                    AbstractUser,
)
from django.db import models

from users.vars import user_vars


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name=user_vars.user_verbose_email,
        help_text=user_vars.user_help_text_email,
    )
    LOGIN_FIELDS = ('email',)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        ordering = ['email']
        verbose_name = user_vars.custom_user_singular
        verbose_name_plural = user_vars.custom_user_plural
        unique_together = ('username', 'email')

    def __str__(self) -> str:
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='subscriber',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=user_vars.follower_verbose
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='publisher',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=user_vars.publisher_verbose
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'author',
                ],
                name='unique_subscribe'
            )
        ]
        verbose_name = user_vars.subscribe_singular
        verbose_name_plural = user_vars.subscribe_plural
