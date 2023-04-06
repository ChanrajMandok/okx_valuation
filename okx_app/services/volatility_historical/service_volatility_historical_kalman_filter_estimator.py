import numpy as np

from datetime import datetime, timezone, timedelta

from okx_app.model.model_candle import ModelCandle
from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange

from okx_app.services.volatility_historical.service_volatility_historical_estimator_interface import ServiceVolatilityHistoricalEstimatorInterface

    #####################################################
    # Service Implements Kalman Filter to Calculate Vol #
    #####################################################


class ServiceVolatilityHistoricalKalmanFilterEstimator(ServiceVolatilityHistoricalEstimatorInterface):

    def __init__(self) -> None:
        super(ServiceVolatilityHistoricalKalmanFilterEstimator, self).__init__()
    
    def estimate(self, 
                 exchange: ModelExchange,
                 base_ccy: ModelCurrency, 
                 quote_ccy: ModelCurrency, 
                 window: int,
                 to_date: datetime = None,
                 **kwargs):
        
        to_date = to_date if to_date else datetime.now(timezone.utc)
        to_date_minute = to_date.replace(second=0, microsecond=0, minute=to_date.minute)
        from_date_minute = to_date_minute - timedelta(minutes=window+1)
        candles = list(ModelCandle.objects.filter(
            exchange=exchange,
            base_ccy=base_ccy,
            quote_ccy=quote_ccy,
            date__gte=from_date_minute
        ).order_by('-date'))
        
            
        ##list of tuples, including loglog returns and time decay factor for application of Kalman Filter
        filtered_list_of_retruns = []
        for i in range(1, len(candles), 1):
            filtered_list_of_retruns.append(tuple(((np.log(candles[i].close/candles[i-1].close)),0.999 ** i)))
        
        filtered_returns = []
        for x,y in filtered_list_of_retruns:
            filtered_returns.append(x*y)

        standard_dev = np.std(filtered_returns)
        annualised_vol = standard_dev*((525600)**0.5)
        return annualised_vol