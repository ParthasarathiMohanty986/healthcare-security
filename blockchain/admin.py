from django.contrib import admin
from .models import BlockchainTransaction, BlockchainAuditLog, BlockchainSync


@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_hash', 'status', 'block_number', 'gas_used', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['transaction_hash']
    readonly_fields = ['transaction_hash', 'created_at', 'confirmed_at']


@admin.register(BlockchainAuditLog)
class BlockchainAuditLogAdmin(admin.ModelAdmin):
    list_display = ['local_audit_log_id', 'blockchain_log_id', 'action', 'user_address', 'synced_at']
    list_filter = ['action', 'access_granted', 'is_emergency', 'synced_at']
    search_fields = ['user_address', 'action', 'resource_id']
    readonly_fields = ['synced_at']


@admin.register(BlockchainSync)
class BlockchainSyncAdmin(admin.ModelAdmin):
    list_display = ['sync_type', 'status', 'synced_items', 'started_at', 'completed_at']
    list_filter = ['sync_type', 'status', 'started_at']
    readonly_fields = ['started_at']
