from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Kengaytirilgan foydalanuvchi modeli."""

    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True, verbose_name="Tug'ilgan sana")
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    preferred_language = models.CharField(
        max_length=10,
        default='uz',
        choices=[('uz', "O'zbek"), ('ru', 'Rus'), ('en', 'Ingliz')],
        verbose_name='Afzal til',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return self.username
