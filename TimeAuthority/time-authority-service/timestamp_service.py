"""
Time Authority - x402 Timestamping Service
A pay-per-use timestamp witness service for AI agents using the x402 protocol
"""

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
import hashlib
import random
import json
import os
from typing import Optional

app = FastAPI(
    title="Time Authority",
    description="x402-powered timestamping service - witness documents at $0.01 USDC per timestamp",
    version="1.0.0"
)

# Enable CORS for agent access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PRICE_USDC = 0.01  # $0.01 USD in USDC
PAYMENT_NETWORK = "base"  # Base network (Coinbase L2)
PAYMENT_TOKEN = "USDC"

# Your Coinbase wallet address on Base network
RECIPIENT_ADDRESS = "0x9A51D52CcbeB0C414d1C4A0feC6fe345A169C1a4"

# Transaction log file
TRANSACTION_LOG = "transaction_log.jsonl"

class DocumentRequest(BaseModel):
    """Document to be timestamped - can be hash or content"""
    content: Optional[str] = None
    hash: Optional[str] = None
    metadata: Optional[dict] = None

class TimestampResponse(BaseModel):
    """Timestamp proof returned to agent"""
    transaction_id: str
    timestamp: str
    timestamp_unix: int
    document_hash: str
    witnessed_by: str
    payment_verified: bool
    signature: str

def generate_transaction_id() -> str:
    """Generate random 8-digit transaction ID"""
    return str(random.randint(10000000, 99999999))

def hash_document(content: str) -> str:
    """Generate SHA-256 hash of document content"""
    return hashlib.sha256(content.encode()).hexdigest()

def log_transaction(transaction_data: dict):
    """Log transaction to file for your records"""
    with open(TRANSACTION_LOG, 'a') as f:
        json.dump(transaction_data, f)
        f.write('\n')

def create_x402_payment_response(request: Request) -> dict:
    """Create x402 payment required response"""
    return {
        "type": "x402",
        "version": "2.0",
        "amount": str(PRICE_USDC),
        "currency": PAYMENT_TOKEN,
        "network": PAYMENT_NETWORK,
        "recipient": RECIPIENT_ADDRESS,
        "description": "Time Authority timestamp witness service",
        "invoice_id": generate_transaction_id(),
        "facilitator": {
            "name": "coinbase",
            "url": "https://api.coinbase.com/v1/x402"
        }
    }

@app.get("/")
async def root():
    """Service information"""
    return {
        "service": "Time Authority",
        "description": "x402-powered timestamping witness service",
        "price": f"{PRICE_USDC} {PAYMENT_TOKEN}",
        "network": PAYMENT_NETWORK,
        "endpoint": "/timestamp",
        "protocol": "x402 v2.0"
    }

@app.post("/timestamp")
async def create_timestamp(
    document: DocumentRequest,
    request: Request,
    response: Response
):
    """
    Create timestamp for a document
    
    This endpoint follows x402 protocol:
    1. First call without payment returns 402 with payment details
    2. Second call with payment header creates timestamp
    """
    
    # Check for payment header (x402 protocol)
    payment_header = request.headers.get("X-Payment")
    
    if not payment_header:
        # No payment provided - return 402 with payment instructions
        response.status_code = 402
        payment_details = create_x402_payment_response(request)
        response.headers["X-Payment-Required"] = json.dumps(payment_details)
        return {
            "error": "Payment Required",
            "message": f"Please pay {PRICE_USDC} {PAYMENT_TOKEN} to timestamp this document",
            "payment": payment_details
        }
    
    # Payment header present - verify and process
    try:
        payment_data = json.loads(payment_header)
    except:
        raise HTTPException(status_code=400, detail="Invalid payment header")
    
    # In production, you would verify the payment with Coinbase's facilitator
    # For now, we'll assume payment is valid if header is present
    # TODO: Add actual payment verification via Coinbase API
    
    payment_verified = True  # Would be result of verification call
    
    # Generate document hash
    if document.hash:
        doc_hash = document.hash
    elif document.content:
        doc_hash = hash_document(document.content)
    else:
        raise HTTPException(status_code=400, detail="Must provide either 'content' or 'hash'")
    
    # Generate timestamp
    now = datetime.now(timezone.utc)
    timestamp_iso = now.isoformat()
    timestamp_unix = int(now.timestamp())
    
    # Generate transaction ID (8 random digits)
    transaction_id = generate_transaction_id()
    
    # Create signature (transaction ID serves as signature)
    signature = f"Time Authority #{transaction_id}"
    
    # Log transaction
    transaction_log = {
        "transaction_id": transaction_id,
        "timestamp": timestamp_iso,
        "timestamp_unix": timestamp_unix,
        "document_hash": doc_hash,
        "payment_amount": PRICE_USDC,
        "payment_token": PAYMENT_TOKEN,
        "payment_network": PAYMENT_NETWORK,
        "payment_verified": payment_verified,
        "metadata": document.metadata or {}
    }
    log_transaction(transaction_log)
    
    # Create response
    timestamp_response = TimestampResponse(
        transaction_id=transaction_id,
        timestamp=timestamp_iso,
        timestamp_unix=timestamp_unix,
        document_hash=doc_hash,
        witnessed_by="Time Authority",
        payment_verified=payment_verified,
        signature=signature
    )
    
    # Add payment confirmation header
    response.headers["X-Payment-Response"] = json.dumps({
        "status": "confirmed",
        "transaction_id": transaction_id,
        "amount": PRICE_USDC,
        "currency": PAYMENT_TOKEN
    })
    
    return timestamp_response

@app.get("/verify/{transaction_id}")
async def verify_timestamp(transaction_id: str):
    """
    Verify a timestamp by transaction ID (free endpoint)
    """
    # Read transaction log and find matching transaction
    if not os.path.exists(TRANSACTION_LOG):
        raise HTTPException(status_code=404, detail="No transactions found")
    
    with open(TRANSACTION_LOG, 'r') as f:
        for line in f:
            transaction = json.loads(line)
            if transaction["transaction_id"] == transaction_id:
                return {
                    "verified": True,
                    "transaction": transaction
                }
    
    raise HTTPException(status_code=404, detail="Transaction ID not found")

@app.get("/stats")
async def get_stats():
    """
    Get service statistics (free endpoint)
    """
    if not os.path.exists(TRANSACTION_LOG):
        return {
            "total_timestamps": 0,
            "total_revenue_usdc": 0
        }
    
    count = 0
    with open(TRANSACTION_LOG, 'r') as f:
        for line in f:
            count += 1
    
    return {
        "total_timestamps": count,
        "total_revenue_usdc": count * PRICE_USDC,
        "price_per_timestamp": PRICE_USDC,
        "payment_token": PAYMENT_TOKEN
    }

# Import dashboard
from dashboard import add_dashboard_routes
add_dashboard_routes(app)

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("⏰ TIME AUTHORITY - x402 Timestamping Service")
    print("=" * 70)
    print(f"🌐 Service running at: http://localhost:8000")
    print(f"📊 Dashboard available at: http://localhost:8000/dashboard")
    print(f"💰 Price: {PRICE_USDC} USDC per timestamp")
    print(f"🔗 Network: {PAYMENT_NETWORK.upper()}")
    print("=" * 70)
    uvicorn.run(app, host="0.0.0.0", port=8000)
