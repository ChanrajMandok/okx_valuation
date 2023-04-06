from enum import Enum

    ##############################
    # Enum interface for NoValue #
    ##############################


class NoValue(Enum):

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
