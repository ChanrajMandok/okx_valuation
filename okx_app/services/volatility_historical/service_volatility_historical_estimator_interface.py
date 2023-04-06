from datetime import datetime
from abc import ABC, abstractmethod

from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange


class ServiceVolatilityHistoricalEstimatorInterface(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'estimate') and
                callable(subclass.estimate)
                )
        
    @abstractmethod    
    def estimate(self, 
                 exchange: ModelExchange,
                 base_ccy: ModelCurrency, 
                 quote_ccy: ModelCurrency, 
                 window: int,
                 subsampling_interval: int = None,
                 to_date: datetime = None,
                 do_winsorizebool:bool = None,
                 winsorization_level: float = None,
                 return_holding_period:int = None,
                 instrument_term: int = None,
                 **kwargs):
        pass