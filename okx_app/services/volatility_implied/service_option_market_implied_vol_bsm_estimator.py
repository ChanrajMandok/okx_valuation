from okx_app.enum.enum_exchange import EnumExchange

from okx_app.model.model_option_market import ModelOptionMarket

from okx_app.services.pricers.service_pricer_black_scholes import ServicePricerBlackScholes
from okx_app.services.quote.service_quote_bybit_retriever import ServiceQuoteBybitRetriever
from okx_app.services.quote.service_quote_okx_retriever import ServiceQuoteOkxRetriever

    #####################################################################################
    # Service Implements BSM Pricer to add bsm_implied_vol to ModelOptionMarket objects #
    #####################################################################################


class ServiceOptionMarketImpliedBSMEstimator():
    
    def __init__(self) -> None:
        self.service_black_scholes_pricer   = ServicePricerBlackScholes()
        self.service_quote_okx_retriever    = ServiceQuoteOkxRetriever()
        self.service_quote_bybit_retriever  = ServiceQuoteBybitRetriever()
    
    def calculate_implied_volatility(self, market: ModelOptionMarket, reference: float = None) -> float:
        
        if not reference:
            reference = market.reference
        
        if not reference:
            if market.exchange.value == EnumExchange.OKX.value:
                quote = self.service_quote_okx_retriever.get_price(
                    base_currency=market.base_currency, 
                    quote_currency=market.quote_currency
                )
            if market.exchange.value == EnumExchange.BYBIT.value:
                quote = self.service_quote_bybit_retriever.get_price(
                    base_currency=market.base_currency, 
                    quote_currency=market.quote_currency
                )    
                
                if not quote:
                    return market
                
                market.strike = quote.last
                
        implied_vol = self.service_black_scholes_pricer.find_vol(
                target_value=(market.bid_price+market.ask_price)/2.0, 
                S=reference, 
                K=market.strike, 
                T=market.term, 
                r=0.0, 
                option_type=market.option_type
            )

        market.bsm_implied_vol = implied_vol
        return market
