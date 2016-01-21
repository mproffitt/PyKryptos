from __future__ import print_function
import sys

class Coordinate():
    x = 0
    y = 0


class Square():
    cipher_index    = 0
    character_index = 0
    keyword_index   = 0
    visible_index   = 0
    top_left        = None
    bottom_right    = None
    top_right       = None
    bottom_left     = None

class Decipher():
    ciphertext          = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR'
    current_cipher_char = ''
    cipher_index        = 0
    alpha_index         = 0
    keyword_index       = 0
    _keyalphaindex      = 0
    _keyword_alphabet   = []

    _mask_index         = 0
    _mask_keyword_index = 0

    actual_alphabet = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G',
        'H', 'I', 'J', 'K', 'L', 'M', 'N',
        'O', 'P', 'Q', 'R', 'S', 'T', 'U',
        'V', 'W', 'X', 'Y', 'Z'
    ]
    clock_alphabet = [
        'W', 'X', 'Y', 'Z',
        'S', 'T', 'U', 'V',
        'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'P', 'Q', 'R',
        'A', 'B', 'C', 'D'
    ]

    direction = False
    @property
    def length(self):
        """ Get the length of the ciphertext message """
        return len(self.ciphertext) - 1

    @property
    def alphalen(self):
        """ Get the length of the configured alphabet """
        return len(self.actual_alphabet) - 1

    @property
    def clocklen(self):
        """ return the length of the clock alphabet """
        return len(self.clock_alphabet) - 1

    @property
    def kryptos_alphabet(self):
        if self.direction:
            alphabet = self._kryptos_alphabet[self._keyalphaindex:] + self._kryptos_alphabet[:self._keyalphaindex]
        else:
            alphabet = (
                self._kryptos_alphabet[len(self._kryptos_alphabet) - self._keyalphaindex:] +
                self._kryptos_alphabet[:len(self._kryptos_alphabet) - self._keyalphaindex]
            )

        self._keyalphaindex = self._keyalphaindex + 1 if self._keyalphaindex < len(self._kryptos_alphabet) -1 else 0
        return alphabet

    @property
    def keyindex(self):
        return self.keyword_index - 1 if self.keyword_index > 0 else len(self._keyword_alphabet) - 1

    def __init__(self, args):
        self.ciphertext       = args.ciphertext
        self.merge_reverse()
        self.clock_alphabet   = args.alphabet
        self._keyword_alphabet = self._add_keyword(args.keyword)
        self._kryptos_alphabet = self._add_keyword('KRYPTOS')

    def merge_reverse(self):
        merged_cipher = ''
        reverse_cipher = self.ciphertext[::-1]
        for a, b in zip(self.ciphertext, reverse_cipher):
            a_index = self.get_index(a)
            b_index = self.get_index(b)
            new_index = (a_index + b_index) % 26
            merged_cipher += self.get_character(new_index)
        self.ciphertext = merged_cipher

    def get_mask_index(self):
        increment = 3
        mask_index = self._mask_index if self._mask_index % 2 != 0 else self._mask_keyword_index
        self._mask_index = (
            self._mask_index + increment
            if self._mask_index + increment < self.alphalen else (self._mask_index + increment) - self.alphalen
        )
        self._mask_keyword_index = (
            self._mask_keyword_index + increment
            if self._mask_keyword_index + increment < self.alphalen else
                (self._mask_keyword_index + increment) - self.alphalen
        )
        return mask_index

    def mask(self, character):
        index = self.get_index(character)
        mask  = self.get_mask_index()
        index = (index + mask) % self.alphalen
        return self.get_character((self.alphalen + index) if index < 0 else index)

    def _add_keyword(self, keyword):
        alphabet = keyword + ''.join([c for c in self.actual_alphabet if c not in keyword and c != ' '])
        return [c for c in alphabet if c != '']

    def get_next(self):
        """ Get the next alphabet character and increment internal pointer """
        c = self.clock_alphabet[self.alpha_index]
        self.alpha_index += 1
        return c

    def get_prev(self):
        index = self.alpha_index

    def get_next_keyword(self):
        """ Gets the next character from the keyword alphabet and increments the internal pointer """
        c = self._keyword_alphabet[self.keyword_index]
        self.keyword_index = self.keyword_index + 1 if self.keyword_index < (len(self._keyword_alphabet) - 1) else 0
        return c

    def get_next_cipher(self):
        """ Get the next ciphertext character and increment internal pointer """
        c = self.ciphertext[self.cipher_index]
        self.cipher_index = 0 if self.cipher_index == self.length else self.cipher_index + 1
        return c

    def get_index(self, character):
        """ Get the alphabetical index of character c """
        return self.actual_alphabet.index(character)

    def get_keyword_index(self, character):
        """ Get the alphabetical index of the given character from the keyword alphabet """
        return self._keyword_alphabet.index(character) if character != ' ' else 0

    def get_cipher_index(self):
        """ Gets the current cipher index """
        return self.cipher_index - 1

    def get_character(self, index):
        """ Get the character at index i """
        return self.actual_alphabet[index]

    def get_index_from_visible_chars(self, visible_chars):
        """ Gets the character represented by the sum of the given list of characters mod self.alphalen """
        index = sum([self.get_index(c) for c in visible_chars]) % self.clocklen
        return index if index != 0 else self.alphalen

    def add(self, character, visible_chars, keyword_char):
        """ gets the sum of c + E[vc] % len where c is a character, vc is a set of visible characters and len is 26 """
        character_index = self.get_index(character)
        visible_index   = self.get_index_from_visible_chars(visible_chars)
        visible_index  += self.get_keyword_index(keyword_char)
        index = (character_index + visible_index) % self.alphalen
        return self.get_character(index)

    def subtract(self, character, visible_chars, keyword_char):
        """ inverse of add """
        character_index = self.get_index(character)
        visible_index   = self.get_index_from_visible_chars(visible_chars)
        visible_index  += self.get_keyword_index(keyword_char)
        index = (character_index - visible_index)
        index = index if index > 0 else (self.alphalen + index)
        return self.get_character(index)

    def square(self, character, visible_chars, keyword_char):
        """ calculates the vigenere square of the given character """
        modulus = self.alphalen + 1 # the +1 is absolutely important for display on the vigenere grid...
        square = Square()

        # first take the cipher character and add it to the visible chars (mod 26)
        encoded_index = (
            (self.get_index_from_visible_chars(visible_chars) -
            self.get_index(character)) %
            modulus
        )

        # Next get the character at this index from the keyword alphabet
        keyword_index = self.get_keyword_index(
            self._keyword_alphabet[encoded_index]
        )

        # Now look up this index on the standard alphabet
        alpha_index = self.get_index(
            self.actual_alphabet[keyword_index]
        )

        square.cipher_index    = self.get_cipher_index()
        square.character_index = self.get_index(character)
        square.visible_index   = self.get_index_from_visible_chars(visible_chars)
        square.keyword_index   = self.get_keyword_index(keyword_char)

        # Finally plot this on the vigenere grid
        coord = Coordinate()
        """coord.x = (square.cipher_index - alpha_index) % modulus
        y = (modulus - coord.x) + alpha_index
        y = y + modulus if y < 0 else y if y < modulus else y % modulus
        coord.y = y"""
        coord.y = (self.alphalen // 2) #(square.cipher_index - self.get_index(character)) % modulus
        coord.x = (square.cipher_index - square.character_index) % modulus
        square.top_left = coord


        return square

    def ceaser(self, message, shift):
        """ perform rot(n) on message """
        message    = message.upper()
        ciphertext = ''
        for c in message:
            i = ord(c) + shift
            if i > ord('Z'):
                i -= 26
            elif i < ord('A'):
                i = ord('Z') - (ord('A') - i)
            ciphertext += chr(i)
        return ciphertext

    def rotate(self, message, shift):
        """ rotate characters within the message by cutting off the start and pasting on the end """
        rotated_message = [c for i, c in enumerate(message) if i not in range(shift)]
        rotated_message += [c for i, c in enumerate(message) if i in range(shift)]
        return rotated_message

