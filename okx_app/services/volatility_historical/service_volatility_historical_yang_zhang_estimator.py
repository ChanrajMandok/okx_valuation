import numpy as np

from cmath import sqrt
from statistics import mean
from datetime import datetime, timezone, timedelta

from okx_app.model.model_candle import ModelCandle
from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange
from okx_app.services.candles.service_candles_binance_retriever import ServiceCandlesBinanceRetriever

from okx_app.services.volatility_historical.service_volatility_historical_estimator_interface import ServiceVolatilityHistoricalEstimatorInterface

    #####################################################################
    # Service Calculates Rogers-Satchell & YZ Vol on Historical Candles #
    #####################################################################


class ServiceVolatilityHistoricalYangZhangEstimator(ServiceVolatilityHistoricalEstimatorInterface):

    def __init__(self) -> None:
        super(ServiceVolatilityHistoricalYangZhangEstimator, self).__init__()
        self.binance_candles_retriever = ServiceCandlesBinanceRetriever()
    
    def estimate(self, 
                 exchange: ModelExchange,
                 base_ccy: ModelCurrency, 
                 quote_ccy: ModelCurrency, 
                 window: int,
                 to_date: datetime = None,
                 **kwargs):
        
        to_date = to_date if to_date else datetime.now(timezone.utc)
        to_date_minute = to_date.replace(second=0, microsecond=0, minute=to_date.minute)
        from_date_minute = to_date_minute - timedelta(minutes=window)
        candles = ModelCandle.objects.filter(
            exchange=exchange,
            base_ccy=base_ccy,
            quote_ccy=quote_ccy,
            date__gte=from_date_minute
        ).order_by('-date')
        
        window = len(candles)
        
        sigma_rs_elements = []
        log_oc_shift = []
        log_co = []
        
        for i in range(1, len(candles), 1):

            # Rogers-Satchell

            log_hc = np.log(candles[i].high/candles[i].close)
            log_ho = np.log(candles[i].high/candles[i].open)
            log_lc = np.log(candles[i].low/candles[i].close)
            log_lo = np.log(candles[i].low/candles[i].open)
            sigma_rs_elements.append(log_hc*log_ho + log_lc*log_lo)
            
            # Yang Zhang
                        
            log_oc_shift.append(np.log(candles[i].open/candles[i-1].close))
            log_co.append(np.log(candles[i].close/candles[i].open))
            
                
        # Rogers-Satchell
        
        sigma_rs_2 = sum(sigma_rs_elements) / len(sigma_rs_elements)
        
        # Yang Zhang
        
        avg_log_oc_shift = mean(log_oc_shift)
        avg_log_co = mean(log_co)
        sigma_o_2 = (1.0/(window-1))*sum([(e - avg_log_oc_shift)**2 for e in log_oc_shift])
        sigma_c_2 = (1.0/(window-1))*sum([(e - avg_log_co)**2 for e in log_co])
        k = 0.34 / (1.34 + (window + 1) / (window - 1))
        sigma_yz = sqrt(sigma_o_2+k*sigma_c_2+(1-k)*sigma_rs_2)
        sigma_yz_annualized = sigma_yz*sqrt(365*24*60)
        
        return float(abs(sigma_yz_annualized))
      