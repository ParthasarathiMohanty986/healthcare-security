from django.db import models
from authentication.models import User


class Patient(models.Model):
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    # Basic Info
    patient_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    contact_number = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Assigned Doctor
    assigned_doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"


class EHRRecord(models.Model):

    SENSITIVITY_CHOICES = [
        (1, 'Level 1 - General'),
        (2, 'Level 2 - Standard'),
        (3, 'Level 3 - Sensitive'),
        (4, 'Level 4 - Highly Sensitive'),
        (5, 'Level 5 - Critical'),
    ]

    RECORD_TYPE_CHOICES = [
        ('general', 'General Health'),
        ('mental_health', 'Mental Health'),
        ('genetic', 'Genetic Information'),
        ('substance', 'Substance Abuse'),
        ('chronic', 'Chronic Condition'),
        ('surgical', 'Surgical History'),
        ('emergency', 'Emergency Record'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='ehr_records'
    )
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        default='general'
    )
    sensitivity_level = models.IntegerField(
        choices=SENSITIVITY_CHOICES,
        default=1
    )

    # Encrypted content fields
    diagnosis = models.TextField()
    treatment_plan = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # Access control flags
    required_clearance_level = models.IntegerField(default=1)
    required_department = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    patient_consent = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_records'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} - {self.record_type} (Sensitivity: {self.sensitivity_level})"


class MedicalReport(models.Model):

    REPORT_TYPE_CHOICES = [
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('blood_test', 'Blood Test'),
        ('urine_test', 'Urine Test'),
        ('ecg', 'ECG'),
        ('ct_scan', 'CT Scan'),
        ('biopsy', 'Biopsy'),
        ('other', 'Other'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_reports'
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    findings = models.TextField(blank=True, null=True)

    # Access control
    sensitivity_level = models.IntegerField(default=1)
    required_clearance_level = models.IntegerField(default=1)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.report_type} - {self.title}"


class LabResult(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='lab_results'
    )
    test_name = models.CharField(max_length=200)
    test_date = models.DateField()
    result_value = models.CharField(max_length=200)
    normal_range = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    is_abnormal = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    # Access control
    sensitivity_level = models.IntegerField(default=1)
    required_clearance_level = models.IntegerField(default=1)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_lab_results'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.test_name} - {self.test_date}"