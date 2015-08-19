import argparse
import curses
from datetime import datetime, timedelta
from time import sleep

class TimeDecipher():
    ciphertext = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR'
    current_cipher_char = ''
    cipher_index = 0

    replacements = [('A', 'E'), ('Q', 'L'), ('U', 'O')]
    alphabet = [
        'W', 'X', 'Y', 'Z',
        'S', 'T', 'U', 'V',
        'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'P', 'Q', 'R',
        'A', 'B', 'C', 'D'
    ]

    alpha_index = 0

    def __init__(self, args):
        self.alphabet     = args.alphabet
        self.replacements = args.replace

    def get_next(self):
        c = self.alphabet[self.alpha_index]
        self.alpha_index += 1
        return c


    def get_next_cipher(self):
        c = self.ciphertext[self.cipher_index]
        self.cipher_index = 0 if self.cipher_index == len(self.ciphertext)-1 else self.cipher_index + 1
        return c

    def get_index(self, character):
        try:
            return self.alphabet.index(character)
        except ValueError:
            for pair in self.replacements:
                if pair[1] == character:
                    return self.get_index(pair[0])

    def get_character(self, index):
        return self.alphabet[index]

class LogItem():
    def __init__(self, time, char, index):
        if len(char) != 1:
            raise ValueError('\'char\' must be a single character')
        self.time = time
        self.text = char
        self.index = index

class LogLine():
    def __init__(self, time):
        self.time = time
        self.text = ''

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.time.strftime('%H:%M:%S - ') + self.text

    def __repr__(self):
        return self.__str__()

    def strip(self):
        return self.text.strip()


class Log(object):
    DEFAULT_HEIGHT = 14
    DEFAULT_WIDTH  = 110

    lines = []
    def __init__(self, y, x, height, width, time):
        self.y = y
        self.x = x
        self.height    = height
        self.width     = width
        self.color     = curses.color_pair(1)
        self.highlight = curses.color_pair(4)
        self.time      = time
        self.writable_height = self.height - 4
        self.window    = curses.newwin(height, width, y, x)
        self.cipher_offset = 12
        self.window.bkgd(' ', self.color)
        self.window.box()
        self.window.refresh()
        self.lines.append(LogLine(time))

    def __add__(self, other):
        if not isinstance(other, LogItem):
            raise TypeError('Trying to add invalid types \'Log\' and \'' + str(type(other).__name__) + '\'')
        self.time = other.time
        self.index = other.index if other.index > 0 else len(TimeDecipher.ciphertext) + other.index
        return self.__setitem__(0, other.text)

    def __getitem__(self, key):
        return self.lines[key]

    def __setitem__(self, key, value):
        if len(self.lines[-1]) == len(TimeDecipher.ciphertext):
            self._check(self.lines[-1])
            if len(self.lines) == self.writable_height:
                self.lines.pop(0)
            self.lines.append(LogLine(self.time))
        self.lines[-1].text += value
        return self._update()

    def _check(self, line):
        if not 'BERLINCLOCK' in line.text:
            return False

        with open('potential.matches', 'a') as potential_matches:
            potential_matches.write(line.text)
        return True

    def _update(self):
        self.window.erase()
        self.window.box()
        self.window.addstr(1, self.cipher_offset, TimeDecipher.ciphertext[0:self.index-1], self.color)
        self.window.addstr(
            1,
            (self.cipher_offset + self.index-1),
            TimeDecipher.ciphertext[self.index-1:self.index],
            self.highlight
        )
        self.window.addstr(1,
            (self.cipher_offset + self.index),
            TimeDecipher.ciphertext[self.index:],
            self.color
        )
        self.window.addstr(2, 1, ''.join(['-' for i in range(self.width - 2)]))
        for i, item in enumerate(self.lines):
            self.window.addstr((i + 3), 1, str(item))
        self.window.refresh()
        return self

class Lamp(object):
    y = 1
    #_state = True
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        self.update()

    def __init__(self, y, x, height, width, color, character):
        self.color     = color
        self.text      = character
        self.window    = curses.newwin(height, width, y, x)
        self.window.box()
        self.window.refresh()
        self.state     = False

    def update(self, y = 0, text = '', center=True):
        h, w = self.window.getmaxyx()
        if text != '':
            self.text = text
        self.window.bkgd(' ', curses.color_pair(self.color if self.state else 1))
        self.window.addstr(
            1 if y == 0 else y,
            w // 2 if center else 1,
            str(self.text) if self.state else ' '
        )
        self.window.refresh()

class LampType():
    DEFAULT_HEIGHT = 4
    DEFAULT_MARGIN = 1

    SECONDS      = 0
    FIVE_HOURS   = 1
    HOURS        = 2
    FIVE_MINUTES = 3
    MINUTES      = 4
    LOG          = 5

    def __init__(self, id, n, width, height=DEFAULT_HEIGHT, margin=DEFAULT_MARGIN, color=2, state=lambda i, t: 0):
        self.id     = id
        self.n      = n
        self.height = height
        self.width  = width
        self.margin = margin
        self.color  = color
        self.state  = state

    def create_windows(self,tc,  y, screen_w):
        """Make a row of n center-justified curses windows."""
        screen_mid = screen_w // 2
        total_width = self.n * self.width + (self.n - 1) * self.margin
        left = screen_mid - total_width // 2
        return [
            self._create_window(
                tc, y, left + i * (self.width + self.margin),
                self.height, self.width, self.color, self.id
        )
            for i in range(self.n)
        ]

    @staticmethod
    def _create_window(tc, y, x, height, width, color, id):
        if id != LampType.LOG:
            return Lamp(y, x, height, width, color, tc.get_next() if id != LampType.SECONDS else tc.get_next_cipher())
        return Lamp(y, x, height, width, color, '')

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
        self.time_decipher = TimeDecipher(self.args)

    def close(self):
        """Restore the screen."""
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def _create_clock_face(self):
        screen_h, screen_w = self.screen.getmaxyx()

        # Try and center the clock on the screen
        y = (screen_h // 2) - ((((LampType.DEFAULT_HEIGHT + LampType.DEFAULT_MARGIN) * len(self.PANEL_TYPES)) + Log.DEFAULT_HEIGHT) // 2)
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
        parser = argparse.ArgumentParser(description='Execute the Berlin Clock')
        parser.add_argument(
            '--time',
            help='Start the clock at the given time',
            default='now'
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
            default=''.join(TimeDecipher.alphabet)
        )

        parser.add_argument(
            '--replace',
            help='A list of characters and their replacements',
            default=','.join([''.join(a) for a in TimeDecipher.replacements])
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
