"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models


# Tác dụng
#   Tùy chỉnh giao diện admin cho User model
#   Đinh nghĩa cách hiển thị danh sách users
#   Cấu hình form chỉnh sửa user
#   Phân quyền và kiểm soát truy cập
#   Tích hợp validation rules
#   Tùy chỉnh actions trong admin


# BaseUserAdmin
# Cấu trúc cơ bản cho user admin interface
# Các field mặc định
# Các phương thức xử lý user
# Security features
class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']  # Override thứ tự
    list_display = ['email', 'name']  # Các cột hiển thị trong listView
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser')
            }),
        (
            _('Important dates'),
            {'fields': ('last_login',)}
        ),
    )  # Tổ chức fields trong detail view
    # Phân nhóm các field liên quan
    # Hỗ trợ đa ngôn ngữ với gettext
    # Override cấu trúc mặc định
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': (
                'wide',), 'fields': (
                'email', 'password1', 'password2', 'name', 'is_active', 'is_staff')}), )


# Đăng ký model với panel của admin
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)