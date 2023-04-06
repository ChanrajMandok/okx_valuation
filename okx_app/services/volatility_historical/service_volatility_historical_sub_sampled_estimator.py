import math
import numpy as np
import django.utils.timezone

from operator import mod
from binance.client import BaseClient
from scipy.stats.mstats import winsorize
from datetime import datetime, timedelta

from okx_app.model.model_candle import ModelCandle
from okx_app.model.model_candle_hourly import ModelCandleHourly
from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange

from okx_app.services.volatility_historical.service_volatility_historical_estimator_interface import ServiceVolatilityHistoricalEstimatorInterface

    #################################################################
    # Service Calculates Vol upon subsampled dataset of Historicals #
    #################################################################


class ServiceVolatilityHistoricalSubSampledEstimator(ServiceVolatilityHistoricalEstimatorInterface):

    def __init__(self) -> None:
        super(ServiceVolatilityHistoricalSubSampledEstimator, self).__init__()
    
    def estimate(self, 
                 exchange: ModelExchange,
                 base_ccy: ModelCurrency, 
                 quote_ccy: ModelCurrency, 
                 window: int,                      # T = 3600s
                 to_date: datetime = None,
                 subsampling_interval: int = 1, # interval = 30s
                 return_holding_period: int = None,         # delta = 300s: return holding period
                 interval: str = BaseClient.KLINE_INTERVAL_1MINUTE,
                 do_winsorize: bool = False,
                 winsorization_level: float = 0.05,
                 **kwargs
                 ):
        
        # adjust the right bound of the time interval
        
        t1 = window - mod(window, subsampling_interval)
        q = math.floor(return_holding_period / subsampling_interval)
        to_date = to_date if to_date else django.utils.timezone.now()
        
        if not interval in [BaseClient.KLINE_INTERVAL_1MINUTE, BaseClient.KLINE_INTERVAL_1HOUR]:
             raise Exception(f"interval {interval} not supported")
        
        if interval == BaseClient.KLINE_INTERVAL_1MINUTE:
            to_date_unit = to_date.replace(second=0, microsecond=0, minute=to_date.minute)
            from_date_unit = to_date_unit - timedelta(minutes=t1-1)
            ModelCandleClass = ModelCandle
        elif interval == BaseClient.KLINE_INTERVAL_1HOUR:
            to_date_unit = to_date.replace(second=0, microsecond=0, minute=0, hour=to_date.hour)
            from_date_unit = to_date_unit - timedelta(hours=t1-1)
            ModelCandleClass = ModelCandleHourly
            
        candles = list(ModelCandleClass.objects.filter(
            exchange=exchange,
            base_ccy=base_ccy,
            quote_ccy=quote_ccy,
            date__gte=from_date_unit
        ).order_by('date'))

        log_candles = [np.log(c.close) for c in candles]
        trs = len(log_candles) - mod(len(log_candles), return_holding_period*subsampling_interval)  
        trs_r = math.ceil(trs)
        log_candles = log_candles[-trs_r:]
        
        rets = {}
        count = [0]*q

        rets = {}
        count = [0]*q

        t = return_holding_period
        while t < trs:
            g = math.ceil(mod(t, return_holding_period))
            if not int(g) in rets:
                rets[int(g)] = []
            rets[int(g)].append(log_candles[int(t)] - log_candles[int(t)-return_holding_period])
            count[int(g)] = count[int(g)] + 1
            t = t + subsampling_interval
        
        r_k_avgs = []
        for k in range(len(rets[0])):
            r_k_avg = 0
            for g in rets:
                r_k_avg = r_k_avg + rets[g][k]
            r_k_avgs.append(r_k_avg / q)

        if do_winsorize:
            r_k_avgs = winsorize(r_k_avgs, limits=[winsorization_level, winsorization_level])

        rv = sum([r_k_avg*r_k_avg for r_k_avg in r_k_avgs])

        rescaled_volatility = math.sqrt(window) * math.sqrt(rv)
        return rescaled_volatility