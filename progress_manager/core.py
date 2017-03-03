import time
from progress_manager.base import BaseExtension, BaseProvider
import sys
from progress_manager.providers import *
sys.setcheckinterval(10)


class ProgressManager:
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
    """
    
    def __init__(self, components, min_value=0, max_value=100,
                 stream=sys.stderr, max_update_interval=0.5):
        import collections
        if not isinstance(components, collections.Iterable):
            raise TypeError("'components' must be iterable")
        self._is_allowed_to_print = True
        self._is_allowed_to_publish = False
        self.clear_on_task_completion = True
        self._stats = dict()
        self.seperator = ' '
        if min_value > max_value:
            raise ValueError("min_value should be less than max_value")
        self.min_value = min_value
        self.max_value = max_value
        self.stream = stream
        self.max_update_interval = max_update_interval
        self._printed_char_num = 0
        self.components = components
        self._registered_providers = dict()
        self._loaded_providers = dict()
        self._register_default_providers()

    def _register_default_providers(self):
        self.register_provider(RateProvider())
        self.register_provider(ETAProvider())
        self.register_provider(ETANewProvider())

    def begin(self):
        """Performs initial tasks prior to printing progress bar.

        It is recommended to perform all customization to the ProgressManager
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
                #params = [self._stats[i] for i in requirements]
                #component._on_begin(params)

        try:
            self._update_interval = min(min(component_update_intervals), self.max_update_interval)
        except TypeError:
            self._update_interval = self.max_update_interval

        #self._load_provider('begin_time')
        #self._load_provider('end_time')
        self._stats['value'] = None
        self._stats['max_value'] = self.max_value
        self._stats['min_value'] = self.min_value
        self._stats['begin_time'] = time.time()
        self._stats['end_time'] = None
        self._stats['iterations'] = 0
        self._stats['percentage'] = 0
        self._stats['time_since_begin'] = 0
        self._stats['deltatime'] = 0

        self._range = self.max_value - self.min_value
        
        self._ordered_providers_tags = self._topological_sort(self._loaded_providers.copy())

        #self._update_stats('begin')
        for tag in self._ordered_providers_tags:
            provider = self._loaded_providers[tag]
            required_tags = provider.get_requirements()
            params = [self._stats[i] for i in required_tags]
            if None not in params:
                provider.on_begin(params)
                #getattr(provider, '_on_{}'.format(event))(params)
                self._stats[tag] = provider.get_value()
            else:
                self._stats[tag] = None
        
        for component in self.components:
            if isinstance(component, BaseExtension):
                requirements = component.get_requirements()
                params = [self._stats[i] for i in requirements]
                component.on_begin(params)

                
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
        self._stats['value'] = self.max_value
        self._stats['max_value'] = self.max_value
        self._stats['min_value'] = self.min_value
        self._stats['end_time'] = time.time()
        self._stats['percentage'] = 100
        self._stats['time_since_begin'] = time.time() - self._stats['begin_time']
        
        #self._update_stats('end')
        for tag in self._ordered_providers_tags:
            provider = self._loaded_providers[tag]
            required_tags = provider.get_requirements()
            params = [self._stats[i] for i in required_tags]
            if None not in params:
                provider.on_end(params)
                #getattr(provider, '_on_{}'.format(event))(params)
                self._stats[tag] = provider.get_value()
            else:
                self._stats[tag] = None
        
        for component in self.components:
            if isinstance(component, BaseExtension):
                requirements = component.get_requirements()
                params = [self._stats[i] for i in requirements]
                component.on_end(params)
        self._update_progress_bar()

        self._loaded_providers = {}

        if self.clear_on_task_completion:
            self._clear_progress_bar()
        self._is_allowed_to_publish = False

    def __next__(self):
        try:
            value = next(self.iterator)
            if self._stats.get('begin_time', None) is None:
                self.begin()
            else:
                self.publish(value)
            return value
        except StopIteration:
            self.end()
            raise

    def __call__(self, iterable):
        self.iterator = iter(iterable)
        self.min_value = 0
        try:
            self.max_value = len(iterable) - 1
        except TypeError:
            import math
            self.max_value = math.inf
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

    def _time_since_last_update(self):
        return (self._stats['time_since_begin']
                - self._stats_at_last_update['time_since_begin'])

    def _is_update_required(self, value)-> bool:

        stats = self._stats
        time_since_update = stats['time_since_update']
        if time_since_update < self.min_update_interval:
            return False
        if time_since_update < self._update_interval:
            try:
                if 100 * (value - stats['value']) / (self.max_value - self.min_value) < 20:
                    return False
            except TypeError:
                return False
        return True

        # Update if time since last update crossed max_update_interval

    def register_provider(self, provider):
        """Any custom providers needed for an extension should be registered
        using this method.

        Parameters
        ----------
        provider : BaseProvider
            An instance of the Custom BaseProvider child class.
        """
        assert isinstance(provider, BaseProvider)
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
        

    def _update_stats(self, event):

        #unordered_providers = list(self._loaded_providers.values())
        #input()
        stats = self._stats
        for tag in self._ordered_providers_tags:
            provider = self._loaded_providers[tag]
            required_tags = provider.get_requirements()
            params = [stats[i] for i in required_tags]
            try:
                provider.on_validated(params)
                #getattr(provider, '_on_{}'.format(event))(params)
                stats[tag] = provider.get_value()
            except TypeError:
                stats[tag] = None

    def publish(self, value=None):
        """Update the progress bar.

        Parameters
        ----------
        value : float or int
            The current progress in percentage. It should be between
            `min_value` and `max_value`.
        """
        #assert self._is_allowed_to_publish is True


        time_curr = time.time()
        stats = self._stats
        stats['iterations'] += 1
        
        time_since_update = time_curr - stats['last_update_time']

        try:
            if ((time_since_update < self._update_interval)
                    and ((value - stats['value']) < (0.1 * self._range))):
                return
        except TypeError:
            pass

        stats['time_since_update'] = time_since_update
        time_ = stats['time_since_begin']
        stats['time_since_begin'] = time_curr - self._stats['begin_time']
        stats['deltatime'] = self._stats['time_since_begin'] - time_

        if value is not None:
            if self.min_value <= value <= self.max_value:
                pass
            else:
                raise ValueError(
                    "'value' must be between {} and {}".format(
                        self.min_value, self.max_value))
        
        stats['value'] = value
        stats['max_value'] = self.max_value
        stats['min_value'] = self.min_value
        try:
            stats['percentage'] = 100 * (value - self.min_value) / (self.max_value - self.min_value)
        except (TypeError, ZeroDivisionError):
            stats['percentage'] = None
        
        for tag in self._ordered_providers_tags:
            provider = self._loaded_providers[tag]
            required_tags = provider.get_requirements()
            params = [stats[i] for i in required_tags]
            try:
                provider.on_validated(params)
                #getattr(provider, '_on_{}'.format(event))(params)
                stats[tag] = provider.get_value()
            except TypeError:
                stats[tag] = None
                

        for component in self.components:
            if isinstance(component, BaseExtension):
                requirements = component.get_requirements()
                params = [stats[i] for i in requirements]
                component.on_update(params)
        
        self._update_progress_bar()
        

    def _update_progress_bar(self):
        """Updates Progress Bar."""
        #self._stats_at_last_update = self._stats.copy()
        self._stats['last_update_time'] = time.time()
        result = []
        for component in self.components:
            if isinstance(component, BaseExtension):
                value = component.get_value()
                if not isinstance(value, str):
                    raise TypeError("{} instance's 'get_value' method returned {}, expected 'str'".format(type(item).__name__, type(item_str)))
                result.append(value)
            elif isinstance(component, str):
                result.append(component)
            else:
                raise ValueError("component was of type {}, expected 'str' or an extension".format(type(item).__name__))

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
        """Clears printed characters by `ProgressManager` instance."""
        self._print_if_allowed(' ' * self._printed_char_num,
                               end='\r',
                               file=self.stream,
                               flush=True)
        self._printed_char_num = 0

    def allow_to_print(self, is_allowed_to_print: bool):
        """Set whether ProgressManager instance is allowed to print to console.

        Parameters
        ----------

        is_allowed_to_print
            Whether ProgressManager instance has permission to print.
        """
        self._is_allowed_to_print = is_allowed_to_print



class SimpleProgressBar(ProgressManager):
    def __init__(self):
        from progress_manager.extensions import Percentage, Timer, ETANew, Rate, Bar
        super().__init__(components = [Percentage(), Bar()])

class AdvancedProgressBar(ProgressManager):
    def __init__(self):
        from progress_manager.extensions import Percentage, Timer, ETA, ETANew, Rate, Bar
        super().__init__(components = [Percentage(), Bar(), Rate(), Timer(), ETA(), ETANew()])

def display_progress(bar):
    def display_progress(func):
        import functools
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bar.begin()
            a = func(*args, **kwargs)
            bar.end()
            return a
        return wrapper
    return display_progress

def main():
    import cProfile, pstats, io
    pr = cProfile.Profile()
    pr.enable()
    
    bar = AdvancedProgressBar()
    bar.begin()
    n = 10000000
    for i in range(n):
        bar.publish((i+1)*100/n)
        pass
    bar.end()

    pr.disable()
    s = io.StringIO()
    sortby = 'time'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

if __name__ == '__main__':
    main()

