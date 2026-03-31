import os
import json
import ccxt
import firebase_admin
from firebase_admin import credentials, messaging

# 1. Setup Firebase using the Secret from GitHub
service_account_info = json.loads(os.environ.get('SERVICE_ACCOUNT_JSON'))
cred = credentials.Certificate(service_account_info)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

def send_akudon_push(signal, pair, price):
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"🚀 AKUDON {signal} ALERT",
            body=f"Bank Move Detected on {pair} at {price}"
        ),
        topic="all_users" 
    )
    response = messaging.send(message)
    print(f"Successfully sent {signal} signal:", response)

def check_market():
    exchange = ccxt.binance() # Professional data source
    symbol = 'BTC/USDT' 
    bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=10)
    
    # Simple Bank Pivot Logic (Sensitivity = 3)
    last_low = bars[-4][3]
    current_low = bars[-1][3]
    current_price = bars[-1][4]

    if current_low < last_low:
        send_push_to_app("BUY", symbol, current_price)
    else:
        # For testing purposes, we send a 'Scan Complete' log
        print("Market scanned. No Bank Entry found yet.")

if __name__ == "__main__":
    check_market()
