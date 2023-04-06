from okx_app.tasks.task_populate_currencies_binance import TaskPopulateCurrenciesBinance
from okx_app.tasks.task_populate_currencies_bybit import TaskPopulateCurrenciesBybit
from okx_app.tasks.task_populate_currencies_okx import TaskPopulateCurrenciesOkx
from okx_app.tasks.task_populate_exchanges import TaskPopulateExchanges

    ####################################################
    # Run Script After Migrations & Db Made in PGadmin #
    ####################################################
    

def run():
    TaskPopulateExchanges().populate()
    TaskPopulateCurrenciesOkx().populate()
    TaskPopulateCurrenciesBinance().populate()
    TaskPopulateCurrenciesBybit().populate()
