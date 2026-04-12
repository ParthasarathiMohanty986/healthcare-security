# Blockchain Audit Logs - API Reference & Workflows

## API Endpoints Overview

### Base URL
```
http://localhost:8000/api
```

### Authentication
All endpoints require JWT Bearer token:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Blockchain Endpoints

### 1. Get Network Information
```bash
GET /blockchain/network-info/
```

**Response Example:**
```json
{
  "chainId": 11155111,
  "latestBlock": 5123456,
  "gasPrice": "25.5",
  "account": "0x1234567890123456789012345678901234567890",
  "accountBalance": 0.5
}
```

---

### 2. Get All Blockchain Audit Logs
```bash
GET /blockchain/audit-logs/?start=0&limit=50
```

**Query Parameters:**
- `start` (integer): Starting index for pagination. Default: 0
- `limit` (integer): Number of logs per page. Default: 50

**Response Example:**
```json
{
  "status": "success",
  "total": 150,
  "logs": [
    {
      "logId": 0,
      "user": "0x1234567890123456789012345678901234567890",
      "action": "ACCESS_EHR",
      "resourceType": "Patient_Record",
      "resourceId": "12345",
      "accessGranted": true,
      "isEmergency": false,
      "details": "{\"reason\": \"Treatment\"}",
      "timestamp": 1712973015,
      "ipAddress": "192.168.1.1"
    }
  ]
}
```

---

### 3. Get Specific Blockchain Log
```bash
GET /blockchain/audit-logs/{log_id}/
```

**Example:**
```bash
GET /blockchain/audit-logs/5/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "logId": 5,
    "user": "0x1234567890123456789012345678901234567890",
    "action": "ACCESS_EHR",
    "resourceType": "Patient_Record",
    "resourceId": "12345",
    "accessGranted": true,
    "isEmergency": false,
    "details": "{\"reason\": \"Treatment\"}",
    "timestamp": 1712973015,
    "ipAddress": "192.168.1.1"
  }
}
```

---

### 4. Verify Log Immutability
```bash
GET /blockchain/audit-logs/{log_id}/verify/
```

**Example:**
```bash
GET /blockchain/audit-logs/5/verify/
```

**Response:**
```json
{
  "status": "success",
  "log_id": 5,
  "verified": true,
  "immutable": true
}
```

---

### 5. Get User's Blockchain Logs
```bash
GET /blockchain/user-logs/{user_address}/?start=0&limit=50
```

**Example:**
```bash
GET /blockchain/user-logs/0x1234567890123456789012345678901234567890/?start=0&limit=50
```

**Response:**
```json
{
  "status": "success",
  "user_address": "0x1234567890123456789012345678901234567890",
  "total": 45,
  "logs": [...]
}
```

---

### 6. Check Transaction Status
```bash
GET /blockchain/transactions/{tx_hash}/status/
```

**Example:**
```bash
GET /blockchain/transactions/0xabcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd1234/status/
```

**Response:**
```json
{
  "status": "success",
  "transaction": {
    "hash": "0xabcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd1234",
    "status": "CONFIRMED",
    "block_number": 5123456,
    "gas_used": 125000,
    "created_at": "2024-04-12T10:30:15Z",
    "confirmed_at": "2024-04-12T10:32:45Z",
    "error": null
  }
}
```

---

## Audit Endpoints (Integrated with Blockchain)

### 1. Get All Audit Logs
```bash
GET /audit/logs/
```

**Response Example:**
```json
{
  "status": "success",
  "count": 50,
  "logs": [
    {
      "id": 1,
      "user": "doctor_user",
      "action": "ACCESS_EHR",
      "resource_type": "Patient_Record",
      "resource_id": "12345",
      "access_granted": true,
      "is_emergency": false,
      "timestamp": "2024-04-12T10:30:15Z",
      "details": {"reason": "Treatment"},
      "ip_address": "192.168.1.1",
      "blockchain": {
        "synced": true,
        "blockchain_log_id": 0,
        "transaction_hash": "0xabcd...",
        "status": "CONFIRMED"
      }
    }
  ]
}
```

---

### 2. Get Specific Audit Log
```bash
GET /audit/logs/{log_id}/
```

**Example:**
```bash
GET /audit/logs/1/
```

---

### 3. Sync Single Log to Blockchain
```bash
POST /audit/logs/{log_id}/sync-blockchain/
Content-Type: application/json

{
  "user_address": "0x1234567890123456789012345678901234567890"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/audit/logs/1/sync-blockchain/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_address": "0x1234567890123456789012345678901234567890"}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Log synced to blockchain",
  "transaction_hash": "0xabcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd1234",
  "block_number": 5123456,
  "gas_used": 125000
}
```

---

### 4. Sync All Unsynced Logs
```bash
POST /audit/sync-all-blockchain/
Content-Type: application/json

{
  "user_address": "0x1234567890123456789012345678901234567890"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/audit/sync-all-blockchain/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_address": "0x1234567890123456789012345678901234567890"}'
```

**Response:**
```json
{
  "status": "completed",
  "total_synced": 47,
  "total_failed": 3,
  "results": [
    {
      "log_id": 1,
      "status": "success",
      "transaction_hash": "0xabcd..."
    },
    {
      "log_id": 2,
      "status": "success",
      "transaction_hash": "0xabcd..."
    },
    {
      "log_id": 3,
      "status": "failed",
      "error": "Not authorized"
    }
  ]
}
```

---

### 5. Get Blockchain Sync Status
```bash
GET /audit/blockchain-status/
```

**Response:**
```json
{
  "status": "success",
  "audit_logs": {
    "total": 150,
    "synced": 145,
    "unsynced": 5,
    "sync_percentage": 96.67
  },
  "transactions": {
    "pending": 2,
    "confirmed": 143,
    "failed": 0
  }
}
```

---

## Command Line Usage

### Sync Single Log
```bash
python manage.py sync_audit_logs --log-id 1 --user-address 0x1234567890123456789012345678901234567890
```

### Sync All Unsynced Logs
```bash
python manage.py sync_audit_logs --all --user-address 0x1234567890123456789012345678901234567890
```

### Example Output
```
✓ Connected to blockchain via Infura
Starting sync for 25 logs...
  ✓ Log 1: 0xabcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd1234
  ✓ Log 2: 0x1234abcd567890abcd1234567890abcd1234567890abcd1234567890abcd1234
  ✓ Log 3: 0xabcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd1234
  ...
✓ Sync completed!
  Synced: 25/25
  Failed: 0/25
```

---

## Complete Workflow Example

### Scenario: Audit access and sync to blockchain

```bash
# Step 1: User accesses patient EHR (automatically creates AuditLog in database)
# This happens in your audit system automatically

# Step 2: Check if synced
curl http://localhost:8000/api/audit/logs/1/ \
  -H "Authorization: Bearer TOKEN"

# Step 3: Sync log to blockchain (if not already synced)
curl -X POST http://localhost:8000/api/audit/logs/1/sync-blockchain/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_address": "0xYourAddress"}'

# Output: Get transaction hash

# Step 4: Check blockchain status
curl http://localhost:8000/api/audit/blockchain-status/ \
  -H "Authorization: Bearer TOKEN"

# Step 5: Verify on Etherscan (optional)
# https://sepolia.etherscan.io/tx/0x<transaction_hash>

# Step 6: Later, retrieve from blockchain
curl http://localhost:8000/api/blockchain/audit-logs/0/ \
  -H "Authorization: Bearer TOKEN"

# Step 7: Verify immutability
curl http://localhost:8000/api/blockchain/audit-logs/0/verify/ \
  -H "Authorization: Bearer TOKEN"
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Healthcare System                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User Action (EHR Access) ─────────────> AuditLog Model    │
│       ↓                                      ↓                 │
│   (Log 1)                              Django Database      │
│                                         (Persistent)         │
│                                                               │
│  Audit Views (GET /audit/logs/)                             │
│       ↓                                                       │
│  Check Sync Status                                           │
│       ↓                                                       │
│  Is synced? ──NO──> Call SyncAuditLogToBlockchain           │
│       │                       ↓                               │
│       │              Call blockchain_service.py             │
│       │                       ↓                               │
│       │              Web3 Instance (Infura)                 │
│       │              (via HTTPProvider)                     │
│       │                       ↓                               │
│       │        ┌─────────────────────────────┐              │
│       │        │   Ethereum Network (Sepolia)│              │
│       │        │   (or Mainnet)              │              │
│       │        │                             │              │
│       │        │   Smart Contract (AuditLog)│              │
│       │        │   - createAuditLog()        │              │
│       │        │   - getAuditLog()           │              │
│       │        │   - getUserLogs()           │              │
│       │        └─────────────────────────────┘              │
│       │                       ↓                               │
│       │              Transaction Confirmed                  │
│       │                       ↓                               │
│       │    Update BlockchainAuditLog Model                  │
│       │    Update BlockchainTransaction Model              │
│       │                       ↓                               │
│       │ ──────────────────────┘                             │
│       ↓                                                       │
│  YES (Already synced)                                        │
│       ↓                                                       │
│  Return Response with:                                       │
│  - Local audit log data                                      │
│  - Blockchain sync status                                    │
│  - Transaction hash                                          │
│  - Immutability verification                                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Error Handling

### Common Error Responses

#### 401 - Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Fix:** Add JWT token to Authorization header

#### 404 - Not Found
```json
{
  "error": "Log not found"
}
```
**Fix:** Verify log ID exists

#### 500 - Blockchain Connection Error
```json
{
  "error": "Could not connect to Infura"
}
```
**Fix:** 
- Check INFURA_URL in .env
- Verify Infura project is active
- Check internet connection

#### 500 - Transaction Failed
```json
{
  "error": "Not authorized to write logs"
}
```
**Fix:** 
- Call authorizeWriter() in smart contract via Remix IDE
- Use your account address

---

## Testing with cURL

### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "yourusername",
    "password": "yourpassword"
  }'

# Response:
# {"access": "eyJ0eXAiOiJKV1QiLCJhbGc... "}
```

### Use Token in Requests
```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Then use in any request:
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/blockchain/network-info/
```

---

## Performance Tips

1. **Pagination**: Always use `limit` parameter to avoid slow queries
2. **Batch Syncing**: Use `/sync-all-blockchain/` instead of syncing one by one
3. **Gas Optimization**: Sync during low gas price times (check via network-info)
4. **Caching**: Cache verification results if audit frequency is high
5. **Archiving**: Archive old logs to Layer 2 solutions (Polygon) after verification

---

## Monitoring & Debugging

### Check Sync Progress
```bash
curl http://localhost:8000/api/audit/blockchain-status/ \
  -H "Authorization: Bearer TOKEN" | python -m json.tool
```

### View All Transactions (Admin)
```
http://localhost:8000/admin/blockchain/blockchaintransaction/
```

### Check Etherscan
```
https://sepolia.etherscan.io/tx/{transaction_hash}
```

### View Smart Contract
```
https://sepolia.etherscan.io/address/{contract_address}
```

---

## Next Steps

1. ✅ Test all endpoints in Postman/Insomnia
2. ✅ Set up transaction monitoring
3. ✅ Implement real-time alerts for failed syncs
4. ✅ Create admin dashboard for blockchain status
5. ✅ Plan migration to mainnet
6. ✅ Set up gas price monitoring

Deployment complete! 🚀
