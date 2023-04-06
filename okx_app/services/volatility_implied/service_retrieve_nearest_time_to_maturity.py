import numpy as np

from typing import List

from okx_app.model.model_option_market import ModelOptionMarket

    ########################################################################################
    # Service Pulls the nearest maturities from list to options to use vanna Volga Pricing #
    ########################################################################################


class ServiceRetrieveNearestTimeToMaturity:

    def get_nearest_times_to_maturity(self, term_in_days: float, markets: List[ModelOptionMarket]):
                    
        time_to_maturities = [t for t in list(markets.keys()) if len(markets[t]) >= 3]
        
        if len(time_to_maturities) == 0:
            return -99999, -99999, -99999
        
        term_index = np.argmin(np.abs(np.array(time_to_maturities)-term_in_days))
        nearest_time_to_maturity = time_to_maturities[term_index] 
        
        time_to_maturities[term_index] = -99999
        
        term_index_2 = np.argmin(np.abs(np.array(time_to_maturities)-term_in_days))
        second_nearest_time_to_maturity = time_to_maturities[term_index_2] 
        
        time_to_maturities[term_index_2] = -99999
        
        term_index_3 = np.argmin(np.abs(np.array(time_to_maturities)-term_in_days))
        third_nearest_time_to_maturity = time_to_maturities[term_index_3] 
        
        return nearest_time_to_maturity, second_nearest_time_to_maturity, third_nearest_time_to_maturity