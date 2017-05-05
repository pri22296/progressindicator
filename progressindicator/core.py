from __future__ import print_function
from __future__ import division
import time
import sys
from .base import BaseExtension, BaseProvider
from .tags import *
from .providers import RateProvider, ETAProvider, ETA1Provider


class ProgressIndicator:
    """Utility Class to display Progress Bars in console.

    Parameters
    ----------
    components : array_like
        pass

    min_value : float, optional
        Minimum value of the progress. Default is 0.

    max_value : float, optional
        Maximum value of the progress. Default is 100.

    max_update_interval : float
        Maximum time interval between two updates of the Progress Indicator.
        Default is 0.50s.

    Attributes
    ----------
    clear_on_task_completion : bool
        Whether Progress Bar is cleared on calling `end`.

    min_value : int, float
        Minimum value of the progress.

    max_value : int, float
        Maximum value of the progress

    max_update_interval : float
        Maximum interval in seconds between succesive updates

    seperator : str
        String used to join output of components.(Default ' ')

    components : list
        List of components used to build the progress bar.
    """

    def __init__(self, components, min_value=0, max_value=100,
                 stream=sys.stderr, max_update_interval=0.5):
        import collections
        if not isinstance(components, collections.Iterable):
            raise TypeError("'components' must be iterable")
        self._is_allowed_to_print = True
        self._is_allowed_to_publish = False
        self._stats = dict()
        if min_value > max_value:
            raise ValueError("min_value should be less than max_value")
        self._printed_char_num = 0
        self._registered_providers = dict()
        self._loaded_providers = dict()
        self._iterator = None
        self._range = max_value - min_value
        self._ordered_providers_tags = []
        self._update_interval = max_update_interval

        self.seperator = ' '
        self.min_value = min_value
        self.max_value = max_value
        self.stream = stream
        self.max_update_interval = max_update_interval
        self.clear_on_task_completion = True
        self.components = components

        self._register_default_providers()

    def _register_default_providers(self):
        self.register_provider(RateProvider())
        self.register_provider(ETAProvider())
        self.register_provider(ETA1Provider())

    def _fire_event(self, event):
        for tag in self._ordered_providers_tags:
            provider = self._loaded_providers[tag]
            required_tags = provider.get_requirements()
            params = [self._stats[i] for i in required_tags]
            getattr(provider, event)(params)
            self._stats[tag] = provider.get_value()

        for component in self.components:
            if isinstance(component, BaseExtension):
                requirements = component.get_requirements()
                params = [self._stats[i] for i in requirements]
                getattr(component, event)(params)

    def begin(self):
        """Performs initial tasks prior to printing progress bar.

        It is recommended to perform all customization to the ProgressIndicator
        instance before calling this method. This method should be called for
        initializing Progress Bar. If not called, first call to publish() will
        automatically call this method.
        """
        component_update_intervals = []
        for component in self.components:
            if isinstance(component, BaseExtension):
                requirements = component.get_requirements()
                update_interval = component._get_update_interval()
                if update_interval is not None:
                    component_update_intervals.append(update_interval)
                else:
                    component_update_intervals.append(self.max_update_interval)
                for requirement in requirements:
                    self._load_provider(requirement)

        try:
            self._update_interval = min(min(component_update_intervals), self.max_update_interval)
        except TypeError:
            self._update_interval = self.max_update_interval

        self._stats[TAG_VALUE] = None
        self._stats[TAG_MAX_VALUE] = self.max_value
        self._stats[TAG_MIN_VALUE] = self.min_value
        self._stats[TAG_BEGIN_TIME] = time.time()
        self._stats[TAG_END_TIME] = None
        self._stats[TAG_ITERATIONS] = 0
        self._stats[TAG_PERCENTAGE] = 0
        self._stats[TAG_TIME_SINCE_BEGIN] = 0
        self._stats[TAG_DELTATIME] = 0
        self._stats[TAG_LAST_UPDATED_AT] = None
        self._stats[TAG_TIME_SINCE_UPDATE] = None

        self._range = self.max_value - self.min_value
        self._ordered_providers_tags = self._topological_sort(self._loaded_providers.copy())
        self._fire_event('on_begin')
        self._update_progress_bar()
        self._is_allowed_to_publish = True

    def end(self):
        """Performs clean up tasks after printing Progress Bar.

        This method should always be called after task is complete. This
        method forces the progress Bar to show progress to 100 percent.
        After calling this method publish() can no longer be called. This
        method clears the Progress Bar from the console if
        clear_on_task_completion is True. The console should support
        printing carriage returns.
        """
        self._stats[TAG_VALUE] = self.max_value
        self._stats[TAG_MAX_VALUE] = self.max_value
        self._stats[TAG_MIN_VALUE] = self.min_value
        self._stats[TAG_END_TIME] = time.time()
        self._stats[TAG_PERCENTAGE] = 100
        self._stats[TAG_TIME_SINCE_BEGIN] = time.time() - self._stats[TAG_BEGIN_TIME]

        self._fire_event('on_end')
        self._update_progress_bar()
        self._loaded_providers = {}
        if self.clear_on_task_completion:
            self._clear_progress_bar()
        self._is_allowed_to_publish = False

    def __next__(self):
        try:
            value = next(self._iterator)
            if self._stats.get(TAG_BEGIN_TIME, None) is None:
                self.begin()
            else:
                self.publish(value)
            return value
        except StopIteration:
            self.end()
            raise

    def __call__(self, iterable):
        self._iterator = iter(iterable)
        self.min_value = 0
        try:
            self.max_value = len(iterable) - 1
        except TypeError:
            self.max_value = float('inf')
        return self

    def __iter__(self):
        return self

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()

    def _print_if_allowed(self, *args, **kwargs):
        if self._is_allowed_to_print:
            print(*args, **kwargs)

    def register_provider(self, provider):
        """Any custom providers needed for an extension should be registered
        using this method.

        Parameters
        ----------
        provider : BaseProvider
            An instance of the Custom BaseProvider child class.
        """
        if not isinstance(provider, BaseProvider):
            raise TypeError("provider must be of type BaseProvider, not {}".format(type(provider).__name__))
        tag = provider.get_tag()
        if tag in self._registered_providers:
            raise ValueError("Another provider exists for the tag {}".format(tag))
        self._registered_providers[tag] = provider

    def deregister_provider(self, tag):
        """All providers can be deregistered using this method.

        Parameters
        ----------
        tag : str
            Tag of the Provider you wish to remove.

        Note
        ----
        For optimization purposes, You don't need to deregister providers if
        they are not needed as Providers which are not required are never executed.
        """
        try:
            self._registered_providers.pop(tag)
        except KeyError:
            raise ValueError("No provider exists for the tag {}".format(tag)) from None

    def _load_provider(self, tag):
        if tag not in self._loaded_providers:
            try:
                provider = self._registered_providers[tag]
            except KeyError:
                pass
            else:
                required_tags = provider.get_requirements()
                for required_tag in required_tags:
                    self._load_provider(required_tag)
                self._loaded_providers[tag] = provider
                self._stats[tag] = None

    def _topological_sort(self, data):
        data.update((i, set(data[i].get_requirements())) for i in data)
        ordered_list = []
        from functools import reduce
        try:
            extra_items = reduce(set.union, data.values()) - set(data.keys())
        except TypeError:
            extra_items = set()
        data.update({item:set() for item in extra_items})
        while True:
            ordered = set(item for item, dep in data.items() if not dep)
            if not ordered:
                break
            ordered_providers = [i for i in ordered if i in self._registered_providers]
            ordered_list.extend(ordered_providers)
            data = {item: (dep - ordered)
                    for item, dep in data.items()
                    if item not in ordered}
        if data:
            raise RuntimeError("cyclic dependency detected. dump = {}".format(data))
        else:
            return ordered_list

    def publish(self, value=None):
        """Update the progress bar.

        Parameters
        ----------
        value : float or int
            The current progress in percentage. It should be between
            `min_value` and `max_value`.
        """
        time_curr = time.time()
        stats = self._stats
        stats[TAG_ITERATIONS] += 1

        time_since_update = time_curr - stats[TAG_LAST_UPDATED_AT]

        if time_since_update < self._update_interval:
            try:
                if (value - stats[TAG_VALUE]) < (0.1 * self._range):
                    return
            except TypeError:
                return

        stats[TAG_TIME_SINCE_UPDATE] = time_since_update
        time_ = stats[TAG_TIME_SINCE_BEGIN]
        stats[TAG_TIME_SINCE_BEGIN] = time_curr - self._stats[TAG_BEGIN_TIME]
        stats[TAG_DELTATIME] = self._stats[TAG_TIME_SINCE_BEGIN] - time_

        if value is not None:
            if self.min_value <= value <= self.max_value:
                pass
            else:
                raise ValueError(
                    "'value' must be between {} and {}".format(
                        self.min_value, self.max_value))

        stats[TAG_VALUE] = value
        stats[TAG_MAX_VALUE] = self.max_value
        stats[TAG_MIN_VALUE] = self.min_value
        try:
            stats[TAG_PERCENTAGE] = 100 * (value - self.min_value) / (self.max_value - self.min_value)
        except (TypeError, ZeroDivisionError):
            stats[TAG_PERCENTAGE] = None

        self._fire_event('on_update')
        self._update_progress_bar()

    def _update_progress_bar(self):
        """Updates Progress Bar."""
        self._stats[TAG_LAST_UPDATED_AT] = time.time()
        result = []
        for component in self.components:
            if isinstance(component, BaseExtension):
                value = component.get_value()
                if not isinstance(value, str):
                    raise TypeError("{} instance's 'get_value' method returned {}, expected 'str'".format(type(component).__name__, type(value)))
                result.append(value)
            elif isinstance(component, str):
                result.append(component)
            else:
                raise ValueError("component was of type {}, expected 'str' or an extension".format(type(component).__name__))

        progress_bar = self.seperator.join(result)
        # Overwrite previous printed content
        # This reduces flicker as compared to clearing and then writing.
        self._print_if_allowed(progress_bar, end='', file=self.stream, flush=False)
        bar_length_diff = self._printed_char_num - len(progress_bar)
        # Clear characters which are not overwritten
        if bar_length_diff > 0:
            self._print_if_allowed(' ' * bar_length_diff, end='', file=self.stream, flush=False)
        self._print_if_allowed('\r', end='', file=self.stream, flush=True)
        self._printed_char_num = len(progress_bar)

    def _clear_progress_bar(self):
        """Clears printed characters by `ProgressIndicator` instance."""
        self._print_if_allowed(' ' * self._printed_char_num,
                               end='\r',
                               file=self.stream,
                               flush=True)
        self._printed_char_num = 0

    def allow_to_print(self, is_allowed_to_print: bool):
        """Set whether ProgressIndicator instance is allowed to print to console.

        Parameters
        ----------

        is_allowed_to_print
            Whether ProgressIndicator instance has permission to print.
        """
        self._is_allowed_to_print = is_allowed_to_print


class SimpleProgressBar(ProgressIndicator):
    def __init__(self):
        from .extensions import Percentage, Bar
        super().__init__(components=[Percentage(), Bar()])


class AdvancedProgressBar(ProgressIndicator):
    def __init__(self):
        from .extensions import Percentage, Timer, ETA1, Rate, Bar
        super().__init__(components=[Percentage(), Bar(),
                                     Rate(), "Time:",
                                     Timer(), "ETA:", ETA1()]
                        )


def display_progress(bar):
    def display_progress_func(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bar.begin()
            return_value = func(*args, **kwargs)
            bar.end()
            return return_value
        return wrapper
    return display_progress_func


def main():
    import cProfile, pstats, io
    pr = cProfile.Profile()
    pr.enable()

    bar = AdvancedProgressBar()
    bar.begin()
    n = 10000000
    for i in range(n):
        bar.publish((i+1)*100/n)
    bar.end()

    pr.disable()
    s = io.StringIO()
    sortby = 'time'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

if __name__ == '__main__':
    main()
