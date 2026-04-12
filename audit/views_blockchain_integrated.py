"""
Updated audit views with blockchain integration
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import logging
import json

from .models import AuditLog
from blockchain.blockchain_service import BlockchainAuditService
from blockchain.models import BlockchainTransaction, BlockchainAuditLog

logger = logging.getLogger(__name__)


class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve audit logs from both database and blockchain"""
        try:
            logs = AuditLog.objects.all()[:50]
            data = []
            
            for log in logs:
                blockchain_record = BlockchainAuditLog.objects.filter(
                    local_audit_log_id=log.id
                ).first()
                
                log_data = {
                    'id': log.id,
                    'user': str(log.user),
                    'action': log.action,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'access_granted': log.access_granted,
                    'is_emergency': log.is_emergency,
                    'timestamp': log.timestamp,
                    'details': log.details,
                    'ip_address': log.ip_address,
                    'blockchain': {
                        'synced': blockchain_record is not None,
                        'blockchain_log_id': blockchain_record.blockchain_log_id if blockchain_record else None,
                        'transaction_hash': blockchain_record.transaction.transaction_hash if blockchain_record and blockchain_record.transaction else None,
                        'status': blockchain_record.transaction.status if blockchain_record and blockchain_record.transaction else None,
                    }
                }
                data.append(log_data)
            
            return Response({
                'status': 'success',
                'count': len(data),
                'logs': data
            })
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AuditLogDetailView(APIView):
    """Get details of a specific audit log"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, log_id):
        try:
            log = AuditLog.objects.filter(id=log_id).first()
            
            if not log:
                return Response(
                    {'error': 'Log not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            blockchain_record = BlockchainAuditLog.objects.filter(
                local_audit_log_id=log.id
            ).first()
            
            log_data = {
                'id': log.id,
                'user': str(log.user),
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'access_granted': log.access_granted,
                'is_emergency': log.is_emergency,
                'timestamp': log.timestamp,
                'details': log.details,
                'ip_address': log.ip_address,
                'blockchain': {
                    'synced': blockchain_record is not None,
                    'blockchain_log_id': blockchain_record.blockchain_log_id if blockchain_record else None,
                    'transaction_hash': blockchain_record.transaction.transaction_hash if blockchain_record and blockchain_record.transaction else None,
                    'status': blockchain_record.transaction.status if blockchain_record and blockchain_record.transaction else None,
                }
            }
            
            return Response({
                'status': 'success',
                'data': log_data
            })
        except Exception as e:
            logger.error(f"Error retrieving audit log: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SyncAuditLogToBlockchainView(APIView):
    """Manually sync audit logs to blockchain"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, log_id):
        """Sync a specific audit log to blockchain"""
        try:
            log = AuditLog.objects.filter(id=log_id).first()
            
            if not log:
                return Response(
                    {'error': 'Log not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if already synced
            existing_sync = BlockchainAuditLog.objects.filter(
                local_audit_log_id=log.id
            ).first()
            
            if existing_sync:
                return Response({
                    'status': 'already_synced',
                    'blockchain_log_id': existing_sync.blockchain_log_id,
                    'transaction_hash': existing_sync.transaction.transaction_hash if existing_sync.transaction else None
                })
            
            # Convert user to Ethereum address (you may need to adjust this based on your user model)
            user_address = request.data.get('user_address')
            
            if not user_address:
                return Response(
                    {'error': 'user_address is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Sync to blockchain
            blockchain_service = BlockchainAuditService()
            details_json = json.dumps(log.details) if log.details else '{}'
            
            result = blockchain_service.create_audit_log(
                user_address=user_address,
                action=log.action,
                resource_type=log.resource_type or '',
                resource_id=log.resource_id or '',
                access_granted=log.access_granted,
                is_emergency=log.is_emergency,
                details=details_json,
                ip_address=log.ip_address or ''
            )
            
            if result and result.get('status') == 'success':
                # Create blockchain transaction record
                tx = BlockchainTransaction.objects.create(
                    audit_log_id=log.id,
                    transaction_hash=result['transaction_hash'],
                    block_number=result['block_number'],
                    gas_used=result['gas_used'],
                    status='CONFIRMED'
                )
                
                # Create blockchain audit log record
                bc_log = BlockchainAuditLog.objects.create(
                    local_audit_log_id=log.id,
                    transaction=tx,
                    user_address=user_address,
                    action=log.action,
                    resource_type=log.resource_type,
                    resource_id=log.resource_id,
                    access_granted=log.access_granted,
                    is_emergency=log.is_emergency
                )
                
                return Response({
                    'status': 'success',
                    'message': 'Log synced to blockchain',
                    'transaction_hash': result['transaction_hash'],
                    'block_number': result['block_number'],
                    'gas_used': result['gas_used']
                })
            else:
                return Response(
                    {'error': 'Failed to sync log to blockchain'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            logger.error(f"Error syncing audit log to blockchain: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SyncAllAuditLogsView(APIView):
    """Sync all unsynced audit logs to blockchain (batch operation)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Sync all unsynced audit logs to blockchain"""
        try:
            # Get unsynced logs
            synced_log_ids = BlockchainAuditLog.objects.values_list('local_audit_log_id', flat=True)
            unsynced_logs = AuditLog.objects.exclude(id__in=synced_log_ids)
            
            blockchain_service = BlockchainAuditService()
            results = []
            
            for log in unsynced_logs:
                try:
                    user_address = request.data.get('user_address') or str(log.user.id)
                    details_json = json.dumps(log.details) if log.details else '{}'
                    
                    result = blockchain_service.create_audit_log(
                        user_address=user_address,
                        action=log.action,
                        resource_type=log.resource_type or '',
                        resource_id=log.resource_id or '',
                        access_granted=log.access_granted,
                        is_emergency=log.is_emergency,
                        details=details_json,
                        ip_address=log.ip_address or ''
                    )
                    
                    if result and result.get('status') == 'success':
                        tx = BlockchainTransaction.objects.create(
                            audit_log_id=log.id,
                            transaction_hash=result['transaction_hash'],
                            block_number=result['block_number'],
                            gas_used=result['gas_used'],
                            status='CONFIRMED'
                        )
                        
                        BlockchainAuditLog.objects.create(
                            local_audit_log_id=log.id,
                            transaction=tx,
                            user_address=user_address,
                            action=log.action,
                            resource_type=log.resource_type,
                            resource_id=log.resource_id,
                            access_granted=log.access_granted,
                            is_emergency=log.is_emergency
                        )
                        
                        results.append({
                            'log_id': log.id,
                            'status': 'success',
                            'transaction_hash': result['transaction_hash']
                        })
                except Exception as e:
                    logger.error(f"Error syncing log {log.id}: {str(e)}")
                    results.append({
                        'log_id': log.id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return Response({
                'status': 'completed',
                'total_synced': len([r for r in results if r['status'] == 'success']),
                'total_failed': len([r for r in results if r['status'] == 'failed']),
                'results': results
            })
        
        except Exception as e:
            logger.error(f"Error syncing audit logs: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlockchainSyncStatusView(APIView):
    """Get overall blockchain sync status"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            total_logs = AuditLog.objects.count()
            synced_logs = BlockchainAuditLog.objects.count()
            unsynced_logs = total_logs - synced_logs
            
            pending_txs = BlockchainTransaction.objects.filter(status='PENDING').count()
            confirmed_txs = BlockchainTransaction.objects.filter(status='CONFIRMED').count()
            failed_txs = BlockchainTransaction.objects.filter(status='FAILED').count()
            
            return Response({
                'status': 'success',
                'audit_logs': {
                    'total': total_logs,
                    'synced': synced_logs,
                    'unsynced': unsynced_logs,
                    'sync_percentage': (synced_logs / total_logs * 100) if total_logs > 0 else 0
                },
                'transactions': {
                    'pending': pending_txs,
                    'confirmed': confirmed_txs,
                    'failed': failed_txs
                }
            })
        except Exception as e:
            logger.error(f"Error getting sync status: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
