import os
import logging

# create logger
logger = logging.getLogger('Option_valuation')
logger.setLevel(logging.INFO)

logger.propagate = 0

# create console handler and set level to debug
ch = logging.StreamHandler()

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d:%m:%y %H:%M:%S')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


# registering services

path = os.path.dirname(os.path.abspath(__file__))

__all__ = []
for py in [f[:-3] for f in os.listdir(path) if f.endswith('.py') and f != '__init__.py' and not f.endswith('interface.py')]:
    __all__.append(py)
