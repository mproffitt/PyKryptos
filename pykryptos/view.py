import curses
from pykryptos.cipher import Decipher
from pykryptos.lamps import LampType

class TimeItem():
    def __init__(self, character='',log=None,time=None):
        self.character = character
        self.log       = log
        self.time      = time

class LogItem():
    def __init__(self, time, char, index):
        #if len(char) != 1:
        #    raise ValueError('\'char\' must be a single character')
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
    def __init__(self, decipher, y, x, height, width, time):
        self.decipher = decipher
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
        self.index = other.index if other.index > 0 else (self.decipher.length + 1) + other.index
        return self.__setitem__(0, other.text)

    def __getitem__(self, key):
        return self.lines[key]

    def __setitem__(self, key, value):
        if len(self.lines[-1]) == len(self.decipher.ciphertext):
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
        self.window.addstr(1, self.cipher_offset, self.decipher.ciphertext[0:self.index-1], self.color)
        self.window.addstr(
            1,
            (self.cipher_offset + self.index-1),
            self.decipher.ciphertext[self.index-1:self.index],
            self.highlight
        )
        self.window.addstr(1,
            (self.cipher_offset + self.index),
            self.decipher.ciphertext[self.index:],
            self.color
        )
        self.window.addstr(2, 1, ''.join(['-' for i in range(self.width - 2)]))
        for i, item in enumerate(self.lines):
            self.window.addstr((i + 3), 1, str(item))
        self.window.refresh()
        return self

class Clock():
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

    def __init__(self, time, decipher):
        self.time = time.time
        self.decipher = decipher
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
        self._create_clock_face()
        self.current = ''
        self.update(time)

    def _create_clock_face(self):
        screen_h, screen_w = self.screen.getmaxyx()

        # Try and center the clock on the screen
        y = (screen_h // 2) - (
            (((LampType.DEFAULT_HEIGHT + LampType.DEFAULT_MARGIN) * len(self.PANEL_TYPES)) + Log.DEFAULT_HEIGHT) // 2
        )
        self.lamps = []
        for lamp_type in self.PANEL_TYPES:
            self.lamps.append(lamp_type.create_windows(self.decipher, y, screen_w))
            y += lamp_type.height + lamp_type.margin
        self.log = Log(
            self.decipher,
            x = (screen_w // 2) - (Log.DEFAULT_WIDTH // 2),
            y = y,
            width  = Log.DEFAULT_WIDTH,
            height = Log.DEFAULT_HEIGHT,
            time = self.time
        )

    @property
    def visible(self):
        visible = []
        for lamp_type, lamp in zip(self.PANEL_TYPES, self.lamps):
            for i, window in enumerate(lamp):
                current = window.text if window.state else False
                if current is not False and lamp_type.id != LampType.SECONDS:
                    visible.append(current)
        return visible

    def update(self, time_item):
        for lamp_type, lamp in zip(self.PANEL_TYPES, self.lamps):
            for i, window in enumerate(lamp):
                window.color = lamp_type.color(i)
                window.state = lamp_type.state(i, time_item.time)
                if lamp_type.id == LampType.SECONDS:
                    window.update(text = time_item.character)
        return self

    def write(self, log_item):
        self.log += log_item

    def stop(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

