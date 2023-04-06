import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.interpolate import griddata
from typing import Dict, List

from okx_app.model.model_option_market import ModelOptionMarket

from okx_app.enum.enum_option_type import EnumOptionType

from okx_app.services.plot.service_plot_interface import ServicePlotVolatilityInterface

    #############################################################
    # Service Plots Volatility Surface Area from entire dataset #
    #############################################################


class ServicePlotVolatilitySurfaceArea(ServicePlotVolatilityInterface):

    def __init__(self) -> None:
        super(ServicePlotVolatilitySurfaceArea, self).__init__()

    def plot(self, option_markets: Dict[str, List[ModelOptionMarket]]) -> plt:

        # Initialize data arrays
        all_strikes = []
        all_maturities = []
        all_vols = []

        for key, data in option_markets.items():
            dte = int(round(float(key) * 365, 0))
            unique_strikes = set()
            for option in data['Okx']:
                unique_strikes.add(float(option.strike))

            unique_strikes_list = sorted(unique_strikes, reverse=False)

            for strike in unique_strikes_list:
                call_vol_list = []
                put_vol_list = []
                for options in option_markets.values():
                    for option in options['Okx']:
                        if option.strike == strike:
                            if option.option_type == EnumOptionType.CALL.value:
                                if all(val is not np.nan for val in [option.strike, option.bsm_implied_vol, option.reference]):
                                    call_vol_list.append(option.bsm_implied_vol)
                            else:
                                if all(val is not np.nan for val in [option.strike, option.bsm_implied_vol, option.reference]):
                                    put_vol_list.append(option.bsm_implied_vol)

                if len(call_vol_list) > 0 and len(put_vol_list) > 0:
                    call_vol = sum(call_vol_list) / len(call_vol_list)
                    put_vol = sum(put_vol_list) / len(put_vol_list)
                    vol = (call_vol + put_vol) / 2
                    all_strikes.append(strike)
                    all_maturities.append(dte)
                    all_vols.append(vol)

        # Create grid for surface plot
        strike_prices = np.linspace(min(all_strikes), max(all_strikes), 100)
        days_to_expiry = np.linspace(min(all_maturities), max(all_maturities), 100)
        X, Y = np.meshgrid(strike_prices, days_to_expiry)
        Z = griddata((all_strikes, all_maturities), all_vols, (X, Y), method='linear')

        # Create surface plot
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, projection='3d')
        surface = ax.plot_surface(X, Y, Z, cmap=cm.inferno)
        ax.set_xlabel('Strike Price')
        ax.set_ylabel('Days to Expiry')
        ax.set_zlabel('Volatilty')
        plt.title(f" Okx Volatility Surface Area")
        fig.colorbar(surface, shrink=0.5, aspect=5) # Add colorbar
        plt.title(f"Okx Volatility Surface Area")
        plt.rcParams.update({'font.size': 12}) # Increase font size
        ax.view_init(elev=30, azim=120) # Adjust lighting
        plt.show(block=False)