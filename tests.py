from progress_manager.core import (SimpleProgressBar, AdvancedProgressBar,
                                   ProgressManager, display_progress)

from progress_manager.extensions import (Percentage, Rate, ETA, ETANew, Bar,
                                         BouncingBar, Ellipses, Timer)

import time
import functools
import shutil

term_width = shutil.get_terminal_size()

print("Calculating bias in time.sleep()...")
st = time.time()
for i in range(1000):
    time.sleep(0.01)
et = time.time()
bias = ((et - st) / 10) - 1
print("bias = {:.2%}\n\n\n".format(bias))


def test(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Running {}...".format(func.__name__))
        start_time = time.time()
        rv = func(*args, **kwargs)
        rv_bias = rv * (1+bias)
        end_time = time.time()
        run_time = end_time - start_time
        print("Sleep time = {:.2f}s\nSleep Time with bias = {:.2f}s\nTotal Runtime = {:.2f}s".format(rv, rv_bias, run_time))
        print("Estimated Overhead = {:.2%}\nEstimated Overhead with bias = {:.2%}\n\n".format((run_time - rv) / rv, (run_time - rv_bias) / rv_bias))
        print("*" * term_width[0])
        return rv
    return wrapper

def generator(n):
    for x in range(n):
        yield x

@test
def test_generator_wrapper(n):
    bar = AdvancedProgressBar()
    for i in bar(generator(n)):
        time.sleep(0.01)
    return n/100

@test
def test_iterator_wrapper(n):
    bar = AdvancedProgressBar()
    for i in bar(range(n)):
        time.sleep(0.01)
    return n/100

bar = AdvancedProgressBar()
@test
@display_progress(bar)
def test_decorator(n):
    for i in range(n):
        time.sleep(0.01)
        bar.publish(100*(i+1)/n)
    return n/100

@test
def test_context_manager(n):
    with AdvancedProgressBar() as bar:
        for i in range(n):
            time.sleep(0.01)
            bar.publish(100*(i+1)/n)
    return n/100

@test
def test_eta(n):
    bar = AdvancedProgressBar()
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

@test
def test_with_print(n):
    bar = AdvancedProgressBar()
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
    'from progress_manager.core import AdvancedProgressBar; [i for i in AdvancedProgressBar()(range(int(1e7)))]']
    import timeit
    for s in stmts:
        print(timeit.timeit(stmt=s, number=1))

def main():
    n = 1000
    test_generator_wrapper(n)
    test_iterator_wrapper(n)
    test_decorator(n)
    test_context_manager(n)
    test_eta(n)
    test_with_print(n)
    #benchmark()

if __name__ == '__main__':
    main()
    
