from progressindicator.base import BaseProvider
from progressindicator.tags import *
import time

class ETAProvider(BaseProvider):
    """Default Provider for an estimate of the time remaining for the
    completion of the task underway. The tag for this provider is `eta`.
    This provider is used by the built-in `ETA` extension.
    """
    def __init__(self):
        BaseProvider.__init__(self,
                              tag=TAG_ETA,
                              requirements=[TAG_TIME_SINCE_BEGIN,
                                            TAG_PERCENTAGE])

    def on_validated(self, params):
        try:
            eta = params[0] * (100 - params[1]) / params[1]
            self.set_value(eta)
        except ZeroDivisionError:
            pass
            

class ETANewProvider(BaseProvider):
    """Default Provider for an alternate estimate of the time remaining for the
    completion of the task underway. The tag for this provider is `eta_new`.
    This provider is used by the built-in `ETANew` extension.
    """
    def __init__(self):
        BaseProvider.__init__(self,
                              tag=TAG_ETA_NEW,
                              requirements=[TAG_ITERATIONS,
                                            TAG_PERCENTAGE,
                                            TAG_RATE])

    def on_validated(self, params):
        try:
            expected_left_iterations = params[0] * (100 - params[1]) / params[1]
            eta_new = expected_left_iterations / params[2]
            self.set_value(eta_new)
        except ZeroDivisionError:
            pass
            


class RateProvider(BaseProvider):
    """Default Provider for the rate at which calls to `publish` are made.
    The tag for this provider is `rate`. This provider is used by the
    built-in `Rate` extension.
    """
    def __init__(self):
        BaseProvider.__init__(self,
                              tag=TAG_RATE,
                              requirements=[TAG_ITERATIONS])
        self.time_prev = time.time()
        #self.value_start = 0
        self.value_prev = 0

    def on_begin(self, params):
        #try:
            #self.set_value(1/params[1])
        #except ZeroDivisionError:
        self.set_value(0)

    def on_validated(self, params):
        value = params[0]
        time_ = time.time()
        try:
            rate = (value - self.value_prev) / (time_ - self.time_prev)
        except ZeroDivisionError:
            rate = 0
        self.set_value(rate)
        self.value_prev, self.time_prev = value, time_
