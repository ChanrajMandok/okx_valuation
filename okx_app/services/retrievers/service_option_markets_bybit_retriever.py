import os
import json
import requests
from typing import Dict

from okx_app.decorators.decorator_rest_headers_required import decorator_rest_headers_required
from okx_app.enum.enum_exchange import EnumExchange

from okx_app.enum.enum_option_type import EnumOptionType

from okx_app.model.model_option_market import ModelOptionMarket

from okx_app.services.quote.service_quote_bybit_retriever import ServiceQuoteBybitRetriever

from okx_app.store.store_currency_retriever import StoreCurrencyRetriever
from okx_app.store.store_exchange_retriever import StoreExchangeRetriever

    ##################################################
    # Service Retrieves ETH - USD Options From Bybit #
    ##################################################


class ServiceOptionMarketsBybitRetriever():
    
    def __init__(self) -> None:
        super(ServiceOptionMarketsBybitRetriever, self).__init__()
        self.url_tickers                 ="https://api.bytick.com/v5/market/instruments-info?category=option&baseCoin=ETH&Status=Trading"
        self.orderbooks                  = "https://api.bytick.com/v5/market/orderbook?category=option&symbol="
        self.exchange                    = StoreExchangeRetriever().get_exchange(value=EnumExchange.BYBIT.value)
        self.store_currency_retriever    = StoreCurrencyRetriever()
        self.bybit_quote_retriever       = ServiceQuoteBybitRetriever()

    @decorator_rest_headers_required
    def get_markets(self,
                    time_to_maturity_days_max = float(os.environ['TIME_TO_MATURITY_MAX_DAYS']),
                    time_to_maturity_days_min = float(os.environ['TIME_TO_MATURITY_MIN_DAYS']),
                    headers: Dict = None
                    ) -> list[ModelOptionMarket]:
       
        option_markets = []


        response_tickers = requests.get(
                url=self.url_tickers,
                headers=headers
            )
        
        reference_price = self.bybit_quote_retriever.get_price(
                                                        base_currency=self.store_currency_retriever.get_or_create('ETH'),
                                                        quote_currency=self.store_currency_retriever.get_or_create('USD')
                                                            )
        
        
        content_tickers = json.loads(response_tickers.content)

        if not "result" in content_tickers:
            return option_markets
        
        if not "list" in content_tickers['result']:
            return option_markets
        
        data = content_tickers['result']['list']
        for value in data:

            term =  (float(value["deliveryTime"]) - float(value['launchTime'])) / float(31536000000)

            if term > (time_to_maturity_days_max/365):
                continue

            if term < (time_to_maturity_days_min/365):
                continue

            elements = value['symbol'].split('-')

            base_currency = self.store_currency_retriever.get_or_create(value["baseCoin"])
            quote_currency = self.store_currency_retriever.get_or_create(value['quoteCoin'])
            option_type = EnumOptionType.PUT.value if (value["optionsType"] == 'Put') else EnumOptionType.CALL.value
            strike = float(elements[2])
            exchange=self.exchange
            source_id=value['symbol']

            spot_price = float(reference_price.last)

            ## Latency Issues caused here, no alternative as endpoints from OKX & Bybit are dfifferent

            orderbook = requests.get(
                url = str(self.orderbooks) + f"{value['symbol']}",
                headers=headers
            )
            content_orderbook = json.loads(orderbook.content)
            if not "result" in content_orderbook:
                continue
            
            orderbook_data = content_orderbook['result']
            if not all(x in orderbook_data for x in ('b', 'a')) or \
               not all(len(orderbook_data[x]) > 0 and len(orderbook_data[x][0]) > 1 for x in ('b', 'a')):
                continue

            ask_price = float(orderbook_data['a'][0][0]) 
            ask_size = float(orderbook_data['a'][0][1]) 
            bid_price = float(orderbook_data['b'][0][0]) 
            bid_size = float(orderbook_data['b'][0][1]) 
 
            option_market = ModelOptionMarket(
                    exchange=exchange,
                    source_id=source_id,
                    base_currency=base_currency,
                    quote_currency=quote_currency,
                    term=term,
                    strike=strike,
                    option_type=option_type,
                    bid_size=bid_size,
                    ask_size=ask_size,
                    bid_price=bid_price,
                    ask_price=ask_price,
                    reference=spot_price,
                )
            
            option_markets.append(option_market)

        return option_markets
           

            


            

            




            



        

