
    #################################################################
    # Model for ModelQuote Objects, representing Prices [Not in DB] #
    #################################################################


class ModelQuote:
    
    def __init__(self,
                 last: float,
                 bid: float = None,
                 ask: float = None,
                 ts: int = None
                 ) -> None:
                 self.last = last
                 self.bid = bid
                 self.ask = ask
                 self.ts = ts