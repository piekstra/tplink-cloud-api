import asyncio
import threading


def asyncio_run(func):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        thread = RunThread(func, (), {})
        thread.start()
        thread.join()
        return thread.result
    else:
        return loop.run_until_complete(func())


# https://stackoverflow.com/a/63072524/17289156
class RunThread(threading.Thread):
    def __init__(self, func, args=(), kwargs={}):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.func(*self.args, **self.kwargs))
