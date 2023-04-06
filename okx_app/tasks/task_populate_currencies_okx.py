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


class TaskPopulateCurrenciesOkx():
    
    def __init__(self) -> None:
        self.exchange      = StoreExchangeRetriever().get_exchange(value=EnumExchange.OKX.value)
        self.url_tickers   ="https://www.okx.com/priapi/v5/market/tickers?instType=OPTION"

    @decorator_rest_headers_required
    def populate(self, headers: Dict = None) :

        currencies = []

        response = requests.get(
                url=self.url_tickers,
                headers=headers
            )
        
        if response.status_code != 200:
            raise Exception(f'status code {response.status_code}, check request to Okx for tickers')
        
        content_tickers = json.loads(response.content)
        if not "data" in content_tickers:
            return currencies
        
        content_tickers_data = content_tickers["data"]

        for ticker in content_tickers_data:
            source_id = ticker["instId"]
            elements = source_id.split('-')

            # Check if the ModelCurrency object with the same value and description is already in the currencies list
            if not any(c.value == elements[0] and c.description == elements[0] for c in currencies):
                currencies.append(ModelCurrency(value=elements[0], description=elements[0], exchange=self.exchange))

            if not any(c.value == elements[1] and c.description == elements[1] for c in currencies):
                currencies.append(ModelCurrency(value=elements[1], description=elements[1], exchange=self.exchange))

        # Append only the new ModelCurrency objects to the database
        new_currencies = [c for c in currencies if not ModelCurrency.objects.filter(value=c.value, description=c.description).exists()]
        ModelCurrency.objects.bulk_create(new_currencies, ignore_conflicts=True)




            