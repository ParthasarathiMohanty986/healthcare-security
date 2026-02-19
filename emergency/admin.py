from django.contrib import admin
from .models import EmergencyAccessToken


@admin.register(EmergencyAccessToken)
class EATAdmin(admin.ModelAdmin):
    list_display = [
        'token_id', 'requested_by', 'patient_id',
        'status', 'issued_at', 'expires_at', 'times_used'
    ]
    list_filter = ['status']
    readonly_fields = [
        'token_id', 'issued_at', 'times_used', 'last_used_at'
    ]