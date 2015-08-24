import curses

class Lamp(object):
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

    def create_windows(self, decipher, y, screen_w):
        """Make a row of n center-justified curses windows."""
        screen_mid = screen_w // 2
        total_width = self.n * self.width + (self.n - 1) * self.margin
        left = screen_mid - total_width // 2
        return [
            self._create_window(
                decipher, y, left + i * (self.width + self.margin),
                self.height, self.width, self.color, self.id
        )
            for i in range(self.n)
        ]

    @staticmethod
    def _create_window(decipher, y, x, height, width, color, id):
        if id != LampType.LOG:
            return Lamp(y, x, height, width, color, decipher.get_next() if id != LampType.SECONDS else '')
        return Lamp(y, x, height, width, color, '')


