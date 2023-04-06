import requests
import json

from typing import Dict, Optional

from okx_app.decorators.decorator_rest_headers_required import decorator_rest_headers_required

from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_quote import ModelQuote

    ##########################################
    # Service Retrieves Spot Quote From Okx #
    ##########################################


class ServiceQuoteOkxRetriever:
    
    def __init__(self) -> None:
        self.url_mult_tickers = "https://www.okx.com/priapi/v5/market/mult-tickers"
    
    @decorator_rest_headers_required
    def get_price(self, base_currency: ModelCurrency,
                        quote_currency: ModelCurrency,
                        headers: Dict = None) -> Optional[ModelQuote]:
        response = requests.get(
            url=f"{self.url_mult_tickers}?instIds={base_currency.value}-{quote_currency.value}",
            headers={
                   "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36" 
                }
            )
        content = json.loads(response.content)

        if 'data' not in content:
            return None

        data = content["data"][0]
        return ModelQuote(
            last=float(data["last"]),
            bid=float(data["bidPx"]),
            ask=float(data["askPx"]),
            ts=int(data["ts"])
        )