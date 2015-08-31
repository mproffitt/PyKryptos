import sys
from datetime import datetime, timedelta
from time import sleep
from pykryptos.view import Clock, LogItem, TimeItem
from pykryptos.cipher import Decipher
from pykryptos.parser import Parser

class Mengenlehreuhr():
    """
    The Mengenlehreur clock tells the time by utilising Set-Theory

    This version of the clock is used to encipher/decipher messages
    by encoding them using a sum of visible characters on the clock face,
    adding to, or subtracting from (depending on the method used) this
    value to the alphabetical index value of the current  message index.

    Equation:
        c = cipher
        m = message
        a = alphabet

        Add:
        ci = (mi + (E[ai == 1] % 26)) % 26

        Subtract
        ci = (mi - (E[ai == 1] % 26)) > 0 ^ 26 + (mi - (E[ai == 1] % 26))
    """

    def __init__(self):
        self.args     = Parser().parse_args()
        self.time     = datetime.now()
        self.decipher = Decipher(self.args)

    def run(self):
        """Run the clock until a keyboard interrupt."""
        self.time = (
            datetime.now() if self.args.time == 'now' else datetime.strptime(self.args.time, '%H:%M:%S')
        )

        self.clock = self._get_clock(
            self._get_time_item(self.time)
        )
        try:
            while True:
                self._update(self.time)
                if self.args.increment == 'minute':
                    if self.time.second & 0x1:
                        self.time += timedelta(seconds=1)
                    self.time += timedelta(minutes=1)
                else:
                    self.time += timedelta(seconds=1)

                sleep(self.args.speed)
        except KeyboardInterrupt:
            pass
        finally:
            self._stop()

    def _stop(self):
        """ Cleanup and return control to the console """
        self.clock.stop()

    def _update(self, time):
        time_item = self._get_time_item(time)
        if time.second % 2 == 0:
            time_item.character = self.decipher.get_next_cipher()
        self.clock.update(time_item)
        character = (
            self.decipher.add(time_item.character, self.clock.visible)
            if self.args.method == 'add' else
                self.decipher.subtract(time_item.character, self.clock.visible)
        )
        if time.second % 2 == 0:
            self.clock.write(
                LogItem(
                    time,
                    character,
                    self.decipher.cipher_index
                )
            )

    def _get_clock(self, time):
        return Clock(time, self.decipher)

    def _get_decipher(self, args):
        return Decipher(args)

    def _get_time_item(self, time):
        return TimeItem(time=time)
