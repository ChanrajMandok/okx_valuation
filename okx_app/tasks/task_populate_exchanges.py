from okx_app.enum.enum_exchange import EnumExchange
from okx_app.model.model_exchange import ModelExchange

    ############################################################################
    # Task utilised by Script to be ran after Migrations to Populate Db tables #
    ############################################################################


class TaskPopulateExchanges():
    
    def populate(self):
        for exchange in EnumExchange:
            ModelExchange.objects.update_or_create(value=exchange.value, defaults={'is_valid':True})
    