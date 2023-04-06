import numpy as np

from typing import List

from math import exp, pi, sqrt

from okx_app.enum.enum_option_type import EnumOptionType

from okx_app.model.model_option_market import ModelOptionMarket

from okx_app.services.pricers.service_pricer_black_scholes import ServicePricerBlackScholes

from okx_app.services.quote.service_quote_okx_retriever import ServiceQuoteOkxRetriever
from okx_app.services.volatility_implied.service_option_market_implied_vol_bsm_estimator import ServiceOptionMarketImpliedBSMEstimator
from okx_app.services.volatility_implied.service_retrieve_nearest_time_to_maturity import ServiceRetrieveNearestTimeToMaturity


    ######################################################################################
    # Service Implements VV Pricer, Pricing an Option Based on the Term Structure of Vol #
    ######################################################################################

class ServiceOptionMarketImpliedVolVannaVolgaEstimator():
    
    def __init__(self) -> None:
        self.service_black_scholes_service             = ServicePricerBlackScholes()
        self.service_exchange_okx                      = ServiceQuoteOkxRetriever()
        self.service_option_market_implied_vol_pricer  = ServiceOptionMarketImpliedBSMEstimator()
        self.service_retrieve_nearest_time_to_maturity = ServiceRetrieveNearestTimeToMaturity()
        

        """
        Paper Utilised to Design & implement in python
        https://www.researchgate.net/publication/285662078_The_Vanna-Volga_method_for_implied_volatilities
        """
    
    def calculate_implied_volatility(self,
                 strike: float,
                 term: float,
                 markets: List[ModelOptionMarket]) -> float:
        
        # give markets for a single exchange on one pair
        
        exchanges = list(set([d.exchange for d in markets]))
        
        if len(exchanges) > 1:
            raise Exception("markets should originate from a single exchange")
        
        pairs = list(set([d.base_currency.value + "/" + d.quote_currency.value for d in markets]))

        if len(pairs) > 1:
            raise Exception("markets should relate to the same pair")

        mkts = {}
        
        for mkt in markets:
            if isinstance(mkt, ModelOptionMarket):
                mkt_time_to_maturity = round(mkt.term, 5)
            if not mkt_time_to_maturity in list(mkts.keys()):
                mkts[mkt_time_to_maturity] = []
            if not mkt.strike in [m.strike for m in mkts[mkt_time_to_maturity]]:
                mkts[mkt_time_to_maturity].append(mkt)
        
        (nearest_time_to_maturity, second_nearest_time_to_maturity, third_nearest_time_to_maturity) = \
            self.service_retrieve_nearest_time_to_maturity.get_nearest_times_to_maturity(term_in_days=term, markets=mkts)
            
        if nearest_time_to_maturity == -99999 or second_nearest_time_to_maturity == -99999 or third_nearest_time_to_maturity == -99999:
            return 0
        
        volatilities = {}
        
        for time_to_maturity in (nearest_time_to_maturity, second_nearest_time_to_maturity, third_nearest_time_to_maturity):
            
            mkts_for_time_to_maturity = mkts[time_to_maturity]
            
            if len(mkts_for_time_to_maturity) > 3:
                strike_distances = np.abs(np.array([mkt.strike for mkt in mkts_for_time_to_maturity])-strike)
                strike_distances_sorted_indexes =  sorted(range(len(strike_distances)), key=lambda k: strike_distances[k])
                mkts_for_time_to_maturity_sub = [mkts_for_time_to_maturity[i] for i in strike_distances_sorted_indexes[0:3]]
            else:
                mkts_for_time_to_maturity_sub = mkts_for_time_to_maturity
                
            mkts_for_time_to_maturity_sub.sort(key=lambda x: x.strike, reverse=False)
            
            s0 = strike
            k = strike
            k1 = mkts_for_time_to_maturity_sub[0].strike
            k2 = mkts_for_time_to_maturity_sub[1].strike
            k3 = mkts_for_time_to_maturity_sub[2].strike
            
            vs_sp = []
            vegas_sp = []
            for mkt in mkts_for_time_to_maturity_sub:
                if isinstance(mkt, ModelOptionMarket):
                    mkt = self.service_option_market_implied_vol_pricer.calculate_implied_volatility(mkt, reference=s0)
                vs_sp.append(mkt.bsm_implied_vol)
                vegas_sp.append(self.vega(s0, mkt.strike, mkt.bsm_implied_vol, time_to_maturity))
                
            sigma = next((mkt.bsm_implied_vol for mkt in mkts_for_time_to_maturity_sub if mkt.bsm_implied_vol is not None), None)
            
            xs = self.xs(s0, k, k1, k2,k3, sigma, time_to_maturity)
            
            C1_mkt = (mkts_for_time_to_maturity_sub[0].bid_price + mkts_for_time_to_maturity_sub[0].ask_price)/2.0/s0
            C3_mkt = (mkts_for_time_to_maturity_sub[2].bid_price + mkts_for_time_to_maturity_sub[2].ask_price)/2.0/s0
            
            if mkts_for_time_to_maturity_sub[0].option_type == EnumOptionType.CALL.value:
                C1_premium_to_bs = C1_mkt - self.service_black_scholes_service.bs_call(s0, k1, time_to_maturity, 0, sigma)/s0
            else:
                C1_premium_to_bs = C1_mkt + 1 - k1/s0 - self.service_black_scholes_service.bs_call(s0, k1, time_to_maturity, 0, sigma)/s0
            
            if mkts_for_time_to_maturity_sub[2].option_type == EnumOptionType.CALL.value:
                C3_premium_to_bs = C3_mkt - self.service_black_scholes_service.bs_call(s0, k3, time_to_maturity, 0, sigma)/s0
            else:
                C3_premium_to_bs = C3_mkt + 1 - k3/s0 - self.service_black_scholes_service.bs_call(s0, k3, time_to_maturity, 0, sigma)/s0
            
            option_put_price = self.service_black_scholes_service.bs_put(s0, k, time_to_maturity, 0, sigma)/s0 \
                + xs[0]*C1_premium_to_bs\
                + xs[2]*C3_premium_to_bs
                
            volatilities[time_to_maturity] = self.service_black_scholes_service.find_vol(option_put_price*s0, s0, k, time_to_maturity, 0, EnumOptionType.CALL.value)
            
        weight = (second_nearest_time_to_maturity-term)/(second_nearest_time_to_maturity-nearest_time_to_maturity)
        
        weight2 = (third_nearest_time_to_maturity-term)/(third_nearest_time_to_maturity-second_nearest_time_to_maturity)
        
        vol2 = weight*(volatilities[nearest_time_to_maturity]**2)*(nearest_time_to_maturity/term) \
                         + (1.0-weight)*(volatilities[second_nearest_time_to_maturity]**2)*(second_nearest_time_to_maturity/term)
        
        if vol2 < 0:
            vol2_2 = weight2*(volatilities[second_nearest_time_to_maturity]**2)*(second_nearest_time_to_maturity/term) \
                         + (1.0-weight2)*(volatilities[third_nearest_time_to_maturity]**2)*(third_nearest_time_to_maturity/term)
            if vol2_2 > 0:
                volatility = sqrt(vol2_2)    
            else:
                volatility = volatilities[nearest_time_to_maturity]
        else:
            volatility= sqrt(vol2)
        
        return volatility  
        
    def d_1(self, s0, k, sigma, T):
        denom = sigma*sqrt(T)
        return (np.log(s0/k)+0.5*denom**2)/denom
    
    def vega(self, s0, k, sigma, T):
        d1 = self.d_1(s0, k, sigma, T)
        return s0*sqrt(T)*(exp(-0.5*d1**2)/sqrt(2*pi))
    
    def xs(self, s0, k, k1, k2, k3, sigma, T) -> List[float]:
        vega_k = self.vega(s0, k, sigma, T)
        vega_k1 = self.vega(s0, k1, sigma, T)
        vega_k2 = self.vega(s0, k2, sigma, T)
        vega_k3 = self.vega(s0, k3, sigma, T)
        return [
            (vega_k/vega_k1)*(np.log(k2/k)*np.log(k3/k))/(np.log(k2/k1)*np.log(k3/k1)),
            (vega_k/vega_k2)*(np.log(k/k1)*np.log(k3/k))/(np.log(k2/k1)*np.log(k3/k2)),
            (vega_k/vega_k3)*(np.log(k/k1)*np.log(k/k2))/(np.log(k3/k1)*np.log(k3/k2))
            ]
        
