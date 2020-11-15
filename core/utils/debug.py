import functools


def debug(foo):
    @functools.wraps(foo)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {foo.__name__}({signature})")
        value = foo(*args, **kwargs)
        print(f"{foo.__name__!r} returned {value!r}")
        return value
    return wrapper_debug
