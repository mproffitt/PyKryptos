import curses
from datetime import datetime, timedelta
from time import sleep
from pykryptos.view import Clock, LogItem, TimeItem
from pykryptos.time import Decipher
from pykryptos.parser import Parser

class Mengenlehreuhr():

    def __init__(self):
        self.args = Parser().parse_args()
        self.time     = datetime.now()
        self.decipher = Decipher(self.args)

    def stop(self):
        self.clock.stop()

    def _update(self, time):
        time_item = TimeItem()
        if time.second % 2 == 0:
            cipher_character = self.decipher.get_next_cipher()
            character = (
                self.decipher.add(cipher_character, self.visible)
                if self.args.method == 'add' else
                    self.decipher.subtract(cipher_character, self.visible)
            )
            time_item.character = cipher_character
            time_item.log = LogItem(
                time,
                character,
                self.decipher.cipher_index
            )

        time_item.time = time

        self.clock.update(time_item)
        self.visible = self.clock.get_visible()

    def run(self):
        """Run the clock until a keyboard interrupt."""
        if self.args.time == 'now':
            self.time = datetime.now()
        else:
            self.time = datetime.strptime(self.args.time, '%H:%M:%S')

        self.clock = Clock(self.time, self.decipher)
        self.visible = self.clock.get_visible()
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
            self.stop()

Mengenlehreuhr().run()
