import numpy as np

from arch import arch_model
from django.utils import timezone
from datetime import datetime, timezone, timedelta

from okx_app.model.model_candle import ModelCandle
from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange

from okx_app.services.volatility_historical.service_volatility_historical_estimator_interface import ServiceVolatilityHistoricalEstimatorInterface

    #########################################
    # Service Models GARCH VOl from Candles #
    #########################################


class ServiceVolatilityHistoricalGarchForecastEstimator(ServiceVolatilityHistoricalEstimatorInterface):

    def __init__(self) -> None:
        super(ServiceVolatilityHistoricalGarchForecastEstimator, self).__init__()
  
    def estimate(self, 
                 exchange: ModelExchange,
                 base_ccy: ModelCurrency, 
                 quote_ccy: ModelCurrency, 
                 window: int,
                 to_date: datetime = None,
                 **kwargs
                 ):

        to_date = to_date if to_date else datetime.now(timezone.utc)
        to_date_minute = to_date.replace(second=0, microsecond=0, minute=to_date.minute)
        from_date_minute = to_date_minute - timedelta(minutes=window)
        candles = list(ModelCandle.objects.filter(
            exchange=exchange,
            base_ccy=base_ccy,
            quote_ccy=quote_ccy,
            date__gte=from_date_minute
        ).order_by('-date'))

        # returns rescaled by *10 (*100 for %)
        returns = []
        for i in range(1, len(candles), 1):
            returns.append(np.log(candles[i].close/candles[i-1].close) *10000)

        ##GARCH Model employed to fit asymmetric reactions of vol 
        # Garch (1,1) Utilised https://core.ac.uk/download/pdf/235049858.pdf
        gm = arch_model(returns, p=1, q=1, dist='skewt', vol='GARCH', mean='AR', lags=1)

        results = []
        for i in range(50):
            training_window_start = i
            training_window_end = training_window_start + 100

            gm_result = gm.fit(first_obs=training_window_start, last_obs=training_window_end, update_freq=5, disp='off', options = {'maxiter': 1000})
            forecast = gm_result.forecast(horizon=1, reindex=False).variance.iloc[-1]
            results.append(forecast)

        mean = np.mean(results)

        return mean/100
