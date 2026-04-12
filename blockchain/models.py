from django.db import models
from django.utils import timezone


class BlockchainTransaction(models.Model):
    """
    Model to track blockchain transactions related to audit logs
    """
    TRANSACTION_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed'),
    ]
    
    audit_log_id = models.IntegerField(null=True, blank=True)
    transaction_hash = models.CharField(max_length=255, unique=True)
    block_number = models.IntegerField(null=True, blank=True)
    gas_used = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_hash} - {self.status}"
    
    def mark_confirmed(self, block_number, gas_used):
        """Mark transaction as confirmed"""
        self.status = 'CONFIRMED'
        self.block_number = block_number
        self.gas_used = gas_used
        self.confirmed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        """Mark transaction as failed"""
        self.status = 'FAILED'
        self.error_message = error_message
        self.save()


class BlockchainAuditLog(models.Model):
    """
    Model to track audit logs stored on blockchain
    This serves as an index to the blockchain data
    """
    local_audit_log_id = models.IntegerField(unique=True)
    blockchain_log_id = models.IntegerField(null=True, blank=True)
    transaction = models.OneToOneField(
        BlockchainTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    user_address = models.CharField(max_length=255)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100, blank=True, null=True)
    resource_id = models.CharField(max_length=100, blank=True, null=True)
    access_granted = models.BooleanField(default=False)
    is_emergency = models.BooleanField(default=False)
    blockchain_timestamp = models.IntegerField(null=True, blank=True)
    synced_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-synced_at']
    
    def __str__(self):
        return f"Log {self.local_audit_log_id} - {self.action}"


class BlockchainSync(models.Model):
    """
    Model to track blockchain sync status
    """
    SYNC_STATUS = [
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    sync_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='RUNNING')
    last_sync_block = models.IntegerField(default=0)
    synced_items = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.sync_type} - {self.status}"
