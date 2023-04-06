from okx_app.services.retrievers.service_option_markets_bybit_retriever import ServiceOptionMarketsBybitRetriever
from okx_app.services.retrievers.service_option_markets_okx_retriever import ServiceOptionMarketsOkxRetriever

service_option_markets_bybit_retriever  = ServiceOptionMarketsBybitRetriever
service_option_markets_okx_retriever    = ServiceOptionMarketsOkxRetriever

    #########################################################
    # Decorator imports all Market Retrievers for interface #
    #########################################################


def decorator_option_market_retriever_interface_imports(func):
    """
    Decorator for importing all Market Retrievers to a function.
    """
    def wrapper(*args, **kwargs):
        return func(*args, 
                     service_option_markets_bybit_retriever   = service_option_markets_bybit_retriever,
                     service_option_markets_okx_retriever     = service_option_markets_okx_retriever,
                     **kwargs)

    return wrapper