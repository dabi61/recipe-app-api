"""
Database models.
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'recipe', filename)

# Định nghĩa schema database
# Quản lý relatiionships giữa các models
# Cung cấp methods tạo/sửa/xóa records
# Validation data
# Custom model managers
# Tích hợp bussiness logic


# BaseUss
class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create, save and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    "Recipe object."
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )  # Foreignkey Tạo mối quan hệ 1 nhiều (1 user có nhiều công thức)
    # Settings.AUTH_USER_MODEL giúp liên kết với user đang sử dụng
    # Khi user bị xóa thì tất cả các recipe bị xóa theo
    title = models.CharField(max_length=255)
    # blank = true là khôt bắt buộc phải nhập
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    # có tổng 5 số, có 2 số sau dấu chấm động
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # Một công thức có thể có rất nhiều tag
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title

    # Khi mình in hoặc hiển thị đối tượng thì nó chỉ trả về tên title của đối
    # tượng thôi

# Gắn tag cho công thức


class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
class Ingredient(models.Model):
    """Ingredient for recipe"""
    name = models.CharField(max_length=255)
    user= models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name