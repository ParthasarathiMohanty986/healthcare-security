from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Patient, EHRRecord, MedicalReport, LabResult
from .serializers import (
    PatientSerializer, EHRRecordSerializer,
    MedicalReportSerializer, LabResultSerializer
)
from engine.decision_point import PolicyDecisionPoint
from emergency.models import EmergencyAccessToken


def check_emergency_token(user, patient_id, token_id):
    """
    Helper to check if a valid EAT exists
    """
    if not token_id:
        return False
    try:
        token = EmergencyAccessToken.objects.get(
            token_id=token_id,
            requested_by=user,
            patient_id=patient_id,
            status='active'
        )
        return token.is_valid()
    except EmergencyAccessToken.DoesNotExist:
        return False


class PatientListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        List all patients - basic info only
        """
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response({
            'count': patients.count(),
            'patients': serializer.data
        })


class EHRAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        """
        Access EHR records for a patient
        Runs through Attribute Engine for every request
        """
        patient = get_object_or_404(Patient, patient_id=patient_id)
        is_emergency = request.query_params.get('emergency', 'false').lower() == 'true'
        token_id = request.query_params.get('token_id', None)
        location = request.query_params.get('location', None)

        # Check emergency token
        has_valid_eat = check_emergency_token(request.user, patient_id, token_id)
        if has_valid_eat:
            is_emergency = True

        # Get all EHR records for patient
        records = EHRRecord.objects.filter(patient=patient)

        pdp = PolicyDecisionPoint()
        accessible_records = []
        denied_records = []

        for record in records:
            decision = pdp.make_decision(
                user=request.user,
                resource_type='ehr',
                resource=record,
                is_emergency=is_emergency,
                location=location
            )

            if decision['access_granted']:
                data = EHRRecordSerializer(record).data
                data['access_decision'] = {
                    'granted': True,
                    'checks_passed': decision['checks_passed'],
                }
                accessible_records.append(data)
            else:
                denied_records.append({
                    'record_id': record.id,
                    'record_type': record.record_type,
                    'sensitivity_level': record.sensitivity_level,
                    'access_decision': {
                        'granted': False,
                        'checks_failed': decision['checks_failed'],
                        'reasons': decision['reasons'],
                    }
                })

        return Response({
            'patient': PatientSerializer(patient).data,
            'is_emergency': is_emergency,
            'has_emergency_token': has_valid_eat,
            'accessible_records': accessible_records,
            'denied_records': denied_records,
            'summary': {
                'total_records': records.count(),
                'accessible': len(accessible_records),
                'denied': len(denied_records),
            }
        })


class MedicalReportAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        """
        Access Medical Reports for a patient
        """
        patient = get_object_or_404(Patient, patient_id=patient_id)
        is_emergency = request.query_params.get('emergency', 'false').lower() == 'true'
        token_id = request.query_params.get('token_id', None)
        location = request.query_params.get('location', None)

        has_valid_eat = check_emergency_token(request.user, patient_id, token_id)
        if has_valid_eat:
            is_emergency = True

        reports = MedicalReport.objects.filter(patient=patient)
        pdp = PolicyDecisionPoint()

        accessible = []
        denied = []

        for report in reports:
            decision = pdp.make_decision(
                user=request.user,
                resource_type='report',
                resource=report,
                is_emergency=is_emergency,
                location=location
            )

            if decision['access_granted']:
                data = MedicalReportSerializer(report).data
                data['access_decision'] = {
                    'granted': True,
                    'checks_passed': decision['checks_passed'],
                }
                accessible.append(data)
            else:
                denied.append({
                    'report_id': report.id,
                    'report_type': report.report_type,
                    'access_decision': {
                        'granted': False,
                        'reasons': decision['reasons'],
                    }
                })

        return Response({
            'patient': PatientSerializer(patient).data,
            'is_emergency': is_emergency,
            'accessible_reports': accessible,
            'denied_reports': denied,
            'summary': {
                'total': reports.count(),
                'accessible': len(accessible),
                'denied': len(denied),
            }
        })


class LabResultAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        """
        Access Lab Results for a patient
        """
        patient = get_object_or_404(Patient, patient_id=patient_id)
        is_emergency = request.query_params.get('emergency', 'false').lower() == 'true'
        token_id = request.query_params.get('token_id', None)
        location = request.query_params.get('location', None)

        has_valid_eat = check_emergency_token(request.user, patient_id, token_id)
        if has_valid_eat:
            is_emergency = True

        results = LabResult.objects.filter(patient=patient)
        pdp = PolicyDecisionPoint()

        accessible = []
        denied = []

        for result in results:
            decision = pdp.make_decision(
                user=request.user,
                resource_type='lab',
                resource=result,
                is_emergency=is_emergency,
                location=location
            )

            if decision['access_granted']:
                data = LabResultSerializer(result).data
                data['access_decision'] = {
                    'granted': True,
                    'checks_passed': decision['checks_passed'],
                }
                accessible.append(data)
            else:
                denied.append({
                    'result_id': result.id,
                    'test_name': result.test_name,
                    'access_decision': {
                        'granted': False,
                        'reasons': decision['reasons'],
                    }
                })

        return Response({
            'patient': PatientSerializer(patient).data,
            'is_emergency': is_emergency,
            'accessible_results': accessible,
            'denied_results': denied,
            'summary': {
                'total': results.count(),
                'accessible': len(accessible),
                'denied': len(denied),
            }
        })