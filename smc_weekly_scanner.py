import os
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import schedule
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=data)

def calculate_smc_signals(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1wk")
        df_daily = yf.download(ticker, period="1mo", interval="1d")
        if df.empty or df_daily.empty or len(df) < 5:
            return None

        df["engulfing"] = (df["Close"] > df["Open"]) &                           (df["Close"].shift(1) < df["Open"].shift(1)) &                           (df["Close"] > df["Open"].shift(1)) &                           (df["Open"] < df["Close"].shift(1))

        df["volSpike"] = df["Volume"] > df["Volume"].rolling(20).mean() * 1.5

        adx = ta.adx(df["High"], df["Low"], df["Close"], length=14)
        df["adx"] = adx["ADX_14"]
        df["trendFilter"] = df["adx"] > 20

        df["ATR"] = ta.atr(df["High"], df["Low"], df["Close"], length=14)
        df["SL"] = df["Low"] - df["ATR"]
        df["TP"] = df["Close"] + df["ATR"] * 4

        df["swingHigh"] = (df["High"] > df["High"].shift(1)) & (df["High"] > df["High"].shift(2))
        df["bosBull"] = df["swingHigh"] & (df["Close"] > df["High"].shift(1))
        df["fvgBull"] = (df["Low"].shift(2) > df["High"]) & (df["Low"].shift(1) > df["High"])
        df["bullOB"] = (df["Close"].shift(1) < df["Open"].shift(1)) & (df["Close"] > df["Open"])
        df["liqGrabBull"] = (df["Low"] < df["Low"].shift(1)) & (df["Close"] > df["Open"])

        df["breakerBlock"] = (df["Close"].shift(2) < df["Open"].shift(2)) &                              (df["Close"].shift(1) > df["High"].shift(2))

        df["inducementZone"] = (df["Low"].shift(1) < df["Low"].shift(2)) & (df["Low"] > df["Low"].shift(1))

        daily_trend = df_daily["Close"] > df_daily["Close"].rolling(20).mean()
        daily_trend_bull = daily_trend.iloc[-1]

        last = df.iloc[-1]
        if all([
            last["engulfing"],
            last["volSpike"],
            last["trendFilter"],
            last["bosBull"],
            last["fvgBull"],
            last["bullOB"],
            last["liqGrabBull"],
            last["breakerBlock"],
            last["inducementZone"],
            daily_trend_bull
        ]):
            return f"📈 *BUY Signal*: {ticker}\nSL: ₹{last['SL']:.2f} | TP: ₹{last['TP']:.2f}"
        return None
    except Exception:
        return None

def run_weekly_smc_scan():

    send_telegram_message("⏰ Weekly SMC scan started... checking Nifty 200 stocks.")


    nifty_200 = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
        "KOTAKBANK.NS", "SBIN.NS", "LT.NS", "AXISBANK.NS", "ITC.NS", "BHARTIARTL.NS",
        "ASIANPAINT.NS", "DMART.NS", "MARUTI.NS", "SUNPHARMA.NS", "BAJFINANCE.NS"
    ]

    messages = []
    for ticker in nifty_200:
        signal = calculate_smc_signals(ticker)
        if signal:
            messages.append(signal)

    if messages:
        final_message = "*Weekly SMC BUY Signals (RR 1:4)*\n\n" + "\n\n".join(messages)
        send_telegram_message(final_message)
    else:
        send_telegram_message("📭 No SMC BUY signals found this week.")

if __name__ == "__main__":
    run_weekly_smc_scan()
