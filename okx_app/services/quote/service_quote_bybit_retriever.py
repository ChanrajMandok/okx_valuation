import json
import requests

from datetime import datetime
from typing import Dict, Optional

from okx_app.decorators.decorator_rest_headers_required import decorator_rest_headers_required

from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_quote import ModelQuote

from okx_app.store.store_currency_retriever import StoreCurrencyRetriever

    ############################################
    # Service Retrieves Spot Quote From Bybit #
    ############################################


class ServiceQuoteBybitRetriever:
    
    def __init__(self) -> None:
        self.url_tickers               = "https://api.bytick.com//v5/market/tickers?category=spot"
        self.store_currency_retriever  = StoreCurrencyRetriever()
    
    @decorator_rest_headers_required
    def get_price(self, base_currency: ModelCurrency,
                        quote_currency: ModelCurrency,
                        headers: Dict = None) -> Optional[ModelQuote]:

        response = requests.get(
            url=f"{self.url_tickers}&symbol={base_currency.value}USDT",
            headers=headers
            )
        content = json.loads(response.content)

        if 'result' not in content:
            return None

        data = content['result']["list"]
        return ModelQuote(
            last=float(data[0]["lastPrice"]),
            bid=float(data[0]["bid1Price"]),
            ask=float(data[0]["ask1Price"]),
            ts=datetime.now().timestamp()
        )