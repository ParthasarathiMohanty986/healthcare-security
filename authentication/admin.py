from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 'get_full_name', 'role',
        'department', 'clearance_level',
        'is_emergency_authorized'
    ]
    list_filter = ['role', 'department', 'clearance_level']
    search_fields = ['username', 'first_name', 'last_name']

    fieldsets = UserAdmin.fieldsets + (
        ('Healthcare Attributes', {
            'fields': (
                'role', 'department', 'specialization',
                'clearance_level', 'hospital_affiliation',
                'certifications', 'working_hours_start',
                'working_hours_end', 'current_location',
                'is_emergency_authorized'
            )
        }),
    )