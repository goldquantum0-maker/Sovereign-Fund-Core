import yfinance as yf
import pandas as pd
import numpy as np

class KyotoQuant:
    """The Mathematician: Generates the surgical trade blueprint."""
    def __init__(self):
        self.min_risk_reward = 3.0 
        self.max_account_risk = 0.015 

    def calculate_volatility(self, ticker):
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        return np.max(ranges, axis=1).rolling(14).mean().iloc[-1]

    def create_blueprint(self, ticker, account_balance=4800):
        data = yf.Ticker(ticker).history(period="1d")
        current_price = data['Close'].iloc[-1]
        atr = self.calculate_volatility(ticker)
        
        stop_loss = current_price - (atr * 2)
        risk_per_share = current_price - stop_loss
        take_profit = current_price + (risk_per_share * self.min_risk_reward)
        
        max_dollar_risk = account_balance * self.max_account_risk
        shares_to_buy = int(max_dollar_risk / risk_per_share)

        return {
            "ticker": ticker,
            "entry": round(current_price, 2),
            "stop": round(stop_loss, 2),
            "tp": round(take_profit, 2),
            "size": shares_to_buy,
            "risk_usd": round(max_dollar_risk, 2)
        }
