from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'user', 'action',
        'resource_type', 'resource_id',
        'access_granted', 'is_emergency'
    ]
    list_filter = ['access_granted', 'is_emergency', 'action']
    readonly_fields = ['timestamp', 'details']
    search_fields = ['user__username', 'resource_id']