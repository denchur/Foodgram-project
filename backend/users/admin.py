from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from users.models import Follow

User = get_user_model()


class UsersAdmin(UserAdmin):
    list_filter = (
        'is_active',
        'is_staff',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = (
        'email',
        'last_name',
        'first_name',
    )
    add_fieldsets = [
        (
            None,
            {
                'classes': ['wide'],
                'fields': [
                    'email',
                    'username',
                    'first_name',
                    'last_name',
                    'password'],
            },
        ),
    ]


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author',
        'user__email',
        'user__last_name',
        'author__email',
        'author__last_name',
    )


admin.site.register(User, UsersAdmin)
admin.site.register(Follow, FollowAdmin)
