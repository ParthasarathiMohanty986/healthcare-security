from django.db import models
from authentication.models import User
from django.utils import timezone
import uuid


class EmergencyAccessToken(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]

    # Token identification
    token_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    # Who requested it
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='emergency_tokens'
    )

    # Which patient
    patient_id = models.CharField(max_length=20)
    reason = models.TextField()

    # Validity
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )

    # Access scope
    can_access_ehr = models.BooleanField(default=True)
    can_access_reports = models.BooleanField(default=True)
    can_access_lab = models.BooleanField(default=True)

    # Usage tracking
    times_used = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"EAT-{str(self.token_id)[:8].upper()} | {self.requested_by} | {self.status}"

    def is_valid(self):
        now = timezone.now()
        if self.status == 'active' and self.expires_at > now:
            return True
        elif self.status == 'active' and self.expires_at <= now:
            # Auto expire
            self.status = 'expired'
            self.save()
        return False

    def use_token(self):
        self.times_used += 1
        self.last_used_at = timezone.now()
        self.save()

    def get_remaining_time(self):
        if self.is_valid():
            remaining = self.expires_at - timezone.now()
            minutes = int(remaining.total_seconds() // 60)
            seconds = int(remaining.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        return "Expired"