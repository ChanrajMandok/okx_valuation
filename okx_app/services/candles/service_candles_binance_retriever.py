import os

from binance.client import BaseClient
from binance.client import Client, HistoricalKlinesType, BinanceAPIException
from datetime import datetime, timedelta, timezone

from okx_app.enum.enun_na_fill import EnumNaFill

from okx_app.model.model_candle import ModelCandle
from okx_app.model.model_candle_hourly import ModelCandleHourly
from okx_app.model.model_currency import ModelCurrency

from okx_app.store.store_exchange_retriever import StoreExchangeRetriever

    ##########################################
    # Service Retrieves Candles From Binance #
    ##########################################


class ServiceCandlesBinanceRetriever():
    
    ## Lookback period utilised to loop over Binance Client get_historical_klines to retrieve Candles for timeframes >1000 Candles 

    def __init__(self, 
                 ) -> None:
        
        self.client = Client(os.environ['BINANCE_API_KEY'], os.environ['BINANCE_SECRET_KEY'])
        self.exchange = StoreExchangeRetriever().get_exchange(value='BINANCE')

    def get_candles(self, 
                    base_ccy: ModelCurrency, 
                    quote_ccy: ModelCurrency, 
                    lookback_period : int,
                    interval: str = BaseClient.KLINE_INTERVAL_1MINUTE, 
                    save_in_bulk: bool=True):
        
        end_time = datetime.now()
        
        if interval == BaseClient.KLINE_INTERVAL_1MINUTE:
            ModelCandleClass = ModelCandle
            end_time = end_time.replace(second=0, microsecond=0, minute=end_time.minute)
            unit = 60
        elif interval == BaseClient.KLINE_INTERVAL_1HOUR:
            ModelCandleClass = ModelCandleHourly
            end_time = end_time.replace(second=0, microsecond=0, minute=0, hour=end_time.hour)
            unit = 60*60
        else:
            raise Exception(f"interval {interval} not supported")
        
        from_ticker = base_ccy.value
        to_ticker = quote_ccy.value
        
        start_date = end_time + timedelta(days= -lookback_period)

        date_from_0 = (start_date-datetime(1970,1,1)).total_seconds()
        date_to = (end_time-datetime(1970,1,1)).total_seconds() 
        
        response_list = []
        date_from = max(int(date_to)-1000*unit, int(date_from_0))
        while int(date_to) > int(date_from_0):
            try:
                response = self.client.get_historical_klines(symbol=f"{from_ticker}{to_ticker}",
                                                            interval=interval,
                                                            start_str=datetime.fromtimestamp(timestamp=date_from, tz=timezone.utc).strftime("%H:%M:%S, %d %B, %Y"),
                                                            end_str=datetime.fromtimestamp(timestamp=date_to, tz=timezone.utc).strftime("%H:%M:%S, %d %B, %Y"),
                                                            klines_type=HistoricalKlinesType.SPOT)
                response_list.extend(response)
            except BinanceAPIException as e:
                print("Binance exception, status_code: %s, message: %s\n" % (e.status_code,e.message))
            if date_from == int(date_from_0):
                break
            date_to = date_from-unit
            date_from = max(int(date_from)-1000*unit, int(date_from_0))
            
        response_list = sorted(response_list)

        candles = []
        dates = []
        date_ms = response_list[0][0]
        previous_candle = None
        for c in range(len(response_list)):
            
            # candle date
            candle_binance = response_list[c]
            candle_binance_date_ms = int(candle_binance[0])
            
            while date_ms < candle_binance_date_ms:
                candle = previous_candle
                candle.date = datetime.fromtimestamp(int(date_ms)/1000, tz=timezone.utc)
                candle.fill_method = EnumNaFill.BACK_FILL
                if interval == BaseClient.KLINE_INTERVAL_1HOUR:
                    candle.time_of_year = candle.date.strftime('%m:%d:%H')
                else:
                    candle.time_of_week = candle.date.strftime('%w:%H:%M')
                candles.append(candle)
                dates.append(candle.date)
                
                # date expected next
                date_ms = date_ms + 60*60*1000
            
            candle_binance_date =  datetime.fromtimestamp(candle_binance_date_ms/1000, tz=timezone.utc)
            candle = ModelCandleClass(
                    exchange = self.exchange,
                    base_ccy = base_ccy,
                    quote_ccy = quote_ccy,
                    date = candle_binance_date,
                    open = float(candle_binance[1]),
                    close = float(candle_binance[2]),
                    high = float(candle_binance[3]),
                    low = float(candle_binance[4])
                )
            if interval == BaseClient.KLINE_INTERVAL_1HOUR:
                candle.time_of_year = candle.date.strftime('%m:%d:%H')
            else:
                candle.time_of_week = candle.date.strftime('%w:%H:%M')
            candles.append(candle)
            dates.append(candle.date) 
            
            previous_candle = candle

            # date expected next
            date_ms = date_ms + 60*60*1000

        ## if not save in bulk, update the single missing candles 
        if save_in_bulk:
            ModelCandleClass.objects.bulk_create(candles, ignore_conflicts=True)
        
        else:    
            existing_records = ModelCandleClass.objects.filter(
                    exchange=self.exchange,
                    base_ccy=base_ccy,
                    quote_ccy=quote_ccy,
                    date__in=dates
                )
            if interval == BaseClient.KLINE_INTERVAL_1HOUR:
                existing_records = existing_records.values_list('id', 'date', 'time_of_year')
            else:
                existing_records = existing_records.values_list('id', 'date', 'time_of_week')
            existing_dates = [ed[1] for ed in existing_records]
            for candle in candles:
                if not candle.date in existing_dates:
                    for candle_id in [ed[0] for ed in existing_records if ed[2] == 
                                      (candle.time_of_year if interval == BaseClient.KLINE_INTERVAL_1HOUR else candle.time_of_week)]:
                        ModelCandleClass.objects.get(id=candle_id).delete()
                    candle.save()
        