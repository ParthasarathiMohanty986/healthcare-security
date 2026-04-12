from django.urls import path
from .views_blockchain_integrated import (
    AuditLogView,
    AuditLogDetailView,
    SyncAuditLogToBlockchainView,
    SyncAllAuditLogsView,
    BlockchainSyncStatusView
)

urlpatterns = [
    # Original audit endpoints
    path('logs/', AuditLogView.as_view(), name='audit_logs'),
    path('logs/<int:log_id>/', AuditLogDetailView.as_view(), name='audit_log_detail'),
    
    # Blockchain sync endpoints
    path('logs/<int:log_id>/sync-blockchain/', SyncAuditLogToBlockchainView.as_view(), name='sync_log_blockchain'),
    path('sync-all-blockchain/', SyncAllAuditLogsView.as_view(), name='sync_all_blockchain'),
    path('blockchain-status/', BlockchainSyncStatusView.as_view(), name='blockchain_status'),
]