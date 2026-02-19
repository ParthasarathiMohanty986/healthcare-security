from django.contrib import admin
from .models import Patient, EHRRecord, MedicalReport, LabResult


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'patient_id', 'first_name', 'last_name',
        'blood_group', 'assigned_doctor'
    ]
    search_fields = ['patient_id', 'first_name', 'last_name']


@admin.register(EHRRecord)
class EHRRecordAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'record_type', 'sensitivity_level',
        'required_clearance_level', 'patient_consent'
    ]
    list_filter = ['record_type', 'sensitivity_level']


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'report_type', 'title',
        'sensitivity_level', 'created_at'
    ]
    list_filter = ['report_type', 'sensitivity_level']


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'test_name', 'test_date',
        'result_value', 'is_abnormal'
    ]
    list_filter = ['is_abnormal']