"""
Blockchain service for handling Ethereum-based audit logs via Infura
"""
import json
import logging
from typing import Dict, Any, Optional
from web3 import Web3
from django.conf import settings

logger = logging.getLogger(__name__)


class BlockchainAuditService:
    """
    Service to interact with Ethereum blockchain for storing audit logs
    Uses Infura as the provider
    """

    def __init__(self):
        """Initialize Web3 connection with Infura"""
        self.infura_url = settings.INFURA_URL
        self.private_key = settings.BLOCKCHAIN_PRIVATE_KEY
        self.contract_address = settings.CONTRACT_ADDRESS
        self.contract_abi = json.loads(settings.CONTRACT_ABI)
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.infura_url))
        
        if not self.w3.is_connected():
            logger.error("Failed to connect to Infura")
            raise ConnectionError("Could not connect to Infura endpoint")
        
        # Get account from private key
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=self.contract_abi
        )
        
        logger.info(f"Blockchain service initialized. Account: {self.account.address}")

    def create_audit_log(
        self,
        user_address: str,
        action: str,
        resource_type: str,
        resource_id: str,
        access_granted: bool,
        is_emergency: bool,
        details: str,
        ip_address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create an audit log entry on the blockchain
        
        Args:
            user_address: Ethereum address of the user
            action: Type of action performed
            resource_type: Type of resource accessed
            resource_id: ID of the resource
            access_granted: Whether access was granted
            is_emergency: Whether this was an emergency access
            details: Additional details in JSON format
            ip_address: IP address of the requester
        
        Returns:
            Transaction receipt if successful, None otherwise
        """
        try:
            # Convert user address to checksum
            user_address = Web3.to_checksum_address(user_address)
            
            # Build transaction
            transaction = self.contract.functions.createAuditLog(
                user_address,
                action,
                resource_type,
                resource_id,
                access_granted,
                is_emergency,
                details,
                ip_address
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key=self.private_key
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            logger.info(f"Audit log created on blockchain. TX Hash: {tx_hash.hex()}")
            
            return {
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber'],
                'gas_used': tx_receipt['gasUsed'],
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error creating audit log on blockchain: {str(e)}")
            return None

    def get_audit_log(self, log_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific audit log from the blockchain
        
        Args:
            log_id: ID of the log to retrieve
        
        Returns:
            Log data if found, None otherwise
        """
        try:
            log_data = self.contract.functions.getAuditLog(log_id).call()
            return self._format_log_data(log_data)
        except Exception as e:
            logger.error(f"Error retrieving audit log {log_id}: {str(e)}")
            return None

    def get_all_logs(self, start_index: int = 0, limit: int = 50) -> Optional[list]:
        """
        Retrieve multiple audit logs from the blockchain (paginated)
        
        Args:
            start_index: Starting index for pagination
            limit: Number of logs to retrieve
        
        Returns:
            List of log data if successful, None otherwise
        """
        try:
            logs = self.contract.functions.getAllLogs(start_index, limit).call()
            return [self._format_log_data(log) for log in logs]
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {str(e)}")
            return None

    def get_user_logs(self, user_address: str, start_index: int = 0, limit: int = 50) -> Optional[list]:
        """
        Retrieve audit logs for a specific user from the blockchain
        
        Args:
            user_address: Ethereum address of the user
            start_index: Starting index for pagination
            limit: Number of logs to retrieve
        
        Returns:
            List of log data if successful, None otherwise
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            logs = self.contract.functions.getUserLogs(user_address, start_index, limit).call()
            return [self._format_log_data(log) for log in logs]
        except Exception as e:
            logger.error(f"Error retrieving user logs: {str(e)}")
            return None

    def get_total_logs(self) -> Optional[int]:
        """Get total number of logs stored on blockchain"""
        try:
            return self.contract.functions.getTotalLogs().call()
        except Exception as e:
            logger.error(f"Error getting total logs: {str(e)}")
            return None

    def get_user_log_count(self, user_address: str) -> Optional[int]:
        """Get count of logs for a specific user"""
        try:
            user_address = Web3.to_checksum_address(user_address)
            return self.contract.functions.getUserLogCount(user_address).call()
        except Exception as e:
            logger.error(f"Error getting user log count: {str(e)}")
            return None

    def verify_log(self, log_id: int) -> bool:
        """Verify if a log exists on the blockchain (immutability check)"""
        try:
            return self.contract.functions.verifyLog(log_id).call()
        except Exception as e:
            logger.error(f"Error verifying log {log_id}: {str(e)}")
            return False

    def authorize_writer(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Authorize a new writer address (e.g., another backend service)
        Only the contract owner can call this
        
        Args:
            address: Ethereum address to authorize
        
        Returns:
            Transaction receipt if successful, None otherwise
        """
        try:
            address = Web3.to_checksum_address(address)
            
            transaction = self.contract.functions.authorizeWriter(address).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key=self.private_key
            )
            
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            logger.info(f"Writer authorized: {address}")
            
            return {
                'transaction_hash': tx_hash.hex(),
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error authorizing writer: {str(e)}")
            return None

    @staticmethod
    def _format_log_data(log_tuple) -> Dict[str, Any]:
        """Format log data from blockchain into dictionary"""
        return {
            'logId': log_tuple[0],
            'user': log_tuple[1],
            'action': log_tuple[2],
            'resourceType': log_tuple[3],
            'resourceId': log_tuple[4],
            'accessGranted': log_tuple[5],
            'isEmergency': log_tuple[6],
            'details': log_tuple[7],
            'timestamp': log_tuple[8],
            'ipAddress': log_tuple[9],
        }

    def get_account_balance(self) -> Optional[float]:
        """Get balance of the account in ETH"""
        try:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            logger.error(f"Error getting account balance: {str(e)}")
            return None

    def get_network_info(self) -> Dict[str, Any]:
        """Get information about the connected network"""
        try:
            return {
                'chainId': self.w3.eth.chain_id,
                'latestBlock': self.w3.eth.block_number,
                'gasPrice': self.w3.from_wei(self.w3.eth.gas_price, 'gwei'),
                'account': self.account.address,
                'accountBalance': self.get_account_balance(),
            }
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}")
            return {}
