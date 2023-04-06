import os
import json
import time
import requests
from typing import Dict

from okx_app.decorators.decorator_rest_headers_required import decorator_rest_headers_required
from datetime import datetime, timedelta, timezone

from okx_app.enum.enum_exchange import EnumExchange

from okx_app.enum.enum_option_type import EnumOptionType

from okx_app.model.model_option_market import ModelOptionMarket

from okx_app.services.retrievers.service_option_markets_retriever_interface import ServiceOptionMarketRetrieverInterface

from okx_app.store.store_currency_retriever import StoreCurrencyRetriever
from okx_app.store.store_exchange_retriever import StoreExchangeRetriever

    #################################################
    # Service Retrieves ETH - USD Options From Okx #
    #################################################


class ServiceOptionMarketsOkxRetriever(ServiceOptionMarketRetrieverInterface):
    
    def __init__(self) -> None:
        super(ServiceOptionMarketsOkxRetriever, self).__init__()
        self.url_open_interest         ="https://www.okx.com/priapi/v5/public/open-interest?instType=OPTION&uly=ETH-USD"
        self.url_tickers               ="https://www.okx.com/priapi/v5/market/tickers?instType=OPTION&uly=ETH-USD"
        self.index_url                 = "https://www.okx.com/priapi/v5/market/index-tickers?quoteCcy=USD"
        self.exchange                  = StoreExchangeRetriever().get_exchange(value =EnumExchange.OKX.value)
        self.store_currency_retriever  = StoreCurrencyRetriever()
    
    @decorator_rest_headers_required
    def get_markets(self,
                    time_to_maturity_days_max = float(os.environ['TIME_TO_MATURITY_MAX_DAYS']),
                    time_to_maturity_days_min = float(os.environ['TIME_TO_MATURITY_MIN_DAYS']),
                    headers: Dict = None
                    ) -> list[ModelOptionMarket]:
        
        prices = {}
        option_markets = []
        
        response_tickers = requests.get(
                url=self.url_tickers,
                headers=headers
            )
        
        time.sleep(2)
        
        response_open_interest = requests.get(
                url=self.url_open_interest,
                headers=headers
            )
        
        time.sleep(2)
        
        response_prices = requests.get(
                url=self.index_url,
                headers=headers
            )

        content_tickers = json.loads(response_tickers.content)
        content_open_interest = json.loads(response_open_interest.content)
        content_prices = json.loads(response_prices.content)
        
        if not "data" in content_prices:
            return option_markets
        
        for content_price in content_prices["data"]:
            if content_price["idxPx"] != '':
                prices[content_price["instId"]] = float(content_price["idxPx"])
        
        if not "data" in content_tickers:
            return option_markets
        
        if not "data" in content_open_interest:
            return option_markets
        
        content_open_interest_data = content_open_interest["data"]
        
        options_with_oi = []
        
        for ticker in content_open_interest_data:
            if not 'oi' in ticker:
                continue
            oi = float(ticker["oi"])
            if oi > 10:
                options_with_oi.append(ticker["instId"])
        
        content_tickers_data = content_tickers["data"]
        
        for ticker in content_tickers_data:
            
            source_id = ticker["instId"]
            
            if not source_id in options_with_oi:
                continue
            
            elements = source_id.split('-')
            
            base_currency = self.store_currency_retriever.get_or_create(elements[0])
            quote_currency = self.store_currency_retriever.get_or_create(elements[1])
            expiry_time = datetime.strptime(elements[2], '%y%m%d').replace(tzinfo=timezone.utc)
            expiry_time = expiry_time + timedelta(hours=7)
            
            if expiry_time.timestamp() < (datetime.utcnow() + timedelta(days=time_to_maturity_days_min)).timestamp():
                continue
            
            if expiry_time.timestamp() > (datetime.utcnow() + timedelta(days=time_to_maturity_days_max)).timestamp():
                continue
            
            bid_size = float(ticker["bidSz"])
            ask_size = float(ticker["askSz"])
            
            if bid_size <= 5 or ask_size <= 5:
                continue 
            
            strike = float(elements[3])
            option_type = EnumOptionType.CALL.value if elements[4] == 'C' else EnumOptionType.PUT.value 
            
            reference = None
            pair = base_currency.value+"-"+quote_currency.value
            if pair in prices:
                reference = prices[pair]
                
            bid_price = float(ticker["bidPx"])*reference
            ask_price = float(ticker["askPx"])*reference
            
            option_market = ModelOptionMarket(
                    exchange=self.exchange,
                    source_id=source_id,
                    base_currency=base_currency,
                    quote_currency=quote_currency,
                    term=(expiry_time.timestamp()-datetime.utcnow().timestamp())/60/60/24/365,
                    strike=strike,
                    option_type=option_type,
                    bid_size=bid_size,
                    ask_size=ask_size,
                    bid_price=bid_price,
                    ask_price=ask_price,
                    reference=reference,
                )
            
            option_markets.append(option_market)
            
        return option_markets