import os
import re
from importlib import import_module

from dmoj.judgeenv import env, only_executors, exclude_executors

_reexecutor = re.compile('([A-Z0-9]+)\.py$')

# List of executors that exist for historical purposes, but which shouldn't ever be run on a normal system
# We keep them for compatibility purposes, but they are not important enough to have a commandline flag for enabling
# them; instead, removing them from this list suffices.
_unsupported_executors = ['CPP0X']

executors = {}


def load_executors():
    __executors = set(i.group(1) for i in map(_reexecutor.match,
                                              os.listdir(os.path.dirname(__file__)))
                      if i is not None)

    if only_executors:
        __executors &= only_executors
    if exclude_executors:
        __executors -= exclude_executors
    __executors = sorted(__executors)

    import traceback

    def __load_module(executor):
        try:
            module = import_module('%s.%s' % (__name__, executor))
        except ImportError as e:
            if e.message not in ('No module named _cptbox',
                                 'No module named msvcrt',
                                 'No module named _wbox',
                                 'No module named termios'):
                traceback.print_exc()
            return None
        return module

    print 'Self-testing executors...'

    for name in __executors:
        if name in _unsupported_executors:
            continue
        executor = __load_module(name)
        if executor is None:
            continue
        if hasattr(executor, 'initialize') and not executor.initialize(sandbox=env.get('selftest_sandboxing', True)):
            continue
        if hasattr(executor, 'aliases'):
            for alias in executor.aliases():
                executors[alias] = executor
        else:
            executors[name] = executor

    print
