from abc import ABC, abstractmethod
from typing import Dict, List

from okx_app.model.model_option_market import ModelOptionMarket

class ServicePlotVolatilityInterface(ABC):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'plot') and
                callable(subclass.plot)
                )

    @abstractmethod
    def plot(self,
             option_markets: Dict[str, List[ModelOptionMarket]]) -> None:
        pass