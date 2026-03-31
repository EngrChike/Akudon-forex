import os
import json
import yfinance as yf # New Data Source
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
    # BTC-USD for testing. You can use 'EURUSD=X' or 'GC=F' for Gold.
    symbol = 'BTC-USD' 
    ticker = yf.Ticker(symbol)
    df = ticker.history(period='1d', interval='5m')
    
    if len(df) < 10:
        print("Waiting for more market data...")
        return

    # Logic: If current price is lower than the previous low (Bank Zone)
    current_price = round(df['Close'].iloc[-1], 2)
    last_low = round(df['Low'].iloc[-2], 2)

    print(f"Scanning {symbol}... Price: {current_price} | Last Low: {last_low}")

    if current_price < last_low:
        send_akudon_push("BUY", symbol, current_price)
    elif current_price > df['High'].iloc[-2]:
        send_akudon_push("SELL", symbol, current_price)
    else:
        print("Market is quiet. No AkuDon signal yet.")

if __name__ == "__main__":
    check_market()
