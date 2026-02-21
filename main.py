import requests
import pandas as pd
import time
import os

# ================= CONFIG =================
SYMBOL = "BTC-USD"
INTERVAL_MINUTES = 5
BB_LENGTH = 20

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ================= TELEGRAM =================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

# ================= DATA (COINBASE) =================
def get_data():
    granularity = INTERVAL_MINUTES * 60
    url = f"https://api.exchange.coinbase.com/products/{SYMBOL}/candles"
    params = {"granularity": granularity}

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if not isinstance(data, list) or len(data) < BB_LENGTH:
        raise Exception("Not enough data")

    df = pd.DataFrame(data, columns=[
        "time","low","high","open","close","volume"
    ])
    df["close"] = df["close"].astype(float)
    df = df.sort_values("time")

    return df

# ================= STRATEGY =================
def check_signal(df):
    df["basis"] = df["close"].rolling(BB_LENGTH).mean()

    prev_close = df["close"].iloc[-2]
    last_close = df["close"].iloc[-1]
    prev_basis = df["basis"].iloc[-2]
    last_basis = df["basis"].iloc[-1]

    buy = prev_close < prev_basis and last_close > last_basis
    sell = prev_close > prev_basis and last_close < last_basis

    return buy, sell, round(last_close, 2)

# ================= MAIN LOOP =================
print("🚀 BTC BB Telegram bot deployed & running")

last_signal = None

while True:
    try:
        df = get_data()
        buy, sell, price = check_signal(df)

        if buy and last_signal != "BUY":
            send_telegram(f"📈 BUY BTC\nTF: {INTERVAL_MINUTES}m\nPrice: {price}")
            last_signal = "BUY"

        elif sell and last_signal != "SELL":
            send_telegram(f"📉 SELL BTC\nTF: {INTERVAL_MINUTES}m\nPrice: {price}")
            last_signal = "SELL"

        time.sleep(INTERVAL_MINUTES * 60)

    except Exception as e:
        print("Error:", e)
        time.sleep(30)
