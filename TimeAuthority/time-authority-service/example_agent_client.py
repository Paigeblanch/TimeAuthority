"""
Example Agent Client for Time Authority Timestamping Service
Demonstrates how AI agents will interact with the x402 service
"""

import requests
import json
from datetime import datetime

class TimestampAgent:
    """Example AI agent that uses the Time Authority service"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.wallet_address = "agent_wallet_0x123..."  # Agent's USDC wallet
        
    def timestamp_document(self, content: str = None, doc_hash: str = None, metadata: dict = None):
        """
        Request timestamp for a document using x402 protocol
        
        Args:
            content: Document content (will be hashed)
            doc_hash: Pre-computed hash of document
            metadata: Optional metadata to store with timestamp
        """
        
        # Prepare request
        payload = {}
        if content:
            payload["content"] = content
        if doc_hash:
            payload["hash"] = doc_hash
        if metadata:
            payload["metadata"] = metadata
        
        # Step 1: Make initial request (will get 402 Payment Required)
        print("🤖 Agent: Requesting timestamp...")
        response = requests.post(f"{self.api_url}/timestamp", json=payload)
        
        if response.status_code == 402:
            # Payment required - get payment details
            payment_required = response.json()
            payment_details = payment_required["payment"]
            
            print(f"💰 Payment Required: {payment_details['amount']} {payment_details['currency']}")
            print(f"   Network: {payment_details['network']}")
            print(f"   Recipient: {payment_details['recipient']}")
            
            # Step 2: Agent creates payment authorization
            # In real implementation, agent would:
            # 1. Sign transaction with its wallet
            # 2. Submit to blockchain
            # 3. Get transaction hash
            
            # Simulated payment authorization
            payment_auth = {
                "transaction_hash": "0xabcdef123456...",  # Would be real tx hash
                "amount": payment_details["amount"],
                "currency": payment_details["currency"],
                "network": payment_details["network"],
                "from": self.wallet_address,
                "to": payment_details["recipient"],
                "timestamp": datetime.now().isoformat()
            }
            
            print("✅ Agent: Payment authorized and submitted to blockchain")
            
            # Step 3: Retry request with payment proof
            headers = {
                "X-Payment": json.dumps(payment_auth)
            }
            
            response = requests.post(f"{self.api_url}/timestamp", json=payload, headers=headers)
            
            if response.status_code == 200:
                timestamp_proof = response.json()
                print("\n📜 TIMESTAMP PROOF RECEIVED:")
                print(json.dumps(timestamp_proof, indent=2))
                return timestamp_proof
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return None
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return None
    
    def verify_timestamp(self, transaction_id: str):
        """Verify a timestamp proof"""
        print(f"\n🔍 Verifying timestamp {transaction_id}...")
        response = requests.get(f"{self.api_url}/verify/{transaction_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Timestamp Verified!")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"❌ Verification failed: {response.status_code}")
            return None


def demo_scenarios():
    """Demonstrate various use cases"""
    
    agent = TimestampAgent()
    
    print("=" * 70)
    print("TIME AUTHORITY - x402 TIMESTAMPING SERVICE DEMO")
    print("=" * 70)
    
    # Scenario 1: Timestamp a document by content
    print("\n\n📝 SCENARIO 1: Timestamp document content")
    print("-" * 70)
    document = "This is an important contract signed on 2026-02-12"
    result1 = agent.timestamp_document(content=document, metadata={
        "document_type": "contract",
        "parties": ["Alice", "Bob"]
    })
    
    # Scenario 2: Timestamp using pre-computed hash
    print("\n\n🔐 SCENARIO 2: Timestamp using document hash")
    print("-" * 70)
    import hashlib
    doc_hash = hashlib.sha256(b"Another important document").hexdigest()
    result2 = agent.timestamp_document(doc_hash=doc_hash, metadata={
        "document_type": "report",
        "author": "AI Agent"
    })
    
    # Scenario 3: Verify a timestamp
    if result1:
        print("\n\n🔍 SCENARIO 3: Verify timestamp")
        print("-" * 70)
        agent.verify_timestamp(result1["transaction_id"])
    
    # Get service stats
    print("\n\n📊 SERVICE STATISTICS")
    print("-" * 70)
    response = requests.get("http://localhost:8000/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"Total Timestamps: {stats['total_timestamps']}")
        print(f"Total Revenue: {stats['total_revenue_usdc']} USDC")
        print(f"Price per Timestamp: {stats['price_per_timestamp']} USDC")


if __name__ == "__main__":
    # Check if service is running
    try:
        requests.get("http://localhost:8000")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Time Authority service is not running!")
        print("Please start the service first:")
        print("  python timestamp_service.py")
        exit(1)
    
    # Run demo
    demo_scenarios()
