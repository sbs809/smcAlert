# 🧠 Weekly SMC Alert Bot (GitHub Actions Version)

This project scans Nifty 200 stocks weekly for high-probability BUY setups based on Smart Money Concepts (SMC) and sends Telegram alerts.

## 🔍 Strategy Includes:
- ✅ Bullish Engulfing Candle
- ✅ Volume Spike
- ✅ ADX Trend Filter
- ✅ ATR-based SL/TP (RR 1:4)
- ✅ Smart Money Concepts: BoS, FVG, OB, Liquidity Grab
- ✅ ➕ Breaker Blocks
- ✅ ➕ Inducement Zones
- ✅ Daily Trend Filter

## 🚀 How to Deploy on GitHub Actions (Free Forever)

1. Fork this repository to your GitHub account.
2. Go to `Settings > Secrets and variables > Actions` in your repo.
3. Add two **repository secrets**:
   - `TELEGRAM_TOKEN` → Your bot token from @BotFather
   - `TELEGRAM_CHAT_ID` → Your chat ID or group ID
4. GitHub will run the scanner **every Friday at 9:30 PM IST**.
5. You’ll receive BUY-only signals via Telegram automatically.

No server or paid hosting required ✅
