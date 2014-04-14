# simple logging utility .. with colors!

import time

class Logger:
    PURPLE = '\033[95m'    # PURPLE
    BLUE = '\033[94m'     # blue
    GREEN = '\033[92m'        # green
    YELLOW = '\033[93m'   # yellow
    RED = '\033[91m'
    ENDC = '\033[0m'

    def warning(self, msg):
        self._write(self.YELLOW, msg)

    def error(self, msg):
        self._write(self.RED, msg)

    def ok(self, msg):
        self._write(self.GREEN, msg)

    def info(self, msg):
        self._write(self.BLUE, msg)

    def _write(self, ANSI, msg):
        t = time.strftime('%b %d, %Y %X %Z')
        print("%s%s : %s%s" % (ANSI,t,msg,self.ENDC))
