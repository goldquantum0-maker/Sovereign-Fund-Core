import os
import requests
from dotenv import load_dotenv

load_dotenv()

class RhineMacro:
    """The Architect: Sets the Global Market Regime via FRED."""
    def __init__(self):
        self.api_key = os.getenv("FRED_API_KEY")
        self.base_url = "https://api.stlouisfed.org/fred/"

    def fetch_fred_series(self, series_id):
        params = {"series_id": series_id, "api_key": self.api_key, "filetype": "json", "limit": 1}
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return float(response.json()['observations'][0]['value'])
        except Exception as e:
            return None

    def determine_regime(self):
        yield_10y = self.fetch_fred_series("DGS10")
        cpi = self.fetch_fred_series("CPIAUCSL")
        if yield_10y is None or cpi is None:
            return "🟡 REGIME: UNKNOWN"
        if yield_10y > 4.2:
            return "🔴 RISK-OFF"
        elif yield_10y < 3.5:
            return "🟢 RISK-ON"
        else:
            return "🟡 NEUTRAL"
