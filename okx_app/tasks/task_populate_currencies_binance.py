from okx_app.enum.enum_exchange import EnumExchange

from okx_app.model.model_currency import ModelCurrency

from okx_app.store.store_exchange_retriever import StoreExchangeRetriever

    #######################################################################################
    # Task utilised by Script to be ran after Migrations to Populate Db Currencies tables #
    #######################################################################################

class TaskPopulateCurrenciesBinance():

    def __init__(self) -> None:
        self.exchange = StoreExchangeRetriever().get_exchange(value=EnumExchange.BINANCE.value)

    def populate(self):
        ModelCurrency.objects.create(value="USDT", description="USDT", exchange=self.exchange)
