from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Значения поля влияют на разрешения для Api.
    Персонал всегда admin.
    """
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    USER_ROLES = (
        (ADMIN, 'Администратор'),
        (USER, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
    )

    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль', max_length=20,
        choices=USER_ROLES,
        default=USER
    )
    email = models.EmailField(
        max_length=254,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        """Относится ли пользователь к персоналу?."""
        return (self.role == User.ADMIN) or self.is_staff

    @property
    def is_user(self):
        """Относится ли пользователь к персоналу?."""
        return self.role == User.USER

    @property
    def is_moderator(self):
        """Относится ли пользователь к персоналу?."""
        return self.role == User.MODERATOR
