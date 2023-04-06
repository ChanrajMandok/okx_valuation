from datetime import datetime, timezone, timedelta

from okx_app.decorators.decorator_historical_estimator_binance_candles_import import decorator_historical_estimator_binance_candles_import

from okx_app.model.model_candle import ModelCandle
from okx_app.model.model_currency import ModelCurrency

from okx_app.enum.enum_exchange import EnumExchange

from okx_app.store.store_exchange_retriever import StoreExchangeRetriever

    ######################################################
    # Service Retrieves Candles and Popultes ModelCandle #
    ######################################################


class ServiceRetrieveAndPopulateCandles:

    def __init__(self) -> None:
        self.exchange = StoreExchangeRetriever().get_exchange(value=EnumExchange.BINANCE.value)
        
    @decorator_historical_estimator_binance_candles_import
    def get_candles(self, 
                    base_ccy: ModelCurrency, 
                    quote_ccy: ModelCurrency, 
                    lookback_period : int,
                    save_in_bulk: bool=True,
                    service_candles_binance_retriever=None
                    ):
        

        ## Delete all Candles in Db to ensure no conficts
        ModelCandle.objects.all().delete()

        window = lookback_period*float(1440)

        ## Populate Db with candles
        service_candles_binance_retriever().get_candles(base_ccy=base_ccy, 
                                                      quote_ccy=quote_ccy,
                                                      lookback_period=lookback_period,
                                                      save_in_bulk=save_in_bulk)
        
        ## Check length of candles against lookback, single updater if not in range
        
        to_date = datetime.now(timezone.utc)
        to_date_minute = to_date.replace(second=0, microsecond=0, minute=to_date.minute)
        from_date_minute = to_date_minute - timedelta(minutes= window)

        candles = list(ModelCandle.objects.filter(
            exchange=self.exchange,
            base_ccy=base_ccy,
            quote_ccy=quote_ccy,
            date__gte=from_date_minute
        ).order_by('-date'))

        if abs(len(candles) - window) > 0.05 * window:
            service_candles_binance_retriever().get_candles(base_ccy=base_ccy, 
                                                        quote_ccy=quote_ccy,
                                                        lookback_period=lookback_period,
                                                        save_in_bulk=False)
        

        
        
