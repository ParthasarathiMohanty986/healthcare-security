from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
import logging

from .blockchain_service import BlockchainAuditService
from .models import BlockchainAuditLog, BlockchainTransaction

logger = logging.getLogger(__name__)


class BlockchainNetworkInfoView(APIView):
    """Get network and account information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            blockchain_service = BlockchainAuditService()
            info = blockchain_service.get_network_info()
            return Response({
                'status': 'success',
                'data': info
            })
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlockchainAuditLogsView(APIView):
    """Retrieve audit logs from blockchain"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            start_index = int(request.query_params.get('start', 0))
            limit = int(request.query_params.get('limit', 50))
            
            blockchain_service = BlockchainAuditService()
            logs = blockchain_service.get_all_logs(start_index, limit)
            
            if logs is None:
                return Response(
                    {'error': 'Failed to retrieve logs from blockchain'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            total_logs = blockchain_service.get_total_logs()
            
            return Response({
                'status': 'success',
                'total': total_logs,
                'logs': logs
            })
        except Exception as e:
            logger.error(f"Error retrieving blockchain logs: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlockchainUserLogsView(APIView):
    """Retrieve audit logs for a specific user from blockchain"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_address):
        try:
            start_index = int(request.query_params.get('start', 0))
            limit = int(request.query_params.get('limit', 50))
            
            blockchain_service = BlockchainAuditService()
            logs = blockchain_service.get_user_logs(user_address, start_index, limit)
            
            if logs is None:
                return Response(
                    {'error': 'Failed to retrieve user logs from blockchain'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            log_count = blockchain_service.get_user_log_count(user_address)
            
            return Response({
                'status': 'success',
                'user_address': user_address,
                'total': log_count,
                'logs': logs
            })
        except Exception as e:
            logger.error(f"Error retrieving user blockchain logs: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlockchainLogDetailView(APIView):
    """Retrieve a specific audit log from blockchain"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, log_id):
        try:
            blockchain_service = BlockchainAuditService()
            log = blockchain_service.get_audit_log(log_id)
            
            if log is None:
                return Response(
                    {'error': 'Log not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                'status': 'success',
                'data': log
            })
        except Exception as e:
            logger.error(f"Error retrieving blockchain log {log_id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlockchainVerifyLogView(APIView):
    """Verify authenticity of a log on blockchain"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, log_id):
        try:
            blockchain_service = BlockchainAuditService()
            is_valid = blockchain_service.verify_log(log_id)
            
            return Response({
                'status': 'success',
                'log_id': log_id,
                'verified': is_valid,
                'immutable': is_valid
            })
        except Exception as e:
            logger.error(f"Error verifying blockchain log {log_id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlockchainTransactionStatusView(APIView):
    """Check status of a blockchain transaction"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, tx_hash):
        try:
            transaction = BlockchainTransaction.objects.filter(
                transaction_hash=tx_hash
            ).first()
            
            if not transaction:
                return Response(
                    {'error': 'Transaction not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                'status': 'success',
                'transaction': {
                    'hash': transaction.transaction_hash,
                    'status': transaction.status,
                    'block_number': transaction.block_number,
                    'gas_used': transaction.gas_used,
                    'created_at': transaction.created_at,
                    'confirmed_at': transaction.confirmed_at,
                    'error': transaction.error_message
                }
            })
        except Exception as e:
            logger.error(f"Error retrieving transaction status: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
