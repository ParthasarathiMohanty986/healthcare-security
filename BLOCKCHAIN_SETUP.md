# Blockchain-Based Healthcare Audit Logs Integration Guide

This guide walks you through integrating a decentralized blockchain-based audit logging system with your Django healthcare security project using Ethereum, Infura, and Remix IDE.

## Overview

The system architecture:
- **Smart Contract**: Stores immutable audit logs on Ethereum blockchain
- **Infura**: Provides access to Ethereum network without running a full node
- **Django Backend**: Writes audit logs to both database and blockchain
- **Remix IDE**: Online IDE for deploying smart contracts

## Prerequisites

1. **MetaMask Wallet**
   - Download MetaMask browser extension
   - Create or import a wallet
   - Save your private key safely!

2. **Infura Account**
   - Sign up at https://infura.io
   - Create a new project
   - Copy your Project ID

3. **Test ETH (for Sepolia testnet)**
   - Get free test ETH from: https://sepoliafaucet.com
   - Use your MetaMask wallet address

## Step 1: Deploy Smart Contract using Remix IDE

### 1.1 Go to Remix IDE
- Visit: https://remix.ethereum.org

### 1.2 Create New File
- Click "Create New File" 
- Name it: `AuditLog.sol`
- Copy the entire content from `blockchain/AuditLog.sol`
- Paste it into the Remix editor

### 1.3 Compile Smart Contract
- In the left sidebar, click the **Solidity Compiler** icon
- Select version: `^0.8.0` (or any 0.8.x)
- Click **Compile AuditLog.sol**

### 1.4 Deploy to Sepolia Testnet

**Important**: Do NOT use mainnet until you test thoroughly!

Steps:
1. Click the **Deploy & Run Transactions** icon
2. In "Environment" dropdown, select **Injected Provider - MetaMask**
3. Make sure MetaMask is set to **Sepolia testnet**
4. Make sure you have test ETH in your wallet
5. Click **Deploy**
6. MetaMask will ask for confirmation - approve the transaction
7. Copy the deployed contract address from the contract panel

### 1.5 Save Contract Address
```
CONTRACT_ADDRESS=0x_your_deployed_contract_address_here
```

Keep this safe! You'll need it for Django configuration.

---

## Step 2: Configure Django Backend

### 2.1 Install Web3.py Dependency

Update your `requirements.txt`:
```
web3>=6.0.0
python-dotenv>=0.19.0
```

Install:
```bash
pip install web3 python-dotenv
```

### 2.2 Create .env File

Copy `.env.blockchain.example` to `.env`

```bash
cp .env.blockchain.example .env
```

Edit `.env` with your values:
```
INFURA_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
BLOCKCHAIN_PRIVATE_KEY=your_private_key_without_0x
CONTRACT_ADDRESS=0x_deployed_contract_address
BLOCKCHAIN_NETWORK=sepolia
BLOCKCHAIN_ENABLED=true
```

⚠️ **SECURITY WARNING**: 
- Never share your private key!
- Never commit `.env` to version control
- Use environment variables for production, not .env files

### 2.3 Update Django Settings

Add to `config/settings.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Blockchain Configuration
BLOCKCHAIN_ENABLED = os.getenv('BLOCKCHAIN_ENABLED', 'false').lower() == 'true'
INFURA_URL = os.getenv('INFURA_URL', '')
BLOCKCHAIN_PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY', '')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')

# Get ABI from blockchain/ABI.json (you'll need to create this)
with open(os.path.join(BASE_DIR, 'blockchain', 'ABI.json'), 'r') as f:
    CONTRACT_ABI = f.read()

# Add blockchain app to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'blockchain',
]
```

### 2.4 Get Contract ABI from Remix

The ABI (Application Binary Interface) is needed to interact with your contract:

1. Go back to Remix IDE
2. In **Solidity Compiler** panel, after compile, click **ABI** button
3. Copy the entire ABI JSON
4. Create file `blockchain/ABI.json`
5. Paste the ABI there

Example structure:
```json
[
  {
    "inputs": [...],
    "name": "createAuditLog",
    ...
  },
  ...
]
```

### 2.5 Update URL Configuration

Add to `config/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...
    path('api/audit/', include('audit.urls')),
    path('api/blockchain/', include('blockchain.urls')),
]
```

### 2.6 Run Migrations

```bash
python manage.py makemigrations blockchain
python manage.py migrate
```

---

## Step 3: Using the System

### 3.1 Sync Audit Logs to Blockchain

#### Option A: Sync Specific Log

```bash
curl -X POST http://localhost:8000/api/audit/logs/1/sync-blockchain/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_address": "0x_ethereum_address"}'
```

#### Option B: Sync All Unsynced Logs

```bash
curl -X POST http://localhost:8000/api/audit/sync-all-blockchain/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_address": "0x_ethereum_address"}'
```

#### Option C: View Sync Status

```bash
curl http://localhost:8000/api/audit/blockchain-status/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3.2 Query Blockchain Logs

#### Get All Blockchain Audit Logs

```bash
curl http://localhost:8000/api/blockchain/audit-logs/?start=0&limit=50 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Specific User's Logs

```bash
curl http://localhost:8000/api/blockchain/user-logs/0x_ethereum_address/?start=0&limit=50 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Verify Log Immutability

```bash
curl http://localhost:8000/api/blockchain/audit-logs/0/verify/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3.3 Check Transaction Status

```bash
curl http://localhost:8000/api/blockchain/transactions/0x_transaction_hash/status/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3.4 Network Info

```bash
curl http://localhost:8000/api/blockchain/network-info/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Step 4: Smart Contract Functions (In Remix)

You can test functions directly in Remix:

### createAuditLog
```
user: 0x_address
action: "ACCESS_EHR"
resourceType: "Patient_Record"
resourceId: "12345"
accessGranted: true
isEmergency: false
details: "{\"reason\": \"Treatment\"}"
ipAddress: "192.168.1.1"
```

### getAuditLog
```
logId: 0
```

### getUserLogs
```
user: 0x_address
startIndex: 0
limit: 50
```

### verifyLog
```
logId: 0
```

---

## Step 5: Production Deployment

### 5.1 Move to Mainnet (WARNING: Real Money!)

1. Swap Sepolia setup in `.env` to Mainnet endpoint:
```
INFURA_URL=https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID
```

2. Deploy contract to mainnet using Remix (requires real ETH for gas)

3. Update `CONTRACT_ADDRESS` in `.env`

### 5.2 Security Best Practices

- Store private key in AWS Secrets Manager / HashiCorp Vault
- Use multiple signatures (multisig wallet)
- Implement rate limiting on sync endpoints
- Monitor gas prices before bulk syncing
- Test on testnet first!

### 5.3 Environment Variables (Production)

Use your platform's secret management:
```
AWS: AWS Secrets Manager
GCP: Google Secret Manager
Azure: Azure Key Vault
DigitalOcean: DigitalOcean App Platform Secrets
```

---

## Step 6: Monitoring & Maintenance

### 6.1 Check Transaction Status

Monitor pending transactions in Django admin:
```
http://localhost:8000/admin/blockchain/blockchaintransaction/
```

### 6.2 Verify Contract on Etherscan

After deployment:
1. Go to https://sepolia.etherscan.io (for testnet) or https://etherscan.io (mainnet)
2. Search for your contract address
3. Verify source code for transparency

### 6.3 Gas Optimization

- Monitor gas prices using `GET /api/blockchain/network-info/`
- Batch multiple logs in batch sync operations
- Consider implementing queue system for high volume

---

## Troubleshooting

### Issue: "Connection failed to Infura"
- Check INFURA_URL is correct
- Verify project ID is valid
- Check internet connection

### Issue: "Not authorized to write logs"
- Make sure your address is authorized in contract
- Use `authorizeWriter()` function in Remix for new addresses

### Issue: "Transaction reverted"
- Check you have enough test ETH for gas
- Verify contract address is correct
- Check ABI matches deployed contract

### Issue: "Private key invalid"
- Remove '0x' prefix from private key
- Ensure it's hex format (0-9, a-f)
- Don't include quotes around it

---

## Cost Estimation

### Sepolia Testnet
- Free! Uses test ETH

### Ethereum Mainnet
- ~$1-10 per log entry (varies with network congestion)
- Consider batching logs to reduce costs
- Use Layer 2 solutions (Polygon, Arbitrum) for cheaper storage

---

## Next Steps

1. ✅ Deploy contract to Sepolia testnet
2. ✅ Configure Django backend
3. ✅ Test sync endpoints
4. ✅ Implement automatic syncing on audit log creation
5. ✅ Deploy to production (after thorough testing!)

---

## Additional Resources

- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Infura Docs](https://docs.infura.io/)
- [Remix IDE Guide](https://remix-ide.readthedocs.io/)
- [Solidity Best Practices](https://docs.soliditylang.org/)
- [Etherscan Explorer](https://etherscan.io/)

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review contract ABI in Remix
3. Verify all environment variables
4. Check Infura status page
5. Review transaction hash on Etherscan
