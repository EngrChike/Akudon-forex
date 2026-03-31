import os
import json
import yfinance as yf
import firebase_admin
from firebase_admin import credentials, messaging

# Setup Firebase
try:
    service_account_info = json.loads(os.environ.get('SERVICE_ACCOUNT_JSON'))
    cred = credentials.Certificate(service_account_info)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase Init Error: {e}")

def send_akudon_push(signal, pair, price):
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"🚀 AKUDON {signal} ALERT",
            body=f"Bank Move on {pair} at {price}"
        ),
        topic="all_users" 
    )
    messaging.send(message)
    print(f"Successfully sent {signal} signal for {pair}")

def check_market():
    # We are now scanning both Gold and EUR/USD
    assets = {
        'GC=F': 'GOLD',
        'EURUSD=X': 'EUR/USD'
    }

    for symbol, name in assets.items():
        ticker = yf.Ticker(symbol)
        # We use a 1-day period with 5-minute intervals
        df = ticker.history(period='1d', interval='5m')
        
        if len(df) < 5:
            print(f"Waiting for more data for {name}...")
            continue

        current_price = round(df['Close'].iloc[-1], 4)
        last_low = round(df['Low'].iloc[-2], 4)
        last_high = round(df['High'].iloc[-2], 4)

        print(f"Scanning {name}... Price: {current_price}")

        # Bank Buy Logic: Price dips below previous low
        if current_price > 0:
            send_akudon_push("BUY", name, current_price)
        
        # Bank Sell Logic: Price breaks above previous high
        elif current_price > last_high:
            send_akudon_push("SELL", name, current_price)

if __name__ == "__main__":
    check_market()
