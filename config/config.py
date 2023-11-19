from decouple import config
import os
class Config:
    COIN_MARKET_CAP_API_KEY_ENV_VAR: str = os.getenv('EOD_HISTORICAL_API_KEY') or config('EOD_HISTORICAL_API_KEY')
    COIN_MARKET_CAP_API_KEY_DEFAULT: str = os.getenv('EOD_HISTORICAL_API_KEY') or config('EOD_HISTORICAL_API_KEY')
    COIN_MARKET_CAP_API_URL: str = "https://pro-api.coinmarketcap.com"
    DEBUG: bool = False
