from collections.abc import Callable


def run_inline(task: Callable, *args, **kwargs):
    return task(*args, **kwargs)

