"""This module contains the BaseExtensions for progress_manager."""
from progress_manager.base import BaseExtension

class Bar(BaseExtension):
    """Extension to display ProgressBar in console.

    Parameters
    ----------
    length : int, optional
        Number of entities in the Bar.

    begin_entity : str, optional
        Symbol to indicate start of the Bar.

    filler_entity : str, optional
        Symbol which is used to show completed part of the Bar.

    empty_entity : str, optional
        Symbol which is used to show incomplete part of the Bar.

    end_entity : str, optional
        Symbol to indicate end of the Bar.
    """
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['percentage'])
        self.length = 60
        self.begin_entity = '['
        self.filler_entity = '#'
        self.empty_entity = ' '
        self.end_entity = ']'

    def _is_update_required(self, prev_params, params):
        return abs(self._get_entity_count(prev_params[0]) - self._get_entity_count(params[0])) >= 1

    def _get_entity_count(self, percentage):
        return int(percentage * self.length / 100)

    def _get_bar(self, filler_count):
        bar = (self.begin_entity
               + (self.filler_entity * filler_count)
               + (self.empty_entity
                  * (self.length - filler_count))
               + self.end_entity)
        return bar

    def _on_validated(self, params):
        current_entity_count = self._get_entity_count(params[0])
        bar = self._get_bar(current_entity_count)
        self.set_value(bar)

    def _on_invalidated(self, params):
        pass

class BouncingBar(BaseExtension):
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['time_since_begin','deltatime'], update_interval=0.1)
        self.length = 60
        self.filler = '*'
        self.begin_entity = '['
        self.end_entity = ']'
        self.empty = ' '
        self.velocity = 200
        self.position = 0

    def _get_bar(self, position):
        bar = (self.begin_entity
               + (self.empty * position)
               + self.filler
               + (self.empty * (self.length - position - 1))
               + self.end_entity)
        return bar

    def _set_position(self, pos):
        self.position = max(min(pos, self.length - 1), 0)

    def _on_validated(self, params):
        if 0 < self.position < self.length - 1:
            pass
        else:
            self.velocity *= -1
        self._set_position(self.position + int(self.velocity * params[1]))
        self.set_value(self._get_bar(self.position))

    def _on_invalidated(self, params):
        _on_validated(params)

    def _on_end(self, params):
        self.position = self.length - 1
        self.set_value(self._get_bar(self.position))

class Ellipses(BaseExtension):
    def __init__(self):
        BaseExtension.__init__(self, requirements = [], update_interval=0.3)
        self._char = '.'
        self._total_char_count = 3
        self._current_count = 0

    def _on_update(self, params):
        self._current_count = (self._current_count + 1) % (self._total_char_count + 1)
        self.set_value(self._char * self._current_count)

    def _on_end(self, params):
        self.set_value(self._char * self._total_char_count + 'Done')
        

class Timer(BaseExtension):
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['time_since_begin'])

    def _on_validated(self, params):
        time_ = params[0]
        self.set_value(self._get_formatted_time(time_))

    def _on_invalidated(self, params):
        self.set_value('UNKNOWN')

    def _get_formatted_time(self, time):
        import datetime
        return str(datetime.timedelta(0, int(time) , 0))
    

class ETA(Timer):
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['eta'])


class ETANew(Timer):
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['eta_new'])


class Rate(BaseExtension):
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['rate'])

    def _on_validated(self, params):
        rate = params[0]
        self.set_value(str(int(rate)) + ' iters/s')

    def _on_invalidated(self, params):
        self.set_value('UNKNOWN')


class Percentage(BaseExtension):
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['percentage'])

    def _on_validated(self, params):
        percentage = params[0]
        self.set_value("{:0=2}%".format(int(percentage)))

    def _on_invalidated(self, params):
        self.set_value('UNKNOWN')

