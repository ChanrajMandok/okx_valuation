import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from scipy.interpolate import splev, splrep
from typing import Dict, List

from okx_app.model.model_option_market import ModelOptionMarket

from okx_app.enum.enum_option_type import EnumOptionType

from okx_app.services.plot.service_plot_interface import ServicePlotVolatilityInterface

    ###############################################################
    # Service Plots Volatility Smile for each maturity in dataset #
    ###############################################################

class ServicePlotVolatilitySmile(ServicePlotVolatilityInterface):

    def __init__(self) -> None:
        super(ServicePlotVolatilitySmile, self).__init__()

    def plot(self, option_markets: Dict[str, List[ModelOptionMarket]] ) -> plt:

        for key, data in option_markets.items():
            dte = int(round(float(key) * 365, 0))
            unique_strikes = set()
            for option in data['Okx']:
                unique_strikes.add(float(option.strike))

            unique_strikes_list = sorted(unique_strikes, reverse=False)

            call_data = []
            put_data = []
            for strike in unique_strikes_list:
                for options in option_markets.values():
                    for option in options['Okx']:
                        if option.strike == strike:
                            if option.option_type == EnumOptionType.CALL.value:
                                if all(val is not np.nan for val in [option.strike, option.bsm_implied_vol, option.reference]):
                                    call_data.append([option.strike, option.bsm_implied_vol, option.reference])
                            else:
                                if all(val is not np.nan for val in [option.strike, option.bsm_implied_vol, option.reference]):
                                    put_data.append([option.strike, option.bsm_implied_vol, option.reference])

            # Plot volatility smile
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)

            if len(call_data) >= 3 or len(put_data) >= 3:
                call_strikes = [x[0] for x in call_data]
                call_vols = [x[1] for x in call_data]
                put_strikes = [x[0] for x in put_data]
                put_vols = [x[1] for x in put_data]

                spl_call = splrep(call_strikes, call_vols, s=1)
                spl_put = splrep(put_strikes, put_vols, s=1)

                xs = np.linspace(min(min(call_strikes), min(put_strikes)), max(max(call_strikes), max(put_strikes)), 1000)
                ys_call = splev(xs, spl_call)
                ys_put = splev(xs, spl_put)

                ax.plot(xs, ys_call, color='red', label='Calls')
                ax.plot(xs, ys_put, color='darkgreen', label='Puts')

            ax.set_xlabel('Strike Price')
            ax.set_ylabel('Implied Volatility')
            plt.title(f" Okx{dte} DTE Volatility Smile")
            ax.legend()
            ax.grid(True, which='both', linewidth=0.1)
            ax.xaxis.set_minor_locator(MultipleLocator(int(dte)))
            ax.yaxis.set_minor_locator(MultipleLocator(int(dte)))
            plt.show(block=True)
            plt.show()


