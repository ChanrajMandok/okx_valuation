import numpy as np

    #############################################################
    # Service Implements Quanto to Calc Vol on non-trades pairs #
    #############################################################


class ServicePricerQuanto:

    def find_vol_sq(self, vol1: float, vol2: float, correl: float):
        return (float(vol1)**2) + (float(vol2)**2) - (correl*vol1*vol2*2.0)
    
    def find_vol(self, vol1: float, vol2: float, correl: float):
        vol_sq = self.find_vol_sq(vol1, vol2, correl)
        return np.sqrt(vol_sq)
