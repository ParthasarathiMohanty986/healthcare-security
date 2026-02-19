from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Admin'),
        ('emergency_staff', 'Emergency Staff'),
        ('lab_technician', 'Lab Technician'),
        ('receptionist', 'Receptionist'),
    ]

    DEPARTMENT_CHOICES = [
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('psychiatry', 'Psychiatry'),
        ('icu', 'ICU'),
        ('emergency', 'Emergency'),
        ('general', 'General'),
        ('laboratory', 'Laboratory'),
    ]

    CLEARANCE_CHOICES = [
        (1, 'Level 1 - Basic'),
        (2, 'Level 2 - Standard'),
        (3, 'Level 3 - Advanced'),
        (4, 'Level 4 - Critical'),
        (5, 'Level 5 - Emergency Override'),
    ]

    # Core attributes
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='nurse'
    )
    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES,
        default='general'
    )
    specialization = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    clearance_level = models.IntegerField(
        choices=CLEARANCE_CHOICES,
        default=1
    )

    # Hospital info
    hospital_affiliation = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    certifications = models.TextField(
        blank=True,
        null=True,
        help_text="Comma separated certifications"
    )

    # Working hours
    working_hours_start = models.TimeField(
        null=True,
        blank=True
    )
    working_hours_end = models.TimeField(
        null=True,
        blank=True
    )

    # Location
    current_location = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # Flags
    is_emergency_authorized = models.BooleanField(
        default=False,
        help_text="Can this user request Emergency Access Tokens?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name()} | {self.role} | {self.department}"

    def get_certifications_list(self):
        if self.certifications:
            return [c.strip() for c in self.certifications.split(',')]
        return []