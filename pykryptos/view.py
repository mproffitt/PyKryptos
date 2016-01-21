from __future__ import print_function
import sys
import curses
from pykryptos.cipher import Decipher
from pykryptos.lamps import LampType
from time import sleep

class TimeItem():
    def __init__(self, character=' ',log=None,time=None, keyword_character=' ', visible = []):
        self.character         = character
        self.keyword_character = keyword_character
        self.log               = log
        self.time              = time
        self.visible           = visible

class LogItem():
    def __init__(self, time, char, index):
        self.time  = time
        self.text  = char
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
        self.decipher        = decipher
        self.y               = y
        self.x               = x
        self.height          = height
        self.width           = width
        self.color           = curses.color_pair(1)
        self.highlight       = curses.color_pair(4)
        self.time            = time
        self.window          = curses.newwin(height, width, y, x)
        self.cipher_offset   = 12
        self.writable_height = self.height - 4

        self.window.bkgd(' ', self.color)
        self.window.box()
        self.window.refresh()
        self.lines.append(LogLine(time))

    def __add__(self, other):
        if not isinstance(other, LogItem):
            raise TypeError('Trying to add invalid types \'Log\' and \'' + str(type(other).__name__) + '\'')
        self.time  = other.time
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


class VigenereGrid():
    DEFAULT_HEIGHT = 28
    DEFAULT_WIDTH  = 53
    window         = None
    decipher       = None

    def __init__(self, decipher, y, x):
        self.decipher        = decipher
        self.color           = curses.color_pair(1)
        self.highlight       = curses.color_pair(4)
        self.window          = curses.newwin(self.DEFAULT_HEIGHT, self.DEFAULT_WIDTH, y, x)
        self.writable_height = self.DEFAULT_HEIGHT - 4

    def update(self, coordinates):
        self.window.bkgd(' ', self.color)
        self.write_grid(coordinates)
        self.window.box()
        self.window.refresh()

    def write_grid(self, coordinates):
        x = coordinates.top_left.x
        y = coordinates.top_left.y
        color     = self.color
        highlight = self.highlight

        alphabet = self.decipher.kryptos_alphabet
        for i in range (len(alphabet)):
            message = self.decipher.rotate(''.join(alphabet), i)
            color     = self.color     if i != self.decipher.keyindex and i != x else curses.color_pair(15) if i == x else curses.color_pair(17)
            highlight = self.highlight if i != self.decipher.keyindex and i != x else curses.color_pair(16) if i == x else curses.color_pair(18)

            if i == x:
                self.window.addstr(
                    (i + 1), 1, ' '.join(message[:y]),
                    color
                )
                self.window.addstr(
                    (i + 1), (y * 2) + 1, ' '.join(message[y:y+1]),
                    highlight
                )
                if y <= (len(message) - 2):
                    self.window.addstr(
                        (i + 1), (y * 2) + 3, ' '.join(message[y+1:]),
                        color
                    )
            else:
                self.window.addstr(
                    (i + 1), 1, ' '.join(message[:y]),
                    color
                )
                self.window.addstr(
                    (i + 1), (y * 2) + 1, ' '.join(message[y:y+1]),
                    curses.color_pair(15 if i != x else 16)
                )
                if y <= (len(message) - 2):
                    self.window.addstr(
                        (i + 1), (y * 2) + 3, ' '.join(message[y+1:]),
                        color
                    )

class Clock():
    PANEL_TYPES = [
        LampType(
            id=LampType.SECONDS,
            n=1,
            width=10,
            color=lambda i:2,
            state=lambda i, t: t.second % 2 == 0
        ),
        LampType(
            id=LampType.KEYWORD_TICKER,
            n=1,
            width=21,
            height=3,
            color=lambda i:1,
            state=lambda i, t: True
        ),
        LampType(
            id=LampType.FIVE_HOURS,
            n=4,
            width=10,
            color=lambda i:2,
            state=lambda i, t: i < t.hour // 5
        ),
        LampType(
            id=LampType.HOURS,
            n=4,
            width=10,
            color=lambda i:2,
            state=lambda i, t: i < t.hour % 5
        ),
        LampType(
            id=LampType.FIVE_MINUTES,
            n=11,
            width=3,
            color=lambda i:2 if i in (2, 5, 8) else 3,
            state=lambda i, t: i < t.minute // 5
        ),
        LampType(
            id=LampType.MINUTES,
            n=4,
            width=10,
            color=lambda i:3,
            state=lambda i, t: i < t.minute % 5
        )
    ]
    log           = None
    vigenere_grid = None

    def __init__(self, time, decipher):
        self.time     = time.time
        self.decipher = decipher
        self.screen   = curses.initscr()
        self.current  = ''
        color         = 237

        curses.noecho()
        curses.cbreak()
        self.screen.nodelay(True)
        self.screen.keypad(1)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        curses.init_pair(4, curses.COLOR_RED,   -1)
        curses.init_pair(5, 254,                -1)
        for i in range (6, 14):
            curses.init_pair(i, color, -1)
            color += 1
        curses.init_pair(15, curses.COLOR_BLACK, 77)
        curses.init_pair(16, curses.COLOR_RED,   77)
        curses.init_pair(17, curses.COLOR_BLACK, 179)
        curses.init_pair(18, curses.COLOR_RED,   179)

        curses.curs_set(0)
        self._create_clock_face()

    def _create_clock_face(self):
        screen_h, screen_w = self.screen.getmaxyx()

        print('screen_w = ' + str(screen_w), file=sys.stderr)
        vigenere_y = (screen_h // 2) - ((VigenereGrid.DEFAULT_HEIGHT + Log.DEFAULT_HEIGHT) // 2) - 1
        vigenere_x = ((screen_w // 2) - (VigenereGrid.DEFAULT_WIDTH // 2)) + 25

        # Try and center the clock on the screen
        y = (screen_h // 2) - (
            (((LampType.DEFAULT_HEIGHT + LampType.DEFAULT_MARGIN) * len(self.PANEL_TYPES)) + Log.DEFAULT_HEIGHT) // 2
        )

        self.lamps = []
        for lamp_type in self.PANEL_TYPES:
            self.lamps.append(lamp_type.create_windows(self.decipher, y, (screen_w - VigenereGrid.DEFAULT_WIDTH)))
            y += lamp_type.height + lamp_type.margin

        self.log = Log(
            self.decipher,
            x = (screen_w // 2) - (Log.DEFAULT_WIDTH // 2),
            y = y,
            width  = Log.DEFAULT_WIDTH,
            height = Log.DEFAULT_HEIGHT,
            time   = self.time
        )

        self.vigenere_grid = VigenereGrid(
            self.decipher,
            vigenere_y,
            vigenere_x
        )
        self.screen.addstr(
            (y + Log.DEFAULT_HEIGHT),
            (screen_w // 2) - (Log.DEFAULT_WIDTH // 2) + 1,
            'Help: \'p\' pause clock. \'c\' continue clock. \'q\' quit',
            curses.color_pair(1)
        )
        self.screen.refresh()
        self.y = (y + Log.DEFAULT_HEIGHT)

    def pause_or_quit(self, key):
        screen_h, screen_w = self.screen.getmaxyx()
        """ enable pausing of the application """
        if key == 'q':
            raise KeyboardInterrupt()
        if key == 'p':
            self.screen.addstr(
                self.y,
                (screen_w // 2) + (Log.DEFAULT_WIDTH // 2) - 11,
                '= PAUSED =',
                curses.color_pair(1)
            )
            self.screen.refresh()
            while True:
                try:
                    key = self.screen.getkey()
                    if key == 'c':
                        self.screen.addstr(
                            self.y,
                            (screen_w // 2) + (Log.DEFAULT_WIDTH // 2) - 11,
                            '          ',
                            curses.color_pair(1)
                        )
                        self.screen.refresh()
                        return
                    elif key == 'b':
                        self.decipher.get_prev()
                        pass
                    elif key == 'n':
                        self.decipher.get_next()
                        pass
                except:
                    sleep(0.5)


    def _get_ticker_text(self, window):
        alphabet      = self.decipher._keyword_alphabet
        slice_size    = 8
        index         = (
            self.decipher.keyword_index - 1 if self.decipher.keyword_index > 0 else
                len(self.decipher._keyword_alphabet) - 1
        )
        keyword_char  = alphabet[index]
        keyword_slice_after  = []
        keyword_slice_before = []

        keyword_slice_before = alphabet[(index - slice_size):index]
        if index <= slice_size:
            keyword_slice_before = alphabet[:index]

        if len(keyword_slice_before) <= slice_size:
            keyword_slice_before = alphabet[((len(alphabet) - (slice_size - index))):] + keyword_slice_before

        keyword_slice_after = alphabet[(index + 1):((index + 1) + slice_size)]
        if index >= ((len(alphabet) - 1) - slice_size):
            keyword_slice_after = alphabet[(index + 1):]

        if index >= ((len(alphabet) - 1) - slice_size):
            keyword_slice_after = keyword_slice_after + alphabet[:(
                slice_size - (len(alphabet) - 1 - index)
            )]

        window.ticker_update(keyword_slice_before, keyword_char, keyword_slice_after)

    @property
    def visible(self):
        visible = []
        for lamp_type, lamp in zip(self.PANEL_TYPES, self.lamps):
            for i, window in enumerate(lamp):
                current = window.text if window.state else False
                if current is not False and lamp_type.id not in [LampType.SECONDS, LampType.KEYWORD_TICKER]:
                    visible.append(current)
        return visible

    def update(self, time_item):
        for lamp_type, lamp in zip(self.PANEL_TYPES, self.lamps):
            for i, window in enumerate(lamp):
                window.color = lamp_type.color(i)
                window.state = lamp_type.state(i, time_item.time)
                if lamp_type.id == LampType.SECONDS:
                    window.update(text = time_item.character)
                if lamp_type.id == LampType.KEYWORD_TICKER:
                    self._get_ticker_text(window)
        if time_item.character != ' ':
            self.vigenere_grid.update(
                self.decipher.square(
                    time_item.character,
                    time_item.visible,
                    time_item.keyword_character
                )
            )
        return self

    def write(self, log_item):
        self.log += log_item

    def stop(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

