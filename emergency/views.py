from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .eat_handler import EATHandler
from .models import EmergencyAccessToken


class RequestEATView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        patient_id = request.data.get('patient_id')
        reason = request.data.get('reason')

        if not patient_id or not reason:
            return Response(
                {'error': 'patient_id and reason are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        handler = EATHandler()
        result = handler.generate_token(request.user, patient_id, reason)

        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_403_FORBIDDEN)


class ValidateEATView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_id = request.data.get('token_id')

        if not token_id:
            return Response(
                {'error': 'token_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        handler = EATHandler()
        result = handler.validate_token(token_id, request.user)

        return Response(result)


class MyTokensView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tokens = EmergencyAccessToken.objects.filter(
            requested_by=request.user
        ).values(
            'token_id', 'patient_id', 'status',
            'issued_at', 'expires_at', 'times_used',
            'reason'
        )

        return Response({
            'tokens': list(tokens)
        })