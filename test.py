from progressindicator.core import (SimpleProgressBar, ProgressIndicator,
                                    display_progress)
from progressindicator.extensions import (Percentage, Rate, ETA, ETA1, Bar,
                                          BouncingBar, Timer, Spinner, Loader)
from progressindicator.base import BaseExtension
from progressindicator.tags import *

import time
import functools
import sys

if sys.version_info[:2] >= (3,3):
    import shutil
    term_width = shutil.get_terminal_size()[0]
else:
    term_width = 80

def test(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Running {}...".format(func.__name__))
        start_time = time.time()
        rv = func(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - start_time
        print("\nSleep time = {:.2f}s\nTotal Runtime = {:.2f}s".format(rv, run_time))
        print("Estimated Overhead = {:.2%}\n\n".format((run_time - rv)/ rv))
        print("*" * term_width)
        return rv
    return wrapper

def generator(n):
    for x in range(n):
        yield x

@test
def test_generator_wrapper(n):
    bar = SimpleProgressBar()
    for _ in bar(generator(n)):
        time.sleep(0.01)
    return n/100

@test
def test_iterator_wrapper(n):
    bar = SimpleProgressBar()
    for _ in bar(range(n)):
        time.sleep(0.01)
    return n/100

bar = SimpleProgressBar()
@test
@display_progress(bar)
def test_decorator(n):
    for i in range(n):
        time.sleep(0.01)
        bar.publish(100*(i+1)/n)
    return n/100

@test
def test_context_manager(n):
    with SimpleProgressBar() as bar:
        for i in range(n):
            time.sleep(0.01)
            bar.publish(100*(i+1)/n)
    return n/100

# Use this to test situations when progress is determinate and rate of
# progress is constant
def extension_test_helper_determinate_type1(bar, n):
    bar.begin()
    for i in range(n):
        bar.publish(100*(i+1)/n)
        time.sleep(0.01)
    bar.end()
    return n/100

# Use this to test situations when progress is determinate but rate of
# progress fluctuates.
def extension_test_helper_determinate_type2(bar, n):
    bar.begin()
    for i in range(n):
        if i < n/10:
            time.sleep(0.02)
        elif i > 8*n/10:
            time.sleep(0.1)
        else:
            time.sleep(0.01)
        bar.publish(100*(i + 1)/n)
    bar.end()
    return ((n/10) * 0.02) + ((7*n/10) * 0.01) + ((n/5) * 0.1)

# Use this to test situations when current progress is indeterminate but
# rate of progress is constant.
def extension_test_helper_indeterminate_type1(bar, n):
    bar.begin()
    for _ in range(n):
        bar.publish()
        time.sleep(0.01)
    bar.end()
    return n/100

# Use this to test situations when current progress is indeterminate and
# rate of progress fluctuates.
def extension_test_helper_indeterminate_type2(bar, n):
    bar.begin()
    for i in range(n):
        if i < n/10:
            time.sleep(0.02)
        elif i > 8*n/10:
            time.sleep(0.1)
        else:
            time.sleep(0.01)
        bar.publish()
    bar.end()
    return ((n/10) * 0.02) + ((7*n/10) * 0.01) + ((n/5) * 0.1)

@test
def test_myextension(n):
    bar = ProgressIndicator(components=[Percentage(), MyExtension()])
    return extension_test_helper_determinate_type1(bar, n)

@test
def test_extension_eta(n):
    bar = ProgressIndicator(components=[ETA()])
    return extension_test_helper_determinate_type2(bar, n)

@test
def test_extension_eta1(n):
    bar = ProgressIndicator(components=[ETA1()])
    return extension_test_helper_determinate_type2(bar, n)

@test
def test_extension_spinner(n):
    bar = ProgressIndicator(components=[Spinner()])
    return extension_test_helper_indeterminate_type1(bar, n)

@test
def test_extension_loader(n):
    bar = ProgressIndicator(components=[Loader()])
    return extension_test_helper_indeterminate_type1(bar, n)

@test
def test_extension_timer(n):
    bar = ProgressIndicator(components=[Timer()])
    return extension_test_helper_indeterminate_type1(bar, n)

@test
def test_extension_bar(n):
    bar = ProgressIndicator(components=[Bar()])
    return extension_test_helper_determinate_type1(bar, n)

@test
def test_extension_bouncing_bar(n):
    bar = ProgressIndicator(components=[BouncingBar()])
    return extension_test_helper_indeterminate_type1(bar, n)

@test
def test_extension_rate(n):
    bar = ProgressIndicator(components=[Rate()])
    return extension_test_helper_indeterminate_type2(bar, n)

@test
def test_extension_percentage(n):
    bar = ProgressIndicator(components=[Percentage()])
    return extension_test_helper_determinate_type1(bar, n)

@test
def test_with_print(n):
    bar = SimpleProgressBar()
    bar.begin()
    for i in range(n):
        bar.publish(100*(i+1)/n)
        time.sleep(0.01)
        if n/2<=i<=n/2+n/200:
            print(i)
    bar.end()
    return n/100

def benchmark():
    stmts = ['[i for i in range(int(1e7))]',
    'from progressindicator.core import SimpleProgressBar; [i for i in SimpleProgressBar()(range(int(1e7)))]']
    import timeit
    for s in stmts:
        print(timeit.timeit(stmt=s, number=1))


class MyExtension(BaseExtension):
   def __init__(self):
       BaseExtension.__init__(self, requirements=[TAG_PERCENTAGE])

   def on_begin(self, params):
       self.set_value("Task has begun")

   def on_validated(self, params):
       if params[0] > 50 and params[0] < 90:
           self.set_value("Task is half completed")
       elif params[0] > 90:
           self.set_value("Task is almost completed")

   def on_end(self, params):
       self.set_value("Task is finished")

def main():
    n = 100
    # Testing various use cases
    test_generator_wrapper(n)
    test_iterator_wrapper(n)
    test_decorator(n)
    test_context_manager(n)
    test_with_print(n)

    # Testing extensions
    test_extension_eta(n)
    test_extension_eta1(n)
    test_myextension(n)
    test_extension_spinner(n)
    test_extension_loader(n)
    test_extension_timer(n)
    test_extension_bar(n)
    test_extension_bouncing_bar(n)
    test_extension_rate(n)
    test_extension_percentage(n)
    #benchmark()

if __name__ == '__main__':
    main()

