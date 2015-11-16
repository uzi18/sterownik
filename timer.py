import threading

class RTimer(object):
    def __init__(self, function):
        self._timer     = None
        self.interval   = None
        self.function   = function
        self.is_running = False
        self.auto_stop  = False

    def _run(self):
        self.is_running = False
        if not self.auto_stop:
           self.start()
        self.function()

    def start(self):
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def startInterval(self, interval):
        self.interval = interval
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
