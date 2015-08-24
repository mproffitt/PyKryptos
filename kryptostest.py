import unittest
import mock
import time
from ddt import data, ddt, unpack

from pykryptos.time import Decipher

class TestArgs():
    replacements = [('A', 'E'), ('Q', 'L'), ('U', 'O')]
    alphabet = [
        'W', 'X', 'Y', 'Z',
        'S', 'T', 'U', 'V',
        'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'P', 'Q', 'R',
        'A', 'B', 'C', 'D'
    ]
    ciphertext = 'HELLOWORLD'

@ddt
class DecipherTest(unittest.TestCase):

    def setUp(self):
        self.decipher = Decipher(TestArgs())

    def tearDown(self):
        pass

    @data(
        ('A', 1),
        ('G', 7),
        ('S', 19),
        ('Y', 25)
    )
    @unpack
    def test_get_index(self, char, expected):
        assert self.decipher.get_index(char) == expected

    @data(
        [['W', 'X', 'S', 'T', 'F','G','H','I','J','K','M','N','P','Q','R','A','B'], 10],
        [['W', 'X','Y', 'S', 'T', 'U', 'F','G','H','I','J','K','M','N','P','Q','R','A','B'],  4],
        [['W', 'S', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'A', 'B', 'C', 'D'], 26]
    )
    @unpack
    def test_get_index_of_visible_chars(self, visible, expected):
        assert self.decipher.get_index_from_visible_chars(visible) == expected

    @data(
        ['H', ['W', 'X', 'S', 'T', 'F','G','H','I','J','K','M','N','P','Q','R','A','B'],         'R'],
        ['E', ['W', 'X', 'S', 'T', 'F','G','H','I','J','K','M','N','P','Q','R','A','B','C'],     'R'],
        ['L', ['W', 'X', 'S', 'T', 'F','G','H','I','J','K','M','N','P','Q','R','A','B','C','D'], 'C'],
        ['L', ['W', 'X', 'S', 'T', 'U'],                                                         'O'],
        ['O', ['W', 'X', 'S', 'T', 'U','A'],                                                     'S'],
        ['W', ['W', 'X', 'S', 'T', 'U','A','B'],                                                 'C'],
        ['O', ['W', 'X', 'S', 'T', 'U','A','B','C'],                                             'X'],
        ['R', ['W', 'X', 'S', 'T', 'U','A','B','C','D'],                                         'E'],
        ['L', ['W', 'X', 'S', 'T', 'U','F'],                                                     'U'],
        ['D', ['W', 'X', 'S', 'T', 'U','F','A'],                                                 'N']
    )
    @unpack
    def test_add_character(self, character, visible, expected):
        assert self.decipher.add(character, visible) == expected

    @data(
        ['R', ['W', 'X', 'S', 'T', 'F','G','H','I','J','K','M','N','P','Q','R','A','B'],         'H'],
        ['R', ['W', 'X', 'S', 'T', 'F','G','H','I','J','K','M','N','P','Q','R','A','B','C'],     'E'],
        ['C', ['W', 'X', 'S', 'T', 'F','G','H','I','J','K','M','N','P','Q','R','A','B','C','D'], 'L'],
        ['O', ['W', 'X', 'S', 'T', 'U'],                                                         'L'],
        ['S', ['W', 'X', 'S', 'T', 'U','A'],                                                     'O'],
        ['C', ['W', 'X', 'S', 'T', 'U','A','B'],                                                 'W'],
        ['X', ['W', 'X', 'S', 'T', 'U','A','B','C'],                                             'O'],
        ['E', ['W', 'X', 'S', 'T', 'U','A','B','C','D'],                                         'R'],
        ['U', ['W', 'X', 'S', 'T', 'U','F'],                                                     'L'],
        ['N', ['W', 'X', 'S', 'T', 'U','F','A'],                                                 'D']
    )
    @unpack
    def test_subtract_character(self, character, visible, expected):
        assert self.decipher.subtract(character, visible) == expected

    def test_get_next_cipher(self):
        for character in [c for c in TestArgs.ciphertext]:
            assert self.decipher.get_next_cipher() == character
