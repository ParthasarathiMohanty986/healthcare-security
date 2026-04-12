from django.urls import path
from .views import (
    BlockchainNetworkInfoView,
    BlockchainAuditLogsView,
    BlockchainUserLogsView,
    BlockchainLogDetailView,
    BlockchainVerifyLogView,
    BlockchainTransactionStatusView
)

app_name = 'blockchain'

urlpatterns = [
    # Network information
    path('network-info/', BlockchainNetworkInfoView.as_view(), name='network-info'),
    
    # Audit logs
    path('audit-logs/', BlockchainAuditLogsView.as_view(), name='audit-logs'),
    path('audit-logs/<int:log_id>/', BlockchainLogDetailView.as_view(), name='audit-log-detail'),
    path('audit-logs/<int:log_id>/verify/', BlockchainVerifyLogView.as_view(), name='verify-log'),
    
    # User logs
    path('user-logs/<str:user_address>/', BlockchainUserLogsView.as_view(), name='user-logs'),
    
    # Transaction status
    path('transactions/<str:tx_hash>/status/', BlockchainTransactionStatusView.as_view(), name='tx-status'),
]
