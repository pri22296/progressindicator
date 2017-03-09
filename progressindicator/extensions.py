"""This module contains the Built-in Extensions for ProgressIndicator class."""
from progressindicator.base import BaseExtension

class Bar(BaseExtension):
    """Extension to display Progress bar in console.

    Parameters
    ----------
    length : int, optional
        Number of entities in the Bar (Default 60)

    begin_entity : str, optional
        Symbol to indicate start of the Bar (Default '[')

    filler_entity : str, optional
        Symbol which is used to show completed part of the Bar (Default '#')

    empty_entity : str, optional
        Symbol which is used to show incomplete part of the Bar (Default ' ')

    end_entity : str, optional
        Symbol to indicate end of the Bar (Default ']')
    """
    def __init__(self, length=60, begin_entity='[', filler_entity='#',
                 empty_entity=' ', end_entity=']'):
        BaseExtension.__init__(self, requirements = ['percentage'])
        self.length = length
        self.begin_entity = begin_entity
        self.filler_entity = filler_entity
        self.empty_entity = empty_entity
        self.end_entity = end_entity

    def _is_update_required(self, prev_params, params):
        return abs((self._get_entity_count(prev_params[0])
                    - self._get_entity_count(params[0]))) >= 1

    def _get_entity_count(self, percentage):
        return int(percentage * self.length / 100)

    def _get_bar(self, filler_count):
        bar = (self.begin_entity
               + (self.filler_entity * filler_count)
               + (self.empty_entity
                  * (self.length - filler_count))
               + self.end_entity)
        return bar

    def on_validated(self, params):
        current_entity_count = self._get_entity_count(params[0])
        bar = self._get_bar(current_entity_count)
        self.set_value(bar)

    def on_invalidated(self, params):
        pass

class BouncingBar(BaseExtension):
    """
    This Extension displays a visual cue for a task with indeterminate
    progress.

    Parameters
    ----------

    length : int, optional
        Number of entities in the Bar (Default 60)

    begin_entity : str, optional
        Symbol to indicate start of the Bar (Default '[')

    filler_entity : str, optional
        Symbol which is used to show completed part of the Bar (Default '*')

    empty_entity : str, optional
        Symbol which is used to show incomplete part of the Bar (Default ' ')

    end_entity : str, optional
        Symbol to indicate end of the Bar (Default ']')

    velocity : int, optional
        Speed of the filler (Default 200)
    """
    def __init__(self, length=60, begin_entity='[', filler_entity='*',
                 empty_entity=' ', end_entity=']', velocity=200):
        BaseExtension.__init__(self,
                               requirements = ['time_since_begin',
                                               'deltatime'],
                               update_interval=0.1)
        self.length = length
        self.filler = filler_entity
        self.begin_entity = begin_entity
        self.end_entity = end_entity
        self.empty = empty_entity
        self.velocity = velocity
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

    def on_validated(self, params):
        if 0 < self.position < self.length - 1:
            pass
        else:
            self.velocity *= -1
        self._set_position(self.position + int(self.velocity * params[1]))
        self.set_value(self._get_bar(self.position))

    def on_invalidated(self, params):
        _on_validated(params)

    def on_end(self, params):
        self.position = self.length - 1
        self.set_value(self._get_bar(self.position))

class Ellipses(BaseExtension):
    """This Extension displays a visual cue for a task with indeterminate
    progress.
    """
    def __init__(self):
        BaseExtension.__init__(self, requirements = [], update_interval=0.3)
        self._char = '.'
        self._total_char_count = 3
        self._current_count = 0

    def on_update(self, params):
        self._current_count = (self._current_count + 1) % (self._total_char_count + 1)
        self.set_value(self._char * self._current_count)

    def on_end(self, params):
        self.set_value(self._char * self._total_char_count + 'Done')

class Alternator(BaseExtension):
    """This Extension displays items from a List in a sequential order
    in a loop after every a fixed time interval.

    Parameters
    ----------
    char_iter : iterable of str
        The set of string through which the extension should loop.
    """
    def __init__(self, char_iter):
        BaseExtension.__init__(self, requirements=[], update_interval=0.3)
        self._char_iter = char_iter
        self._current_pos = 0

    def on_update(self, params):
        self.set_value(self._char_iter[self._current_pos])
        self._current_pos = (self._current_pos + 1) % len(self._char_iter)

class Spinner(Alternator):
    """This Extension displays a visual cue for a task with indeterminate
    progress. It displays a rotating marker to indicate progress of a task.
    """
    def __init__(self):
        super.__init__(['\\', '|', '/', '-'])

class Loader(Alternator):
    """This Extension displays a visual cue for a task with indeterminate
    progress.

    Parameters
    ----------
    char : str
        The character which is to be repeated.

    n : int
        The maximum number character which should be displayed.
    """
    def __init__(self, char='.', n=3):
        char_iter = [char*i for i in range(n+1)]
        super.__init__(char_iter)
        

class Timer(BaseExtension):
    """This Extension provides total time since the task was started.
    """
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['time_since_begin'])

    def on_validated(self, params):
        time_ = params[0]
        self.set_value(self._get_formatted_time(time_))

    def on_invalidated(self, params):
        self.set_value('UNKNOWN')

    def _get_formatted_time(self, time):
        import datetime
        return str(datetime.timedelta(0, int(time) , 0))
    

class ETA(Timer):
    """This Extension displays the expected time left for the task to be
    completed.
    """
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['eta'])


class ETANew(Timer):
    """This Extension displays an alternate expected time left for the task
    to be completed.
    """
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['eta_new'])


class Rate(BaseExtension):
    """This Extension displays the rate at which calls to `publish` are made.
    """
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['rate'])

    def on_validated(self, params):
        rate = params[0]
        self.set_value(str(int(rate)) + ' iters/s')

    def on_invalidated(self, params):
        self.set_value('UNKNOWN')


class Percentage(BaseExtension):
    """This Extension displays percentage of the task completed.
    """
    def __init__(self):
        BaseExtension.__init__(self, requirements = ['percentage'])

    def on_validated(self, params):
        percentage = params[0]
        self.set_value("{:0=2}%".format(int(percentage)))

    def on_invalidated(self, params):
        self.set_value('UNKNOWN')

