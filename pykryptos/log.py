import curses
from pykryptos.time import Decipher
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
        self.index = other.index if other.index > 0 else len(Decipher.ciphertext) + other.index
        return self.__setitem__(0, other.text)

    def __getitem__(self, key):
        return self.lines[key]

    def __setitem__(self, key, value):
        if len(self.lines[-1]) == len(Decipher.ciphertext):
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
        self.window.addstr(1, self.cipher_offset, Decipher.ciphertext[0:self.index-1], self.color)
        self.window.addstr(
            1,
            (self.cipher_offset + self.index-1),
            Decipher.ciphertext[self.index-1:self.index],
            self.highlight
        )
        self.window.addstr(1,
            (self.cipher_offset + self.index),
            Decipher.ciphertext[self.index:],
            self.color
        )
        self.window.addstr(2, 1, ''.join(['-' for i in range(self.width - 2)]))
        for i, item in enumerate(self.lines):
            self.window.addstr((i + 3), 1, str(item))
        self.window.refresh()
        return self


