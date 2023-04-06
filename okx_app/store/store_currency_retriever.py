from singleton_decorator import singleton
from okx_app.model.model_currency import ModelCurrency

    ##############################################################################
    # Store utilised when deployed as API to reduce Latency & volume of DB calls #
    ##############################################################################


@singleton
class StoreCurrencyRetriever:

    def __init__(self):
        self.__currency_dict = {}

    def get(self, value: str) -> ModelCurrency:
        value_upper = value.upper()
        if not value_upper in self.__currency_dict.keys():
            self.__currency_dict[value_upper] = ModelCurrency.objects.filter(value=value_upper).first()
        return self.__currency_dict[value_upper]

    def get_or_create(self, value: str) -> ModelCurrency:
        value_upper = value.upper()
        if not value_upper in self.__currency_dict.keys():
            self.__currency_dict[value_upper], _ = ModelCurrency.objects.get_or_create(value=value_upper)
        return self.__currency_dict[value_upper]

    def set(self, currency: ModelCurrency):
        self.__currency_dict[currency.value] = currency

    def clear(self):
        self.__currency_dict = {}