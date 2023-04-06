import numpy as np

from django.utils import timezone
from datetime import datetime, timezone, timedelta

from okx_app.model.model_candle import ModelCandle
from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange

from okx_app.services.volatility_historical.service_volatility_historical_estimator_interface import ServiceVolatilityHistoricalEstimatorInterface

    ##############################################
    # Service Calculates Vol of Vol from Candles #
    ##############################################


class ServiceVolatilityHistoricalVvolEstimator(ServiceVolatilityHistoricalEstimatorInterface):

    def __init__(self) -> None:
        super(ServiceVolatilityHistoricalVvolEstimator, self).__init__()
  
    def estimate(self, 
                 instrument_term: int,
                 exchange: ModelExchange,
                 base_ccy: ModelCurrency, 
                 quote_ccy: ModelCurrency, 
                 window: int,
                 **kwargs
                 ):

        to_date =  datetime.now(timezone.utc)
        to_date_minute = to_date.replace(second=0, microsecond=0, minute=to_date.minute)
        from_date_minute = to_date_minute - timedelta(minutes=window*2)
        candles = list(ModelCandle.objects.filter(
            exchange=exchange,
            base_ccy=base_ccy,
            quote_ccy=quote_ccy,
            date__gte=from_date_minute
        ).order_by('-date'))
        
    
        ##calculate logog returns of all candles in last 7 days (candles-1)
        returns = []
        for i in range(1, len(candles), 1):
            returns.append(np.log(candles[i].close/candles[i-1].close))

        ## calculate hvol over each instrument_term period in returns eg. every non-overlapping 12h(720) period in 7 days (10080) 
        start= 0
        dynamic_end = 0
        end = int(window)

        response_list = []
        dynamic_start = max(start, dynamic_end) 
        dynamic_end = max(start+int(instrument_term)*60, start)
        while end > dynamic_end:
            try:
                period_returns = returns[dynamic_start:dynamic_end]
                standard_dev = np.std(period_returns)
                periodic_annualised_vol = standard_dev*((525600)**0.5)
                response_list.append(periodic_annualised_vol)

            except returns == None:
                print("no returns")
            if start == int(end):
                break
            dynamic_start = max(start, dynamic_start+int(instrument_term)*60)
            dynamic_end = min(end, dynamic_start+int(instrument_term)*60)

        vvol = np.std(response_list)
        return vvol