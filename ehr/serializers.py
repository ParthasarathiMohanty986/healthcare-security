from rest_framework import serializers
from .models import Patient, EHRRecord, MedicalReport, LabResult


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'first_name', 'last_name',
            'date_of_birth', 'blood_group', 'contact_number',
            'emergency_contact', 'assigned_doctor'
        ]


class EHRRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EHRRecord
        fields = [
            'id', 'patient', 'record_type', 'sensitivity_level',
            'diagnosis', 'treatment_plan', 'medications', 'notes',
            'required_clearance_level', 'required_department',
            'patient_consent', 'created_at'
        ]


class MedicalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalReport
        fields = [
            'id', 'patient', 'report_type', 'title',
            'description', 'findings', 'sensitivity_level',
            'required_clearance_level', 'created_at'
        ]


class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = [
            'id', 'patient', 'test_name', 'test_date',
            'result_value', 'normal_range', 'unit',
            'is_abnormal', 'remarks', 'sensitivity_level',
            'required_clearance_level', 'created_at'
        ]