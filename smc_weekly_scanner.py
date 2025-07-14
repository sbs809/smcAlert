import os
import pandas as pd
from nsepy import get_history
from datetime import date, timedelta
import pandas_ta as ta
import requests
from concurrent.futures import ThreadPoolExecutor

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=data)
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")


def calculate_smc_signals(ticker):
    try:
        end = date.today()
        start = end - timedelta(days=180)
        daily = get_history(symbol=ticker, start=start, end=end)
        
        if daily.empty or len(daily) < 20:
            return None

        weekly = daily.resample('W-FRI').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        if weekly.empty or len(weekly) < 5:
            return None

        weekly["engulfing"] = (
            (weekly["Close"] > weekly["Open"]) &
            (weekly["Close"].shift(1) < weekly["Open"].shift(1)) &
            (weekly["Close"] > weekly["Open"].shift(1)) &
            (weekly["Open"] < weekly["Close"].shift(1))
        )

        weekly["volSpike"] = weekly["Volume"] > weekly["Volume"].rolling(20).mean() * 1.5
        adx = ta.adx(weekly["High"], weekly["Low"], weekly["Close"], length=14)
        weekly["adx"] = adx["ADX_14"]
        weekly["trendFilter"] = weekly["adx"] > 20

        weekly["ATR"] = ta.atr(weekly["High"], weekly["Low"], weekly["Close"], length=14)
        weekly["SL"] = weekly["Low"] - weekly["ATR"]
        weekly["TP"] = weekly["Close"] + weekly["ATR"] * 4

        weekly["swingHigh"] = (weekly["High"] > weekly["High"].shift(1)) & (weekly["High"] > weekly["High"].shift(2))
        weekly["bosBull"] = weekly["swingHigh"] & (weekly["Close"] > weekly["High"].shift(1))
        weekly["fvgBull"] = (weekly["Low"].shift(2) > weekly["High"]) & (weekly["Low"].shift(1) > weekly["High"])
        weekly["bullOB"] = (weekly["Close"].shift(1) < weekly["Open"].shift(1)) & (weekly["Close"] > weekly["Open"])
        weekly["liqGrabBull"] = (weekly["Low"] < weekly["Low"].shift(1)) & (weekly["Close"] > weekly["Open"])
        weekly["breakerBlock"] = (weekly["Close"].shift(2) < weekly["Open"].shift(2)) & (weekly["Close"].shift(1) > weekly["High"].shift(2))
        weekly["inducementZone"] = (weekly["Low"].shift(1) < weekly["Low"].shift(2)) & (weekly["Low"] > weekly["Low"].shift(1))

        daily_trend = daily["Close"] > daily["Close"].rolling(20).mean()
        daily_trend_bull = daily_trend.iloc[-1]

        last = weekly.iloc[-1]
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
    except Exception as e:
        print(f"⚠️ Error processing {ticker}: {e}")
        return None


def run_weekly_smc_scan():
    send_telegram_message("⏰ Weekly SMC scan started... checking Nifty 200 stocks.")
    df_symbols = pd.read_csv("nifty200_symbols.csv")
    tickers = df_symbols["Symbol"].tolist()

    messages = []
    def process(ticker):
        signal = calculate_smc_signals(ticker)
        if signal:
            messages.append(signal)

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process, tickers)

    if messages:
        final_message = "*Weekly SMC BUY Signals (RR 1:4)*\n\n" + "\n\n".join(messages)
        send_telegram_message(final_message)
    else:
        send_telegram_message("📭 No SMC BUY signals found this week.")


if __name__ == "__main__":
    run_weekly_smc_scan()
