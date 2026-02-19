from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog


class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AuditLog.objects.all()[:50]
        data = []
        for log in logs:
            data.append({
                'id': log.id,
                'user': str(log.user),
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'access_granted': log.access_granted,
                'is_emergency': log.is_emergency,
                'timestamp': log.timestamp,
                'details': log.details,
            })
        return Response({'logs': data})