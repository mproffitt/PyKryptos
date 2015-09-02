from argparse import ArgumentParser, Action
from pykryptos.validation import TimeValidator, AlphabetValidator, KeywordValidator
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
            help='An alphabet to use for the clock face (max 23 characters)',
            default=''.join(Decipher.clock_alphabet),
            action=AlphabetValidator
        )

        parser.add_argument(
            '--keyword',
            help='A keyword to use for the second alphabet',
            default='',
            action=KeywordValidator
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

        args            = parser.parse_args()
        args.alphabet   = [c for c in args.alphabet.upper()]
        args.ciphertext = args.ciphertext.upper()
        args.keyword    = args.keyword.upper()
        return args

