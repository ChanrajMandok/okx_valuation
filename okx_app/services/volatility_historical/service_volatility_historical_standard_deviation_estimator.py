import numpy as np

from datetime import datetime, timezone, timedelta

from okx_app.model.model_candle import ModelCandle
from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange

from okx_app.services.volatility_historical.service_volatility_historical_estimator_interface import ServiceVolatilityHistoricalEstimatorInterface

    ###############################################
    # Service Calculates Classic Vol from Candles #
    ###############################################


class ServiceVolatilityHistoricalStandardDeviationEstimator(ServiceVolatilityHistoricalEstimatorInterface):

        def __init__(self) -> None:
            super(ServiceVolatilityHistoricalStandardDeviationEstimator, self).__init__()

        def estimate(
            self,
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

            returns = []
            for i in range(1, len(candles), 1):
                returns.append(np.log(candles[i].close/candles[i-1].close))

            standard_dev = np.std(returns)
            annualised_vol = standard_dev*((525600)**0.5)

            return annualised_vol
