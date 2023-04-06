from abc import ABC, abstractmethod

class ServiceOptionMarketRetrieverInterface(ABC):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_markets') and
                callable(subclass.get_markets)
                )

    @abstractmethod
    def get_markets(self) -> None:
        pass