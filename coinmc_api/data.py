from re import M
import typing
import aiohttp as aiohttp
import requests
import pandas as pd
from io import StringIO
from ._utils import (_init_session, _format_date,
                     _sanitize_dates, _url, RemoteDataError, _handle_request_errors, EnvironNotSet,
                     _handle_environ_error, sentinel, api_key_not_authorized)

from config.config import Config
import json

config_data: Config = Config()

COIN_MARKET_CAP_API_KEY_ENV_VAR: str = config_data.COIN_MARKET_CAP_API_KEY_ENV_VAR
COIN_MARKET_CAP_API_KEY_DEFAULT: str = config_data.COIN_MARKET_CAP_API_KEY_DEFAULT
COIN_MARKET_CAP_API_URL: str = config_data.COIN_MARKET_CAP_API_URL


def set_envar() -> str:
    return COIN_MARKET_CAP_API_KEY_ENV_VAR

def inv_api_key():
    print(f"API Key Restricted, Try upgrading your API Key: {__name__}")
    return sentinel

@_handle_request_errors
def get_latest_listing(api_key: str = COIN_MARKET_CAP_API_KEY_DEFAULT,
                       sort_by: str = "market_cap",
                       top_n: int = 500,
                 session: typing.Union[None, requests.Session] = None,) -> typing.Union[pd.DataFrame, None]:
    """
        Returns latest listing in cryptomarkets
    """
    session: requests.Session = _init_session(session)
    endpoint: str = f"/v1/cryptocurrency/listings/latest"
    url: str = COIN_MARKET_CAP_API_URL + endpoint
    params: dict = {
        "convert": "USD",
        "limit": str(top_n),
        "sort": sort_by # volume_7d, volume_30d, percent_change_7d, market_cap
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    r: requests.Response = session.get(url, params=params, headers = headers)

    if r.status_code == requests.codes.ok:
        _tmp = json.loads(r.text)
        return pd.json_normalize(_tmp["data"], sep = "-")
    elif r.status_code == api_key_not_authorized:
        inv_api_key()
    else:
        params["api_token"] = "YOUR_HIDDEN_API"
        raise RemoteDataError(r.status_code, r.reason, _url(url, params))

# TODO: Add global metrics historical
@_handle_request_errors
def get_historical_global_metrics(api_key: str = COIN_MARKET_CAP_API_KEY_DEFAULT, 
                 session: typing.Union[None, requests.Session] = None,) -> typing.Union[pd.DataFrame, None]:
    """
        Returns global metrics (e.g. market cap, listed pairs, etc.)
    """
    session: requests.Session = _init_session(session)
    endpoint: str = f"/v1/global-metrics/quotes/historical"
    url: str = COIN_MARKET_CAP_API_URL + endpoint
    params: dict = {
        "interval": "1d",
        "convert": "USD",
        "count": "30",
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    r: requests.Response = session.get(url, params=params, headers = headers)

    if r.status_code == requests.codes.ok:
        _tmp = json.loads(r.text)
        return pd.json_normalize(_tmp["data"]["quotes"], sep = "-")
    elif r.status_code == api_key_not_authorized:
        inv_api_key()
    else:
        params["api_token"] = "YOUR_HIDDEN_API"
        raise RemoteDataError(r.status_code, r.reason, _url(url, params))

@_handle_request_errors
def get_latest_global_metrics(api_key: str = COIN_MARKET_CAP_API_KEY_DEFAULT, 
                 session: typing.Union[None, requests.Session] = None,) -> typing.Union[pd.DataFrame, None]:
    """
        Returns global metrics (e.g. market cap, listed pairs, etc.)
    """
    session: requests.Session = _init_session(session)
    endpoint: str = f"/v1/global-metrics/quotes/historical"
    url: str = COIN_MARKET_CAP_API_URL + endpoint
    params: dict = {
        "convert": "USD",
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    r: requests.Response = session.get(url, params=params, headers = headers)

    if r.status_code == requests.codes.ok:
        _tmp = json.loads(r.text)
        return pd.json_normalize(_tmp["data"]["quotes"], sep = "-")
    elif r.status_code == api_key_not_authorized:
        inv_api_key()
    else:
        params["api_token"] = "YOUR_HIDDEN_API"
        raise RemoteDataError(r.status_code, r.reason, _url(url, params))

# TODO: Add OHLCV historical data
@_handle_request_errors
def get_historical_OHLCV_metrics(api_key: str = COIN_MARKET_CAP_API_KEY_DEFAULT, 
                                 symbol_list: typing.List[str] = [],
                                 time_period: str = "hourly", # daily or hourly
                                 time_start: str = None,
                                 time_end: str = None,
                                 interval: str = "1h",
                 session: typing.Union[None, requests.Session] = None,) -> typing.Union[pd.DataFrame, None]:
    """
        Returns global metrics (e.g. market cap, listed pairs, etc.)
    """
    def _parse_ohlcv(response: dict, symbol_list: typing.List[str]):
        _res_df = [pd.DataFrame(response["data"][s]).explode("quotes") for s in symbol_list]
        return pd.concat(_res_df, axis = 0)

    session: requests.Session = _init_session(session)
    endpoint: str = f"/v2/cryptocurrency/ohlcv/historical"
    url: str = COIN_MARKET_CAP_API_URL + endpoint
    
    params: dict = {
        "convert": "USD",
        "symbol": ",".join(symbol_list),
        "time_period": time_period,
        "time_start": time_start,
        "time_end": time_end,
        "interval": interval
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    r: requests.Response = session.get(url, params=params, headers = headers)

    if r.status_code == requests.codes.ok:
        _tmp = json.loads(r.text)
        return _parse_ohlcv(_tmp, symbol_list)
    elif r.status_code == api_key_not_authorized:
        inv_api_key()
    else:
        params["api_token"] = "YOUR_HIDDEN_API"
        raise RemoteDataError(r.status_code, r.reason, _url(url, params))

@_handle_request_errors
def get_latest_OHLCV_metrics(api_key: str = COIN_MARKET_CAP_API_KEY_DEFAULT, 
                                 symbol_list: typing.List[str] = [],
                 session: typing.Union[None, requests.Session] = None,) -> typing.Union[dict, None]:
    """
        Returns global metrics (e.g. market cap, listed pairs, etc.)
    """

    session: requests.Session = _init_session(session)
    endpoint: str = f"/v2/cryptocurrency/ohlcv/latest"
    url: str = COIN_MARKET_CAP_API_URL + endpoint
    
    params: dict = {
        "convert": "USD",
        "symbol": ",".join(symbol_list),
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    r: requests.Response = session.get(url, params=params, headers = headers)

    if r.status_code == requests.codes.ok:
        _tmp = json.loads(r.text)
        return _tmp["data"]
    elif r.status_code == api_key_not_authorized:
        inv_api_key()
    else:
        params["api_token"] = "YOUR_HIDDEN_API"
        raise RemoteDataError(r.status_code, r.reason, _url(url, params))

# TODO: Add coin categories
# TODO: Add airdrops
