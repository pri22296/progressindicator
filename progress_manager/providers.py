from progress_manager.base import BaseProvider
import time

"""class PercentageProvider(BaseProvider):
    def __init__(self):
        BaseProvider.__init__(self,
                              requirements=['min_value',
                                            'value',
                                            'max_value'],
                              tag='percentage')

    def _on_begin(self, params):
        self.set_value(0)

    def _on_validated(self, params):
        try:
            percentage = 100 * (params[1] - params[0]) / (params[2] - params[0])
            self.set_value(percentage)
        except ZeroDivisionError:
            pass
            

    def _on_end(self, params):
        self.set_value(100)


class IterationsProvider(BaseProvider):
    def __init__(self):
        BaseProvider.__init__(self,
                              requirements=[],
                              tag='iterations')

    def _on_begin(self, params):
        self.set_value(0)

    def _on_validated(self, params):
        self.set_value(self.get_value() + 1)

class BeginTimeProvider(BaseProvider):
    def __init__(self):
        BaseProvider.__init__(self,
                              requirements=[],
                              tag='begin_time')

    def _on_begin(self, params):
        import time
        self.set_value(time.time())

    def _on_end(self, params):
        self.set_value(None)

class EndTimeProvider(BaseProvider):
    def __init__(self):
        BaseProvider.__init__(self,
                              requirements=[],
                              tag='end_time')

    def _on_begin(self, params):
        self.set_value(None)

    def _on_end(self, params):
        import time
        self.set_value(time.time())


class TimeElapsedProvider(BaseProvider):
    def __init__(self):
        BaseProvider.__init__(self,
                              requirements=['begin_time'],
                              tag='time_since_begin')

    def _on_begin(self, params):
        self.set_value(0)

    def _on_validated(self, params):
        self.set_value(time.time() - params[0])

class DeltaTimeProvider(BaseProvider):
    def __init__(self):
        BaseProvider.__init__(self,
                              requirements=['time_since_begin'],
                              tag='deltatime')
        self._time = 0
        
    def _on_validated(self, params):
        self.set_value(params[0] - self._time)
        self._time = params[0]"""

class ETAProvider(BaseProvider):
    def __init__(self):
        BaseProvider.__init__(self,
                              requirements=['time_since_begin',
                                            'percentage'],
                              tag='eta')

    def _on_validated(self, params):
        try:
            eta = params[0] * (100 - params[1]) / params[1]
            self.set_value(eta)
        except ZeroDivisionError:
            pass
            

class ETANewProvider(BaseProvider):
    def __init__(self):
        BaseProvider.__init__(self,
                              requirements=['iterations',
                                            'percentage',
                                            'rate'],
                              tag='eta_new')

    def _on_validated(self, params):
        try:
            expected_left_iterations = params[0] * (100 - params[1]) / params[1]
            eta_new = expected_left_iterations / params[2]
            self.set_value(eta_new)
        except ZeroDivisionError:
            pass
            


class RateProvider(BaseProvider):
    def __init__(self):
        BaseProvider.__init__(self,
                              requirements=['iterations',],
                              tag='rate')
        self.time_prev = time.time()
        #self.value_start = 0
        self.value_prev = 0

    def _on_begin(self, params):
        #try:
            #self.set_value(1/params[1])
        #except ZeroDivisionError:
        self.set_value(0)

    def _on_validated(self, params):
        value = params[0]
        time_ = time.time()
        try:
            rate = (value - self.value_prev) / (time_ - self.time_prev)
        except ZeroDivisionError:
            rate = 0
        self.set_value(rate)
        self.value_prev, self.time_prev = value, time_
