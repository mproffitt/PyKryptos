from argparse import Action
from pykryptos.time import Decipher
from datetime import datetime
import re

class AlphabetValidator(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(namespace.replace) != 8:
            parser.error(
                'Alphabet is reliant on the replace parameter being set and containing valid replacements'
            )

        if len(values) != len(Decipher.alphabet):
            parser.error(
                'Invalid length for alphabet. Must be ' + str(len(Decipher.alphabet)).zfill(2) + ' characters in length'
            )
        setattr(namespace, self.dest, values)

class ReplacementValidator(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(namespace.alphabet) == 0:
            parser.error('alphabet is required for replacements')
        if not re.match('[A-Z]{2},[A-Z]{2},[A-Z]{2}', values):
            parser.error('replacements must match the format `CR,CR,CR`')

        replacements = [(a, b) for a, b in [c for c in args.replace.upper().split(',')]]
        for replacement in replacements:
            if replacement[0] in namespace.alphabet and replacement[1] not in namespace.alphabet:
                continue
            parser.error('replacements contains invalid values')
        setattr(namespace, self.dest, values)

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


