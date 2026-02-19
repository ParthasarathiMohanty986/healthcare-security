from django.db import models
from authentication.models import User


class AuditLog(models.Model):

    ACTION_CHOICES = [
        ('ACCESS_EHR', 'Access EHR Record'),
        ('ACCESS_REPORT', 'Access Medical Report'),
        ('ACCESS_LAB', 'Access Lab Result'),
        ('EMERGENCY_TOKEN_ISSUED', 'Emergency Token Issued'),
        ('EMERGENCY_TOKEN_USED', 'Emergency Token Used'),
        ('EMERGENCY_TOKEN_EXPIRED', 'Emergency Token Expired'),
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, blank=True, null=True)
    resource_id = models.CharField(max_length=50, blank=True, null=True)
    access_granted = models.BooleanField(default=False)
    is_emergency = models.BooleanField(default=False)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        status = "✅ GRANTED" if self.access_granted else "❌ DENIED"
        return f"{self.timestamp} | {self.user} | {self.action} | {status}"