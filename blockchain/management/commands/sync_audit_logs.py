from django.core.management.base import BaseCommand
from django.conf import settings
from audit.models import AuditLog
from blockchain.models import BlockchainAuditLog, BlockchainTransaction
from blockchain.blockchain_service import BlockchainAuditService
import logging
import json

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync audit logs to blockchain'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all unsynced logs',
        )
        parser.add_argument(
            '--log-id',
            type=int,
            help='Sync specific log by ID',
        )
        parser.add_argument(
            '--user-address',
            type=str,
            default='0x0000000000000000000000000000000000000000',
            help='Default user address for syncing',
        )

    def handle(self, *args, **options):
        if not settings.BLOCKCHAIN_ENABLED:
            self.stdout.write(
                self.style.ERROR('Blockchain is not enabled. Check BLOCKCHAIN_ENABLED setting.')
            )
            return

        try:
            blockchain_service = BlockchainAuditService()
            self.stdout.write(
                self.style.SUCCESS('✓ Connected to blockchain via Infura')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to connect to blockchain: {str(e)}')
            )
            return

        if options['log_id']:
            self.sync_specific_log(options['log_id'], options['user_address'], blockchain_service)
        elif options['all']:
            self.sync_all_logs(options['user_address'], blockchain_service)
        else:
            self.stdout.write(
                self.style.WARNING('Use --all to sync all logs or --log-id to sync specific log')
            )

    def sync_specific_log(self, log_id, user_address, blockchain_service):
        """Sync a specific audit log"""
        try:
            log = AuditLog.objects.filter(id=log_id).first()

            if not log:
                self.stdout.write(self.style.ERROR(f'Log {log_id} not found'))
                return

            # Check if already synced
            existing = BlockchainAuditLog.objects.filter(local_audit_log_id=log.id).first()
            if existing:
                self.stdout.write(
                    self.style.WARNING(
                        f'Log {log_id} already synced. Blockchain ID: {existing.blockchain_log_id}'
                    )
                )
                return

            # Sync to blockchain
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
                # Save transaction
                tx = BlockchainTransaction.objects.create(
                    audit_log_id=log.id,
                    transaction_hash=result['transaction_hash'],
                    block_number=result['block_number'],
                    gas_used=result['gas_used'],
                    status='CONFIRMED'
                )

                # Save blockchain audit log
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

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Log {log_id} synced successfully\n'
                        f'  Transaction: {result["transaction_hash"]}\n'
                        f'  Block: {result["block_number"]}\n'
                        f'  Gas Used: {result["gas_used"]}'
                    )
                )
            else:
                self.stdout.write(self.style.ERROR(f'✗ Failed to sync log {log_id}'))

        except Exception as e:
            logger.error(f"Error syncing log {log_id}: {str(e)}")
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))

    def sync_all_logs(self, user_address, blockchain_service):
        """Sync all unsynced audit logs"""
        try:
            # Get unsynced logs
            synced_ids = BlockchainAuditLog.objects.values_list('local_audit_log_id', flat=True)
            unsynced_logs = AuditLog.objects.exclude(id__in=synced_ids)

            total = unsynced_logs.count()
            if total == 0:
                self.stdout.write(self.style.SUCCESS('✓ All logs are already synced!'))
                return

            self.stdout.write(f'Starting sync for {total} logs...\n')

            synced_count = 0
            failed_count = 0

            for log in unsynced_logs:
                try:
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

                        synced_count += 1
                        self.stdout.write(f'  ✓ Log {log.id}: {result["transaction_hash"]}')
                    else:
                        failed_count += 1
                        self.stdout.write(self.style.WARNING(f'  ✗ Log {log.id}: Sync failed'))

                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error syncing log {log.id}: {str(e)}")
                    self.stdout.write(self.style.WARNING(f'  ✗ Log {log.id}: {str(e)}'))

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Sync completed!\n'
                    f'  Synced: {synced_count}/{total}\n'
                    f'  Failed: {failed_count}/{total}'
                )
            )

        except Exception as e:
            logger.error(f"Error syncing logs: {str(e)}")
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
