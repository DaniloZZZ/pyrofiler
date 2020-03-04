from time import time, sleep
from contextlib import contextmanager
import psutil
from pyrofiler import threaded

@contextmanager
def timing(description: str) -> None:
    start = time()
    yield
    ellapsed_time = time() - start
    print(f"{description}: {ellapsed_time}")

def timed(descr):
    def  decor(f):
        def wrapped(*a,**kw):
            with timing(descr):
                return f(*a, **kw)
        return wrapped
    return decor

def profile_decorator(profiler):
    """ An abstract decorator factory.
        Takes a function `profiler` and returns a decorator,
        which takes a function to profile, `profilee`,
        starts it in separate thread and
        passes `profiler` a generator that iterates
        while the therad with `profilee` is running.
        Last vaulue of the generator will be a return value of `profilee`

        Usage:
            @profile_decorator
            def cpu_load(gen, output_fmt='cpu_vals='):
                cpus = []
                while ret in gen:
                    cpus.append(get_cpu_util())
                print(output_fmt, cpus)
                return ret

        Returns:
            profiler_kwargs -> callable -> wrapped_callable
    """
    def wrapper(**profiler_kw):
        def decorator(profilee):
            def wrap(*args, **kwargs):
                thr_gen = threaded_gen(profilee)
                gen = thr_gen(*args, **kwargs)
                res = profiler(gen, **profiler_kw)
                return res
            return wrap
        return decorator
    return wrapper

@profile_decorator
def proc_count(gen, description='Process max count:'):
    pnames = set()
    res = None
    for res in gen:
        names = [proc.name() for proc in psutil.process_iter()]
        names = {name + str(i) for i, name in enumerate(names) 
                 if 'python' in name}
        pnames = pnames | names
    print(description, len(pnames))
    return res

@profile_decorator
def cpu_util(gen, description='CPU utilisation:'):
    utils = []
    res = None
    for res in gen:
        utils.append(psutil.cpu_percent(interval=0))
    print(description, max(utils))
    return res
