import warnings
import numpy as np
from scipy.stats import norm

from okx_app.enum.enum_option_type import EnumOptionType
N = norm.cdf

    ###########################################
    # Service Implements Black Scholes Merton #
    ###########################################


class ServicePricerBlackScholes:
    
    def bs_put(self, S, K, T, r, vol):
        d1 = round((np.log(S/K)+(r+0.5*vol*vol)*T)/(vol*np.sqrt(T)),8)
        d2 = round((d1-vol*np.sqrt(T)),5)
        return round((np.exp(-r*T)*K*norm.cdf(-d2)-S*norm.cdf(-d1)),8)
    
    def bs_call(self, S, K, T, r, vol):
        d1 = round((np.log(S/K)+(r+0.5*vol*vol)*T)/(vol*np.sqrt(T)),8)
        d2 = round((d1-vol*np.sqrt(T)),8)
        return round((S*norm.cdf(d1)-np.exp(-r*T)*K*norm.cdf(d2)),8)

    def bs_vega(self, S, K, T, r, sigma):
        d1 = round((np.log(S/K)+(r+0.5*sigma*sigma)*T)/(sigma*np.sqrt(T)),8)
        return round((S*norm.pdf(d1)*np.sqrt(T)),8)

    def find_vol(self, target_value, S, K, T, r, option_type, *args):
        MAX_ITERATIONS = 200
        PRECISION = 1.0e-5
        sigma = 1.0
        try:
            for i in range(0, MAX_ITERATIONS):
                if option_type == EnumOptionType.CALL.value:
                    price = self.bs_call(S, K, T, r, sigma)
                else:
                    price = self.bs_put(S, K, T, r, sigma)
                vega = self.bs_vega(S, K, T, r, sigma)
                diff = target_value - price  # our root
                if (abs(diff) < PRECISION):
                    return sigma
                if vega == 0:
                    return np.nan
                sigma = sigma + diff/vega # f(x) / f'(x)
        except Exception as e:
            return np.nan
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        return sigma # value wasn't found, return best guess so far