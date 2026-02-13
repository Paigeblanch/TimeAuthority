# Setup Guide - Time Authority x402 Service

Complete guide to get your timestamping service up and running.

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.9+** installed
   ```bash
   python3 --version
   ```

2. **Coinbase Account** with:
   - A wallet that supports USDC on Base network
   - Your wallet address ready

3. **Basic command line knowledge**

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Download the Code

If you received this as files:
```bash
cd time-authority
```

If cloning from git:
```bash
git clone https://github.com/yourusername/time-authority.git
cd time-authority
```

### Step 2: Configure Your Wallet

Edit `timestamp_service.py` and find this line:

```python
RECIPIENT_ADDRESS = "YOUR_COINBASE_WALLET_ADDRESS_HERE"
```

Replace it with your actual Coinbase wallet address that accepts USDC on Base:

```python
RECIPIENT_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
```

**Where to find your wallet address:**
1. Open Coinbase app or website
2. Go to "Wallets" → "USDC"
3. Select "Base" network
4. Click "Receive"
5. Copy your address (starts with "0x")

### Step 3: Run the Quick Start Script

```bash
./start.sh
```

Or manually:
```bash
pip install -r requirements.txt
python timestamp_service.py
```

### Step 4: Access Your Service

Open your browser to:
- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/docs
- **Service Info**: http://localhost:8000

---

## 🧪 Testing Your Service

### Test with Example Agent

In a new terminal:

```bash
python example_agent_client.py
```

This will simulate an AI agent:
1. Requesting a timestamp
2. Receiving payment instructions
3. Paying in USDC
4. Getting timestamp proof

### Test with cURL

**Get service info:**
```bash
curl http://localhost:8000/
```

**Request timestamp (will get 402):**
```bash
curl -X POST http://localhost:8000/timestamp \
  -H "Content-Type: application/json" \
  -d '{"content": "Test document"}'
```

**Check stats:**
```bash
curl http://localhost:8000/stats
```

---

## 🔧 Configuration Options

### Environment Variables

Create a `.env` file:

```bash
RECIPIENT_ADDRESS=0xYourWalletAddress
COINBASE_API_KEY=your_api_key_here  # Optional
PORT=8000
```

Then load it:

```bash
# Linux/Mac
export $(cat .env | xargs)

# Or use python-dotenv
pip install python-dotenv
```

### Pricing Configuration

Edit `timestamp_service.py`:

```python
PRICE_USDC = 0.01  # Change to your desired price
PAYMENT_NETWORK = "base"  # Network to accept payments on
PAYMENT_TOKEN = "USDC"  # Token to accept
```

---

## 📊 Viewing Your Revenue

### Dashboard (Visual)

Visit: http://localhost:8000/dashboard

You'll see:
- Total timestamps created
- Total revenue in USDC
- Recent transaction list
- Transaction details

### Command Line

**Count transactions:**
```bash
wc -l transaction_log.jsonl
```

**Calculate revenue:**
```bash
python -c "import json; print(sum(json.loads(line)['payment_amount'] for line in open('transaction_log.jsonl')))"
```

**View latest transactions:**
```bash
tail -n 5 transaction_log.jsonl | python -m json.tool
```

---

## 🔐 Enabling Real Payment Verification

Currently, the service simulates payment verification. To enable real verification:

### Step 1: Get Coinbase API Credentials

1. Go to https://www.coinbase.com/settings/api
2. Create new API key with permissions:
   - `wallet:transactions:read`
   - `wallet:payment-methods:read`
3. Save your API key and secret

### Step 2: Configure API Key

In `timestamp_service.py`, add:

```python
from x402_integration import X402PaymentVerifier

# Initialize verifier with your API key
payment_verifier = X402PaymentVerifier(
    coinbase_api_key="your_api_key_here"
)
```

### Step 3: Update Payment Verification

In the `/timestamp` endpoint, replace:

```python
payment_verified = True  # Simulated
```

With:

```python
verification = payment_verifier.verify_payment(payment_data)
payment_verified = verification["verified"]
```

---

## 🌐 Making Your Service Public

### Option 1: Use ngrok (Quick Testing)

```bash
# Install ngrok
brew install ngrok  # Mac
# or download from ngrok.com

# Run ngrok
ngrok http 8000
```

Your service will be available at: `https://xxxxx.ngrok.io`

### Option 2: Deploy to Cloud

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides for:
- Railway.app (easiest)
- Render.com
- Fly.io
- Google Cloud Run
- Docker deployment

---

## 🤖 How Agents Will Use Your Service

### Discovery

Agents can find your service through:
1. **x402 Bazaar**: https://bazaar.x402.org (submit your service)
2. **Direct URL**: Share your service URL with agent developers
3. **Agent marketplaces**: List on AI agent platforms

### Example Agent Integration

Agents using x402-compatible wallets will:

```python
import requests

# Agent makes request
response = requests.post(
    "https://your-service.com/timestamp",
    json={"content": "Document to timestamp"}
)

if response.status_code == 402:
    # Agent sees payment required
    payment_details = response.json()["payment"]
    
    # Agent's wallet automatically:
    # 1. Signs USDC transaction
    # 2. Submits to blockchain
    # 3. Retries request with proof
    
    # Agent receives timestamp proof
    timestamp_proof = response.json()
```

---

## 📈 Scaling Your Service

### Performance Tips

**For 1,000+ timestamps/day:**
- Use a database instead of JSONL file
- Add Redis for caching
- Deploy to multiple regions

**For 10,000+ timestamps/day:**
- Use PostgreSQL or MongoDB
- Add load balancer
- Enable horizontal scaling
- Consider batch processing

### Database Migration

Switch from JSONL to PostgreSQL:

```python
# Install
pip install psycopg2-binary

# Create table
CREATE TABLE timestamps (
    transaction_id VARCHAR(8) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    document_hash VARCHAR(64) NOT NULL,
    payment_amount DECIMAL NOT NULL,
    payment_verified BOOLEAN DEFAULT TRUE
);

# Update log_transaction function
def log_transaction(transaction_data: dict):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO timestamps VALUES (%s, %s, %s, %s, %s)",
        (
            transaction_data["transaction_id"],
            transaction_data["timestamp"],
            transaction_data["document_hash"],
            transaction_data["payment_amount"],
            transaction_data["payment_verified"]
        )
    )
    conn.commit()
```

---

## 🚨 Troubleshooting

### Service won't start

**Port already in use:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
python timestamp_service.py --port 8001
```

**Dependencies won't install:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install individually
pip install fastapi
pip install uvicorn
pip install pydantic
```

### Agents can't connect

**Check CORS settings:**

In `timestamp_service.py`, verify:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific agent domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Check firewall:**
```bash
# Linux
sudo ufw allow 8000

# Mac
# System Preferences → Security & Privacy → Firewall
```

### Payment verification fails

**Check network:**
- Ensure payments are on Base network
- Verify it's USDC token
- Check wallet address is correct

**Check Coinbase API:**
- Verify API key is valid
- Check API key permissions
- Review rate limits

---

## 📞 Getting Help

### Documentation
- x402 Protocol: https://docs.cdp.coinbase.com/x402/welcome
- FastAPI: https://fastapi.tiangolo.com
- USDC: https://www.circle.com/usdc

### Community
- Coinbase Developers: https://discord.gg/coinbase
- x402 GitHub: https://github.com/coinbase/x402

### Issues
- Check the FAQ in README.md
- Open GitHub issue
- Ask in Coinbase Discord

---

## ✅ Production Checklist

Before going live:

- [ ] Wallet address configured correctly
- [ ] Tested with example agent
- [ ] Payment verification working
- [ ] Dashboard accessible
- [ ] Transaction logs backing up
- [ ] Service deployed to cloud
- [ ] HTTPS enabled
- [ ] Custom domain set up (optional)
- [ ] Monitoring/alerts configured
- [ ] Listed on x402 Bazaar
- [ ] Documented API for users

---

## 🎉 You're All Set!

Your Time Authority timestamping service is ready to serve AI agents worldwide!

**Next Steps:**
1. Deploy to production (see DEPLOYMENT.md)
2. List on x402 Bazaar
3. Share with agent developers
4. Monitor your dashboard
5. Watch the revenue grow! 💰

Good luck! 🚀
