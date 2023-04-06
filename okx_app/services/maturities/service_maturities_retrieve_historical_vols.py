import math

from typing import Dict

from okx_app.decorators.decorator_historical_estimator_interface_imports import decorator_historical_estimator_interface_imports

from okx_app.enum.enum_exchange import EnumExchange

from okx_app.services.candles.service_retrieve_and_populate_candles import ServiceRetrieveAndPopulateCandles

from okx_app.services.volatility_historical.service_volatility_historical_estimator_interface import ServiceVolatilityHistoricalEstimatorInterface

from okx_app.store.store_currency_retriever import StoreCurrencyRetriever
from okx_app.store.store_exchange_retriever import StoreExchangeRetriever


    ##########################################################################
    # Service uses Maturities Dict and gets Hvol estimators for each maturity #
    ##########################################################################


class ServiceMaturitiesRetrieveHistoricalVols:
        
    def __init__(self):
        self.store_currency_retriever = StoreCurrencyRetriever()
        self.service_retrieve_and_populate_candles = ServiceRetrieveAndPopulateCandles()

    @decorator_historical_estimator_interface_imports
    def get_vols(self,
                 maturities_dict:Dict,
                 service_volatility_historical_estimator                 = None,
                 service_volatility_historical_garch_estimator           = None,
                 service_volatility_historical_kalman_filter_estimator   = None,
                 service_volatility_historical_sub_sampled_estimator     = None,
                 service_volatility_historical_vvol_estimator            = None,
                 service_volatility_historical_yang_zhang_estimator      = None
                ):
        
        exchange = StoreExchangeRetriever().get_exchange(value=EnumExchange.BINANCE.value)
        base_currency = self.store_currency_retriever.get_or_create('ETH')
        quote_currency = self.store_currency_retriever.get_or_create('USDT')

        ### Update Candles for longest maturtiy needed
        sorted_maturities_dict = dict(sorted(maturities_dict.items(), key=lambda x: -float(x[0])))
        max_term = list(sorted_maturities_dict.keys())[0]
        self.service_retrieve_and_populate_candles.get_candles(base_ccy=base_currency, 
                                                                quote_ccy=quote_currency,
                                                                lookback_period=math.ceil(max_term*1.2*float(365)),
                                                                save_in_bulk=True)
        
        # get all historical volatilty figures from vol historical interface for comparison
        for key, value in sorted_maturities_dict.items():
            window= int(key*float(525600))
            for cls in ServiceVolatilityHistoricalEstimatorInterface.__subclasses__():
                class_name = cls.__name__.replace('ServiceVolatilityHistorical', '').replace('Estimator', '')
                value[f"{class_name}"] = cls().estimate(exchange=exchange,
                                                                base_ccy=base_currency, 
                                                                quote_ccy=quote_currency, 
                                                                window=window,
                                                                subsampling_interval=1,
                                                                do_winsorize=False,
                                                                winsorization_level=0.05,
                                                                return_holding_period=math.ceil(window/60),
                                                                instrument_term=1
                                                                )
                
        return maturities_dict
                
                 