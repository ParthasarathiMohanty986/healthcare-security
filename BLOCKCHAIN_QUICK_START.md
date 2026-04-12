# Blockchain Integration - Quick Start Checklist

## Pre-Requisites Setup

### Phase 1: Wallet & Infura Setup (15 minutes)
- [ ] Install MetaMask browser extension (https://metamask.io)
- [ ] Create/import Ethereum wallet in MetaMask
- [ ] **SAVE** recovery phrase in secure location
- [ ] **SAVE** private key (never share!)
- [ ] Create Infura account (https://infura.io)
- [ ] Create new Infura project
- [ ] Copy Infura Project ID

### Phase 2: Get Test ETH (5-10 minutes)
- [ ] Switch MetaMask to Sepolia testnet
- [ ] Go to https://sepoliafaucet.com
- [ ] Paste your wallet address
- [ ] Request test ETH (~0.5 ETH should be enough)
- [ ] Wait for funds to arrive (usually instant)

---

## Smart Contract Deployment (15 minutes)

### Step 1: Deploy on Remix IDE
1. [ ] Go to https://remix.ethereum.org
2. [ ] Create new file: `AuditLog.sol`
3. [ ] Copy entire content from `blockchain/AuditLog.sol`
4. [ ] In Solidity Compiler: Select version ~0.8.0
5. [ ] Click **Compile AuditLog.sol**
6. [ ] In Deploy panel:
   - [ ] Select "Injected Provider - MetaMask"
   - [ ] Confirm MetaMask is on Sepolia testnet
   - [ ] Click **Deploy**
   - [ ] Approve transaction in MetaMask

### Step 2: Copy Contract Address
- [ ] In Remix, find the deployed contract in output
- [ ] Copy the contract address (0x...)
- [ ] Save it - you'll need it in Django config

### Step 3: Get Contract ABI
1. [ ] In Solidity Compiler panel, click **ABI** button
2. [ ] Copy the entire JSON ABI
3. [ ] Replace content in `blockchain/ABI.json` with the ABI
4. [ ] Save the file

---

## Django Backend Configuration (10 minutes)

### Step 1: Install Dependencies
```bash
pip install web3>=6.0.0 python-dotenv>=0.19.0
```
- [ ] Packages installed successfully

### Step 2: Create .env File
```bash
cp .env.blockchain.example .env
```
- [ ] `.env` file created

### Step 3: Fill .env with Your Values
Edit `.env` and add:
```
INFURA_URL=https://sepolia.infura.io/v3/[YOUR_PROJECT_ID]
BLOCKCHAIN_PRIVATE_KEY=[your_private_key_without_0x]
CONTRACT_ADDRESS=[0x_deployed_contract_address]
BLOCKCHAIN_NETWORK=sepolia
BLOCKCHAIN_ENABLED=true
```

- [ ] INFURA_URL filled with your Project ID
- [ ] BLOCKCHAIN_PRIVATE_KEY filled (without 0x prefix)
- [ ] CONTRACT_ADDRESS filled (with 0x prefix)
- [ ] BLOCKCHAIN_NETWORK set to sepolia
- [ ] BLOCKCHAIN_ENABLED set to true

### Step 4: Update Django Settings
Edit `config/settings.py` and add to the very end:

```python
# Blockchain Configuration
import os
from dotenv import load_dotenv

load_dotenv()

BLOCKCHAIN_ENABLED = os.getenv('BLOCKCHAIN_ENABLED', 'false').lower() == 'true'
INFURA_URL = os.getenv('INFURA_URL', '')
BLOCKCHAIN_PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY', '')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')

# Load ABI
import json
ABI_PATH = os.path.join(BASE_DIR, 'blockchain', 'ABI.json')
try:
    with open(ABI_PATH, 'r') as f:
        CONTRACT_ABI = f.read()
except FileNotFoundError:
    CONTRACT_ABI = '[]'
    
# Add blockchain to INSTALLED_APPS if not already there
if 'blockchain' not in INSTALLED_APPS:
    INSTALLED_APPS = list(INSTALLED_APPS) + ['blockchain']
```

- [ ] Settings updated
- [ ] INSTALLED_APPS includes 'blockchain'

### Step 5: Update URL Configuration
Edit `config/urls.py`:

```python
urlpatterns = [
    # ... existing patterns ...
    path('api/audit/', include('audit.urls')),
    path('api/blockchain/', include('blockchain.urls')),
]
```

- [ ] URLs configured

### Step 6: Run Migrations
```bash
python manage.py makemigrations blockchain
python manage.py migrate
```

- [ ] Migrations completed successfully

### Step 7: Update Requirements
```bash
pip freeze > requirements.txt
```
- [ ] Requirements updated

---

## Testing the Integration (10 minutes)

### Test 1: Verify Blockchain Connection
```bash
python manage.py shell
```

```python
from blockchain.blockchain_service import BlockchainAuditService
service = BlockchainAuditService()
info = service.get_network_info()
print(info)
# Should show your account, balance, chain ID, etc.
```

- [ ] Connection successful
- [ ] Account balance shows (should be > 0)

### Test 2: Check Existing Audit Logs
```bash
python manage.py shell
from audit.models import AuditLog
logs = AuditLog.objects.all()
print(f"Total audit logs: {logs.count()}")
```

- [ ] Can retrieve audit logs

### Test 3: Sync Single Log
```bash
python manage.py sync_audit_logs --log-id 1 --user-address 0x_your_metamask_address
```

Replace `0x_your_metamask_address` with your actual MetaMask address from wallet.

- [ ] Log synced successfully
- [ ] Got transaction hash

### Test 4: API Endpoints
Get your JWT token first:
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "youruser", "password": "yourpass"}'
```

Then test blockchain endpoints:
```bash
# Get blockchain status
curl http://localhost:8000/api/blockchain/network-info/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# View synced logs
curl http://localhost:8000/api/blockchain/audit-logs/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Check sync status
curl http://localhost:8000/api/audit/blockchain-status/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

- [ ] All endpoints return data
- [ ] No authentication errors

---

## Production Deployment Checklist

### Before Going Live:

#### Security
- [ ] Private key stored in secrets manager (NOT in .env)
- [ ] Removed .env from git (check .gitignore)
- [ ] Used HTTPS endpoints only
- [ ] Tested with test ETH extensively
- [ ] No console.logs or debug keys in code

#### Testing
- [ ] Tested all sync endpoints
- [ ] Verified transaction status on Etherscan
- [ ] Tested with multiple users
- [ ] Verified data integrity

#### Environment
- [ ] Switch to Mainnet in .env (after testing!)
- [ ] Get real ETH for gas fees
- [ ] Update INFURA_URL to mainnet endpoint
- [ ] Deploy new CONTRACT_ADDRESS on mainnet
- [ ] Update all .env variables for production

#### Monitoring
- [ ] Set up transaction monitoring
- [ ] Create alerts for failed syncs
- [ ] Monitor gas prices
- [ ] Track blockchain costs

---

## Emergency Procedures

### If Transaction Fails
1. Check https://sepolia.etherscan.io (testnet) or https://etherscan.io (mainnet)
2. Search for transaction hash
3. View error reason
4. Check account balance (need ETH for gas)
5. Verify contract address is correct

### If Connection Fails
1. Check INFURA_URL is correct
2. Test Infura URL in browser (should return JSON)
3. Verify Infura project status (not disabled)
4. Check internet connection

### If Private Key Issues
1. Never use a key with 0x prefix in .env
2. Make sure it's exactly 64 hex characters
3. No quotes around the key
4. Never share or commit to git

---

## File Structure Created

```
blockchain/
├── __init__.py
├── apps.py
├── admin.py
├── models.py                    # Transaction tracking models
├── views.py                     # API endpoints
├── urls.py                      # URL routing
├── tests.py                     # Unit tests
├── blockchain_service.py        # Web3 integration
├── AuditLog.sol                 # Smart contract
├── ABI.json                     # Contract ABI (fill this!)
├── management/
│   └── commands/
│       └── sync_audit_logs.py   # CLI command
└── migrations/
    └── __init__.py

audit/
├── views_blockchain_integrated.py  # Updated views with blockchain
└── urls.py                         # Updated with blockchain routes
```

---

## Key Files to Remember

| File | Purpose |
|------|---------|
| `.env` | Your secrets (NEVER commit to git!) |
| `blockchain/ABI.json` | Contract ABI from Remix (MUST fill!) |
| `blockchain/AuditLog.sol` | Smart contract for Remix IDE |
| `blockchain/blockchain_service.py` | Django ↔ Ethereum bridge |
| `BLOCKCHAIN_SETUP.md` | Full documentation |

---

## Costs at a Glance

| Network | Cost per Log | Use Case |
|---------|--------------|----------|
| Sepolia (Testnet) | FREE | Development & Testing |
| Ethereum Mainnet | $1-10 | Production |
| Polygon | $0.01-0.1 | Lower Cost Alternative |

---

## Support Resources

| Issue | Resource |
|-------|----------|
| Smart contract questions | https://docs.soliditylang.org |
| Web3 Python | https://web3py.readthedocs.io |
| Infura help | https://docs.infura.io |
| Etherscan explorer | https://etherscan.io |
| Debugging transactions | https://sepolia.etherscan.io |

---

**Status**: ✅ Ready to deploy!

Once you complete all steps, your audit logs will be:
- ✅ Stored in Django database
- ✅ Duplicated on Ethereum blockchain
- ✅ Immutable and cryptographically verified
- ✅ Fully decentralized and auditable

Happy deploying! 🚀
