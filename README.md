# 🧠 Weekly SMC BUY Signal Bot (Python)

This bot scans Nifty 200 stocks weekly using a Smart Money Concepts strategy and sends Telegram BUY alerts.

## 📦 Strategy Includes
- Bullish Engulfing Candle
- Volume Spike
- ADX Trend Filter
- ATR for SL/TP
- Smart Money Concepts (BoS, FVG, OB, Liquidity Grab)
- Daily Trend Confirmation

## 🚀 Deploy on Render (Free Forever)
1. Create an account at https://render.com
2. Fork this repo to your GitHub
3. Go to Render → New → Background Worker
4. Connect your GitHub repo
5. Set command:
   ```bash
   python smc_weekly_scanner.py
   ```
6. Add environment variables:
   - `TELEGRAM_TOKEN`
   - `TELEGRAM_CHAT_ID`
