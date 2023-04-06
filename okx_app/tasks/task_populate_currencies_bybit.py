import json
import requests

from typing import Dict

from okx_app.decorators.decorator_rest_headers_required import decorator_rest_headers_required
from okx_app.enum.enum_exchange import EnumExchange


from okx_app.model.model_currency import ModelCurrency
from okx_app.store.store_exchange_retriever import StoreExchangeRetriever

    ############################################################################
    # Task utilised by Script to be ran after Migrations to Populate Db tables #
    ############################################################################


class TaskPopulateCurrenciesBybit():

    def __init__(self) -> None:
        self.exchange      = StoreExchangeRetriever().get_exchange(value=EnumExchange.BYBIT.value)
        self.url_tickers   ="https://api.bytick.com/v5/market/instruments-info?category=option&baseCoin=ETH&Status=Trading"

    @decorator_rest_headers_required
    def populate(self, headers: Dict = None):

        currencies_bybit = []

        response_tickers = requests.get(
                url=self.url_tickers,
                headers=headers
            )
        
        content_tickers = json.loads(response_tickers.content)

        if not "list" in content_tickers['result']:
            raise Exception('Check Bybit Currencies Populate function')
    
        data = content_tickers['result']['list']

        for value in data:
            bc, qc, sc = (value[c] for c in ['baseCoin', 'quoteCoin', 'settleCoin'])
            currencies = [bc, qc, sc]
            for c in currencies:
                if c not in currencies_bybit:
                    currencies_bybit.append(c)
            if qc in [bc, sc]:
                if qc != bc:
                    bc, sc = sc, bc
                if sc not in currencies_bybit:
                    currencies_bybit.append(sc)

        bybit_ccys = [ModelCurrency(value=x, description=x, exchange=self.exchange) for x in currencies_bybit]
        ModelCurrency.objects.bulk_create(bybit_ccys, ignore_conflicts=True)


