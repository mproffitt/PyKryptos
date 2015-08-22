from argparse import ArgumentParser, Action
import curses
from datetime import datetime, timedelta
from time import sleep
import re
from pykryptos.validation import TimeValidator, AlphabetValidator, ReplacementValidator
from pykryptos.log import Log, LogItem
from pykryptos.time import Decipher
from pykryptos.lamps import Lamp, LampType

class Mengenlehreuhr():
    PANEL_TYPES = [
        LampType( # seconds
            id=LampType.SECONDS,
            n=1,
            width=10,
            color=lambda i:2,
            state=lambda i, t: t.second % 2 == 0
        ),
        LampType( # five hours
            id=LampType.FIVE_HOURS,
            n=4,
            width=10,
            color=lambda i:2,
            state=lambda i, t: i < t.hour // 5
        ),
        LampType( # hours
            id=LampType.HOURS,
            n=4,
            width=10,
            color=lambda i:2,
            state=lambda i, t: i < t.hour % 5
        ),
        LampType( # five minutes
            id=LampType.FIVE_MINUTES,
            n=11,
            width=3,
            color=lambda i:2 if i in (2, 5, 8) else 3,
            state=lambda i, t: i < t.minute // 5
        ),
        LampType( # minutes
            id=LampType.MINUTES,
            n=4,
            width=10,
            color=lambda i:3,
            state=lambda i, t: i < t.minute % 5
        )
    ]

    log = None

    def __init__(self):
        self.args = self._parse_args()
        self.string = ''
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.curs_set(0)
        self.time          = datetime.now()
        self.time_decipher = Decipher(self.args)

    def close(self):
        """Restore the screen."""
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def _create_clock_face(self):
        screen_h, screen_w = self.screen.getmaxyx()

        # Try and center the clock on the screen
        y = (screen_h // 2) - (
            (((LampType.DEFAULT_HEIGHT + LampType.DEFAULT_MARGIN) * len(self.PANEL_TYPES)) + Log.DEFAULT_HEIGHT) // 2
        )
        self.lamps = []
        for lamp_type in self.PANEL_TYPES:
            self.lamps.append(lamp_type.create_windows(self.time_decipher, y, screen_w))
            y += lamp_type.height + lamp_type.margin
        self.log = Log(
            x = (screen_w // 2) - (Log.DEFAULT_WIDTH // 2),
            y = y,
            width  = Log.DEFAULT_WIDTH,
            height = Log.DEFAULT_HEIGHT,
            time = self.time
        )

    def _update(self, time):
        visible = []
        character = ''
        for lamp_type, lamp in zip(self.PANEL_TYPES, self.lamps):
            for i, window in enumerate(lamp):
                window.color = lamp_type.color(i)
                window.state = lamp_type.state(i, time)
                current = window.text if window.state and window.text != '' else False
                if lamp_type.id == LampType.SECONDS and time.second % 2 == 0:
                    character = self.time_decipher.get_next_cipher()
                    window.text = character

                if current is not False and not lamp_type.id == LampType.SECONDS:
                    visible.append(current)

        if character != '':
            self._append(character, visible, time)

    def _append(self, character, visible_chars, time):
        length   = len(self.time_decipher.alphabet)
        add_char = sum([self.time_decipher.get_index(c) for c in visible_chars]) % length
        index    = (add_char + self.time_decipher.get_index(character)) % length
        self.log += LogItem(time, self.time_decipher.get_character(index), (self.time_decipher.cipher_index - 1))

    def _parse_args(self):
        parser = ArgumentParser(description='Execute the Berlin Clock')
        parser.add_argument(
            '--time',
            help='Start the clock at the given time',
            default='now',
            action=TimeValidator
        )

        parser.add_argument(
            '--increment',
            help='Increment speed - seconds or minutes',
            choices=['second', 'minute'],
            default='second'
        ),

        parser.add_argument(
            '--speed',
            help='The speed at which to update the clock',
            type=float,
            default=1
        )
        parser.add_argument(
            '--alphabet',
            help='An alternative alphabet to use',
            default=''.join(Decipher.alphabet),
            action=AlphabetValidator
        )

        parser.add_argument(
            '--replace',
            help='A list of characters and their replacements',
            default=','.join([''.join(a) for a in Decipher.replacements]),
            action=ReplacementValidator
        )

        args = parser.parse_args()
        args.alphabet = [c for c in args.alphabet.upper()]
        args.replace  = [(a, b) for a, b in [c for c in args.replace.upper().split(',')]]
        return args


    def run(self):
        """Run the clock until a keyboard interrupt."""
        if self.args.time == 'now':
            self.time = datetime.now()
        else:
            self.time = datetime.strptime(self.args.time, '%H:%M:%S')
        self._create_clock_face()
        try:
            while True:
                if self.args.increment == 'minute':
                    if self.time.second & 0x1:
                        self.time += timedelta(seconds=1)
                    self.time += timedelta(minutes=1)
                else:
                    self.time += timedelta(seconds=1)

                self._update(self.time)
                sleep(self.args.speed)
        except KeyboardInterrupt:
            pass
        finally:
            self.close()

Mengenlehreuhr().run()
