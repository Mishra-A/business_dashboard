from django.contrib import admin

# Register your models here.

from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'country', 'created_at']
    list_filter = ['country', 'city', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'city', 'country']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'company_name', 'bio')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'country')
        }),
        ('Profile Details', {
            'fields': ('profile_picture', 'date_of_birth')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )