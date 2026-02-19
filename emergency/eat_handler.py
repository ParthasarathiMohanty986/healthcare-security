from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import EmergencyAccessToken
from audit.models import AuditLog


class EATHandler:
    """
    Handles Emergency Access Token generation,
    validation, and usage
    """

    def generate_token(self, user, patient_id: str, reason: str) -> dict:
        """
        Generate a new Emergency Access Token
        """

        # Check if user is authorized for emergency access
        if not user.is_emergency_authorized:
            return {
                'success': False,
                'message': 'You are not authorized to request Emergency Access Tokens',
            }

        # Check if there's already an active token for this patient
        existing = EmergencyAccessToken.objects.filter(
            requested_by=user,
            patient_id=patient_id,
            status='active',
            expires_at__gt=timezone.now()
        ).first()

        if existing:
            return {
                'success': True,
                'message': 'Active token already exists',
                'token_id': str(existing.token_id),
                'expires_at': existing.expires_at,
                'remaining_time': existing.get_remaining_time(),
                'already_existed': True,
            }

        # Generate new token
        validity_minutes = getattr(
            settings, 'EMERGENCY_TOKEN_VALIDITY_MINUTES', 10
        )
        expires_at = timezone.now() + timedelta(minutes=validity_minutes)

        token = EmergencyAccessToken.objects.create(
            requested_by=user,
            patient_id=patient_id,
            reason=reason,
            expires_at=expires_at,
        )

        # Log it
        AuditLog.objects.create(
            user=user,
            action='EMERGENCY_TOKEN_ISSUED',
            resource_type='patient',
            resource_id=patient_id,
            access_granted=True,
            is_emergency=True,
            details={
                'token_id': str(token.token_id),
                'reason': reason,
                'expires_at': str(expires_at),
                'validity_minutes': validity_minutes,
            }
        )

        return {
            'success': True,
            'message': f'Emergency Access Token generated successfully',
            'token_id': str(token.token_id),
            'issued_at': token.issued_at,
            'expires_at': token.expires_at,
            'remaining_time': token.get_remaining_time(),
            'validity_minutes': validity_minutes,
            'access_scope': {
                'ehr_data': token.can_access_ehr,
                'medical_reports': token.can_access_reports,
                'lab_results': token.can_access_lab,
            }
        }

    def validate_token(self, token_id: str, user) -> dict:
        """
        Validate an Emergency Access Token
        """
        try:
            token = EmergencyAccessToken.objects.get(
                token_id=token_id,
                requested_by=user
            )
        except EmergencyAccessToken.DoesNotExist:
            return {
                'valid': False,
                'message': 'Token not found'
            }

        if token.is_valid():
            token.use_token()

            # Log usage
            AuditLog.objects.create(
                user=user,
                action='EMERGENCY_TOKEN_USED',
                resource_type='patient',
                resource_id=token.patient_id,
                access_granted=True,
                is_emergency=True,
                details={
                    'token_id': str(token.token_id),
                    'times_used': token.times_used,
                    'remaining_time': token.get_remaining_time(),
                }
            )

            return {
                'valid': True,
                'message': 'Token is valid',
                'patient_id': token.patient_id,
                'remaining_time': token.get_remaining_time(),
                'times_used': token.times_used,
                'access_scope': {
                    'ehr_data': token.can_access_ehr,
                    'medical_reports': token.can_access_reports,
                    'lab_results': token.can_access_lab,
                }
            }
        else:
            # Log expiry
            AuditLog.objects.create(
                user=user,
                action='EMERGENCY_TOKEN_EXPIRED',
                resource_type='patient',
                resource_id=token.patient_id,
                access_granted=False,
                is_emergency=True,
                details={
                    'token_id': str(token.token_id),
                    'expired_at': str(token.expires_at),
                }
            )

            return {
                'valid': False,
                'message': 'Token has expired',
                'expired_at': token.expires_at,
            }

    def revoke_token(self, token_id: str, user) -> dict:
        """
        Revoke an active token
        """
        try:
            token = EmergencyAccessToken.objects.get(
                token_id=token_id,
                requested_by=user
            )
            token.status = 'revoked'
            token.save()

            return {
                'success': True,
                'message': 'Token revoked successfully'
            }
        except EmergencyAccessToken.DoesNotExist:
            return {
                'success': False,
                'message': 'Token not found'
            }