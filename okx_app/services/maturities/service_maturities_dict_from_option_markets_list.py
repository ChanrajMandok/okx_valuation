from typing import Dict, List

from okx_app.model.model_option_market import ModelOptionMarket

    #########################################################################################
    # Service Sorts Dict of Options into Maturiteis Dict -> term : maturity:list of options #
    #########################################################################################


class ServiceMaturitiesDictFromOptionMarketDict:
    
    def get_maturities(self, option_markets: Dict[str, List[ModelOptionMarket]]) -> Dict:


        # segregate dict of options into maturirity: exhchange: List of ModelOptionPosition. 
        maturities = {}
        for exchange, markets in option_markets.items():
            for market in markets:
                if isinstance(market, ModelOptionMarket):
                    mkt_time_to_maturity = round(market.term, 8)
                if not mkt_time_to_maturity in list(maturities.keys()):
                    maturities[mkt_time_to_maturity] = {exchange: []}
                if not (market.strike, market.option_type) in [(m.strike, m.option_type) for m in maturities[mkt_time_to_maturity][exchange]]:
                    maturities[mkt_time_to_maturity][exchange].append(market)
        
        sorted_maturities = {k: v for k, v in sorted(maturities.items(), reverse=True)}
        return sorted_maturities

                

