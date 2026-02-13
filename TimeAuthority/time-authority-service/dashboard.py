"""
Transaction Dashboard - View your timestamp revenue and logs
Simple web interface to monitor your Time Authority service
"""

from fastapi.responses import HTMLResponse
from fastapi import FastAPI
import json
import os
from datetime import datetime

def add_dashboard_routes(app: FastAPI):
    """Add dashboard routes to the main FastAPI app"""
    
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """
        Web dashboard to view transactions and revenue
        """
        
        # Read transaction log
        transactions = []
        total_revenue = 0
        
        if os.path.exists("transaction_log.jsonl"):
            with open("transaction_log.jsonl", 'r') as f:
                for line in f:
                    tx = json.loads(line)
                    transactions.append(tx)
                    total_revenue += tx.get("payment_amount", 0)
        
        # Sort by timestamp descending
        transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Time Authority Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .stat-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-card .subtitle {{
            color: #999;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .transactions {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .transactions h2 {{
            margin-bottom: 20px;
            color: #333;
        }}
        
        .transaction-list {{
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .transaction {{
            border-bottom: 1px solid #eee;
            padding: 20px 0;
        }}
        
        .transaction:last-child {{
            border-bottom: none;
        }}
        
        .transaction-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .transaction-id {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }}
        
        .transaction-amount {{
            background: #4caf50;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
        }}
        
        .transaction-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            color: #666;
            font-size: 0.9em;
        }}
        
        .detail-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .detail-label {{
            font-weight: bold;
            color: #999;
            font-size: 0.85em;
            margin-bottom: 3px;
        }}
        
        .detail-value {{
            color: #333;
            font-family: 'Courier New', monospace;
        }}
        
        .hash {{
            word-break: break-all;
            font-size: 0.85em;
        }}
        
        .verified-badge {{
            background: #4caf50;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }}
        
        .empty-state svg {{
            width: 100px;
            height: 100px;
            margin-bottom: 20px;
            opacity: 0.3;
        }}
        
        .refresh-btn {{
            background: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
            color: #667eea;
            margin-top: 20px;
        }}
        
        .refresh-btn:hover {{
            background: #f0f0f0;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2em;
            }}
            
            .stat-card .value {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ Time Authority</h1>
            <p>x402 Timestamping Service Dashboard</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total Timestamps</h3>
                <div class="value">{len(transactions)}</div>
                <div class="subtitle">Documents witnessed</div>
            </div>
            
            <div class="stat-card">
                <h3>Total Revenue</h3>
                <div class="value">${total_revenue:.2f}</div>
                <div class="subtitle">USDC earned</div>
            </div>
            
            <div class="stat-card">
                <h3>Price Per Stamp</h3>
                <div class="value">$0.01</div>
                <div class="subtitle">USDC on Base</div>
            </div>
        </div>
        
        <div class="transactions">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>Recent Transactions</h2>
                <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
            </div>
            
            <div class="transaction-list">
                {"".join([f'''
                <div class="transaction">
                    <div class="transaction-header">
                        <div class="transaction-id">#{tx["transaction_id"]}</div>
                        <div class="transaction-amount">+${tx.get("payment_amount", 0):.2f} USDC</div>
                    </div>
                    <div class="transaction-details">
                        <div class="detail-item">
                            <div class="detail-label">Timestamp</div>
                            <div class="detail-value">{tx.get("timestamp", "N/A")}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Document Hash</div>
                            <div class="detail-value hash">{tx.get("document_hash", "N/A")[:16]}...</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Network</div>
                            <div class="detail-value">{tx.get("payment_network", "N/A").upper()}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Verification</div>
                            <div class="detail-value">
                                {"<span class='verified-badge'>✓ VERIFIED</span>" if tx.get("payment_verified") else "Pending"}
                            </div>
                        </div>
                    </div>
                </div>
                ''' for tx in transactions]) if transactions else '''
                <div class="empty-state">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    <h3>No timestamps yet</h3>
                    <p>Waiting for agents to use your service...</p>
                </div>
                '''}
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return html

# This will be imported by the main service
if __name__ == "__main__":
    print("Dashboard module - import this in timestamp_service.py")
