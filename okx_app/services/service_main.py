import os
import math
import json
from okx_app.decorators.decorator_option_market_retriever_interface_imports import decorator_option_market_retriever_interface_imports
from okx_app.decorators.decorator_plot_volatilty_interface_imports import decorator_plot_volatilty_interface_imports

from okx_app.services.retrievers.service_option_markets_retriever_interface import ServiceOptionMarketRetrieverInterface
from okx_app.services.plot.service_plot_interface import ServicePlotVolatilityInterface

from okx_app.services.volatility_implied.service_option_market_implied_vol_bsm_estimator import ServiceOptionMarketImpliedBSMEstimator
from okx_app.services.maturities.service_maturities_dict_from_option_markets_list import ServiceMaturitiesDictFromOptionMarketDict
from okx_app.services.maturities.service_maturities_retrieve_historical_vols import ServiceMaturitiesRetrieveHistoricalVols


from okx_app.services import logger


class ServiceMain():

    def __init__(self):
        self.__service_option_market_implied_vol_bsm_estimator   = ServiceOptionMarketImpliedBSMEstimator()
        self.service_maturities_dict_from_option_markets_list    = ServiceMaturitiesDictFromOptionMarketDict()
        self.service_maturities_retrieve_historical_vols         = ServiceMaturitiesRetrieveHistoricalVols()

    @decorator_plot_volatilty_interface_imports
    @decorator_option_market_retriever_interface_imports
    def get_markets(self,
                    service_option_markets_okx_retriever = None,
                    service_plot_volatilty_surface_area = None,
                    service_plot_volatilty_smile = None,
                    service_option_markets_bybit_retriever = None,
                    ):
        
        # Get Option Markets from OKX & Bybit utilising Interface for efficency
        option_markets = {}
        for cls in ServiceOptionMarketRetrieverInterface.__subclasses__():
            exchange = str(cls.__name__.replace('ServiceOptionMarkets', '').replace('Retriever', ''))
            logger.info(f"Retrieving ETH-USD Option Markets from {exchange} ")
            option_markets[f"{exchange}"] = (cls().get_markets())
            logger.info(f"{len(cls().get_markets())} ETH-USD Option Markets retrived from {exchange} ")

        # Add bsm_iv to ModelOptionMarket objects for use later
        logger.info('Calculating BSM Derived Implied Volatilty')
        for exchange, markets in option_markets.items():
            for market in markets:
                self.__service_option_market_implied_vol_bsm_estimator.calculate_implied_volatility(market=market, reference=market.reference)

        # Get list of maturities and corresponding options (key=maturity: value=list of options)
        maturities_dict = self.service_maturities_dict_from_option_markets_list.get_maturities(option_markets=option_markets)
    
        for term, exchange_options in maturities_dict.items():
            for exchange, options in exchange_options.items():
                dte = int(round(float(term) * 365, 0))
                logger.info(f"{len(options)} {dte} DTE options in {exchange} dataset")

        for cls in ServicePlotVolatilityInterface.__subclasses__():
            plot = str(cls.__name__.replace('ServicePlotVolatility', ''))
            logger.info(f"Plotting Volatilty {plot} ")
            logger.info(f"If Paused, close plot to continue")
            cls().plot(option_markets=maturities_dict)

        if not os.environ['BINANCE_API_KEY'] == '' :
            logger.info(f"Retrieving Short term Historical Vol Estimators")
            historicals_dict = {k: v for k, v in sorted(maturities_dict.items(), reverse=True) if k < float(3/365)}
            final_dict = self.service_maturities_retrieve_historical_vols.get_vols(maturities_dict=historicals_dict)
            
            for k, v in final_dict.items():
                print(json.dumps(f"{math.ceil(k*365)} DTE Historical Volatilty Data : {v}"))
            



        




         
            
        
        
        