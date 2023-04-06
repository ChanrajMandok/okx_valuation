from singleton_decorator import singleton

from okx_app.model.model_exchange import ModelExchange

    ##############################################################################
    # Store utilised when deployed as API to reduce Latency & volume of DB calls #
    ##############################################################################


@singleton
class StoreExchangeRetriever:
    
    def __init__(self) -> None:
        self.exchanges = dict([(e.value, e) for e in list(ModelExchange.objects.all())])

    def get_exchange(self, value: str) -> ModelExchange:
        return self.exchanges[value]