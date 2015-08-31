from argparse import ArgumentParser, Action
from pykryptos.validation import TimeValidator, AlphabetValidator, ReplacementValidator
from pykryptos.cipher import Decipher

class Parser():
    def parse_args(self):
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

        parser.add_argument(
            '--method',
            help='Cipher method used [add|subtract]',
            choices=['add', 'subtract'],
            default='add'
        )

        parser.add_argument(
            '--ciphertext',
            help='Set a custom message (useful for testing)',
            default=Decipher.ciphertext
        )

        args = parser.parse_args()
        args.alphabet = [c for c in args.alphabet.upper()]
        args.replace  = [(a, b) for a, b in [c for c in args.replace.upper().split(',')]]
        args.ciphertext = args.ciphertext.upper()
        return args

