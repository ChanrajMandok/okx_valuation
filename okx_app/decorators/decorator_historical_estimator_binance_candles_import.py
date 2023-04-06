from okx_app.services.candles.service_candles_binance_retriever import ServiceCandlesBinanceRetriever

service_candles_binance_retriever = ServiceCandlesBinanceRetriever

    ###############################################
    # Decorator imports Binance Candles Retirever #
    ################################################


def decorator_historical_estimator_binance_candles_import(func):
    """
    Decorator for importing service_candles_binance_retriever into function.
    """
    def wrapper(*args, **kwargs):
        return func(*args, 
                     service_candles_binance_retriever = ServiceCandlesBinanceRetriever,
                     **kwargs)

    return wrapper