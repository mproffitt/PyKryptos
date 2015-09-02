from collections import OrderedDict
from argparse import Action
from pykryptos.cipher import Decipher
from datetime import datetime
import re

class AlphabetValidator(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) != len(Decipher.clock_alphabet):
            parser.error(
                'Invalid length for alphabet. Must be ' + str(len(Decipher.clock_alphabet)).zfill(2) + ' characters in length'
            )
        setattr(namespace, self.dest, values.upper())

class TimeValidator(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            if not re.match('\d+:\d+:\d+', values):
                raise AttributeError('Time must be in the format HH:MM:SS')
            time = datetime.strptime(values, '%H:%M:%S')
        except Exception as e:
            raise
            parser.error('Time must be in the format HH:MM:SS')
        setattr(namespace, self.dest, values)

class KeywordValidator(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        subset = ''.join(OrderedDict.fromkeys(values))
        if len(values) != len(subset):
            parser.error('Keyword should not contain duplicate letters')
        setattr(namespace, self.dest, values.upper())
