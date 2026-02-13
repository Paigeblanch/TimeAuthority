# Time Authority - x402 Timestamping Service

A pay-per-use timestamping witness service for AI agents using Coinbase's x402 protocol.

## 🎯 What This Service Does

Time Authority provides cryptographic timestamp witnesses for documents at **$0.01 USDC** per timestamp. AI agents can autonomously pay and receive timestamp proofs without human intervention.

**Key Features:**
- ✅ x402 protocol compliant (Coinbase standard)
- ✅ Accepts USDC payments on Base network
- ✅ Generates unique 8-digit transaction IDs
- ✅ Logs all transactions for your records
- ✅ Free verification endpoint
- ✅ Works with any x402-compatible agent wallet

## 💰 Pricing

- **0.01 USDC** per timestamp
- Payments on **Base network** (low fees, instant settlement)
- Coinbase facilitator handles verification (1,000 free/month, then $0.001/tx)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your Wallet

Edit `timestamp_service.py` and replace:

```python
RECIPIENT_ADDRESS = "YOUR_COINBASE_WALLET_ADDRESS_HERE"
```

With your actual Coinbase wallet address that accepts USDC on Base network.

### 3. Run the Service

```bash
python timestamp_service.py
```

The service will start at `http://localhost:8000`

### 4. Test with Example Agent

In another terminal:

```bash
python example_agent_client.py
```

## 📡 API Endpoints

### POST /timestamp
Create a timestamp for a document (costs 0.01 USDC)

**Request (without payment):**
```bash
curl -X POST http://localhost:8000/timestamp \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Important document to timestamp"
  }'
```

**Response (402 Payment Required):**
```json
{
  "error": "Payment Required",
  "payment": {
    "type": "x402",
    "amount": "0.01",
    "currency": "USDC",
    "network": "base",
    "recipient": "0xYourWalletAddress...",
    "invoice_id": "12345678"
  }
}
```

**Request (with payment):**
```bash
curl -X POST http://localhost:8000/timestamp \
  -H "Content-Type: application/json" \
  -H "X-Payment: {payment_authorization_json}" \
  -d '{
    "content": "Important document to timestamp"
  }'
```

**Response (200 Success):**
```json
{
  "transaction_id": "87654321",
  "timestamp": "2026-02-12T10:30:45.123456+00:00",
  "timestamp_unix": 1739358645,
  "document_hash": "sha256_hash_here...",
  "witnessed_by": "Time Authority",
  "payment_verified": true,
  "signature": "Time Authority #87654321"
}
```

### GET /verify/{transaction_id}
Verify a timestamp (free)

```bash
curl http://localhost:8000/verify/87654321
```

### GET /stats
Get service statistics (free)

```bash
curl http://localhost:8000/stats
```

## 🔧 How x402 Protocol Works

1. **Agent makes request** → Service returns 402 with payment details
2. **Agent pays** → Signs USDC transaction on Base network
3. **Agent retries with payment proof** → Service verifies and processes
4. **Service returns timestamp** → Agent receives cryptographic proof

## 📊 Transaction Logging

All timestamps are logged to `transaction_log.jsonl` in JSON Lines format:

```json
{"transaction_id": "12345678", "timestamp": "2026-02-12T10:30:45Z", "document_hash": "abc123...", "payment_amount": 0.01, "payment_verified": true}
{"transaction_id": "23456789", "timestamp": "2026-02-12T11:15:22Z", "document_hash": "def456...", "payment_amount": 0.01, "payment_verified": true}
```

## 🔐 Security Features

- **8-digit random transaction IDs** - Unique identifier for each timestamp
- **SHA-256 hashing** - Cryptographic proof of document state
- **Payment verification** - Via Coinbase x402 facilitator
- **Timestamped logging** - Immutable record of all transactions

## 💳 Setting Up Coinbase Wallet

1. **Get a Coinbase account**: https://www.coinbase.com
2. **Enable Base network**: In your wallet, add Base (L2) network
3. **Get your wallet address**: Copy your USDC address on Base
4. **Update the code**: Replace `RECIPIENT_ADDRESS` in `timestamp_service.py`

## 🛠️ Production Deployment

### Option 1: Deploy to Cloud

**Railway.app** (Recommended - easiest):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Fly.io**:
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

**Render.com**:
1. Connect your GitHub repo
2. Select "Web Service"
3. Build command: `pip install -r requirements.txt`
4. Start command: `python timestamp_service.py`

### Option 2: Deploy with Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY timestamp_service.py .
COPY x402_integration.py .

CMD ["python", "timestamp_service.py"]
```

```bash
docker build -t time-authority .
docker run -p 8000:8000 time-authority
```

### Environment Variables for Production

Set these in your deployment:

```bash
RECIPIENT_ADDRESS=your_coinbase_wallet_address
COINBASE_API_KEY=your_coinbase_api_key  # Optional, for paid tier
PORT=8000
```

## 📈 Monitoring Revenue

Check your transaction log:

```bash
# Count total timestamps
wc -l transaction_log.jsonl

# Calculate total revenue
python -c "import json; print(sum(json.loads(line)['payment_amount'] for line in open('transaction_log.jsonl')))"
```

Or use the stats endpoint:

```bash
curl http://localhost:8000/stats
```

## 🤖 Agent Integration

Agents using x402-compatible wallets (Coinbase Agentic Wallets, etc.) can automatically:

1. Detect the 402 payment requirement
2. Authorize USDC payment from their wallet
3. Retry the request with payment proof
4. Receive and store the timestamp

**Example with Coinbase AgentKit:**
```python
from coinbase import AgentKit

agent = AgentKit()
response = agent.call_service(
    url="https://your-service.com/timestamp",
    data={"content": "Document to timestamp"}
)
# Agent automatically handles payment!
```

## 🔄 Upgrading to Production Payment Verification

The current implementation simulates payment verification. To add real verification:

1. **Get Coinbase API credentials**:
   - https://www.coinbase.com/settings/api

2. **Update `x402_integration.py`**:
   - Uncomment the real API call section
   - Add your API key

3. **Enable in `timestamp_service.py`**:
```python
from x402_integration import X402PaymentVerifier

verifier = X402PaymentVerifier(coinbase_api_key="your_key")
payment_verified = verifier.verify_payment(payment_data)["verified"]
```

## 📚 Additional Resources

- **x402 Protocol Docs**: https://docs.cdp.coinbase.com/x402/welcome
- **Agentic Wallets**: https://docs.cdp.coinbase.com/agentic-wallet/welcome
- **Base Network**: https://base.org
- **USDC Stablecoin**: https://www.circle.com/usdc

## 🆘 Troubleshooting

**"Payment Required" but agent already paid?**
- Check transaction log to see if payment was recorded
- Verify payment was sent to correct address on Base network
- Check if payment was in USDC (not another token)

**Service not starting?**
- Ensure port 8000 is available: `lsof -i :8000`
- Check Python version: `python --version` (need 3.9+)
- Verify dependencies: `pip install -r requirements.txt`

**Agent can't connect?**
- Check CORS settings in `timestamp_service.py`
- Verify service is accessible from agent's network
- Check firewall rules if deployed to cloud

## 📝 License

MIT License - Free to use and modify

## 🙋 Support

For questions about:
- **x402 protocol**: Coinbase Developer Discord
- **This implementation**: Open a GitHub issue
- **Payment issues**: Check Coinbase support

---

**Built with ❤️ for the agent economy**
