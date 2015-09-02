class Decipher():
    ciphertext          = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR'
    current_cipher_char = ''
    cipher_index        = 0
    alpha_index         = 0
    keyword_index       = 25

    actual_alphabet = [
        ' ', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
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

    @property
    def length(self):
        """ Get the length of the ciphertext message """
        return len(self.ciphertext) - 1

    @property
    def alphalen(self):
        """ Get the length of the configured alphabet """
        return len(self.actual_alphabet) - 1

    def __init__(self, args):
        self.ciphertext       = args.ciphertext
        self.clock_alphabet   = args.alphabet
        self.keyword_alphabet = self._add_keyword(args.keyword)

    def _add_keyword(self, keyword):
        alphabet = keyword + ''.join([c for c in self.actual_alphabet if c not in keyword and c != ' '])
        return [c for c in alphabet if c != '']

    def get_next(self):
        """ Get the next alphabet character and increment internal pointer """
        c = self.clock_alphabet[self.alpha_index]
        self.alpha_index += 1
        return c

    def get_next_keyword(self):
        """ Gets the next character from the keyword alphabet and increments the internal pointer """
        c = self.keyword_alphabet[self.keyword_index]
        self.keyword_index = self.keyword_index + 1 if self.keyword_index < (len(self.keyword_alphabet) - 1) else 0
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
        return self.keyword_alphabet.index(character) if character != ' ' else 0

    def get_character(self, index):
        """ Get the character at index i """
        index = index if index != 0 else self.alphalen
        return self.actual_alphabet[index]

    def get_index_from_visible_chars(self, visible_chars):
        """ Gets the character represented by the sum of the given list of characters mod self.alphalen """
        index = sum([self.get_index(c) for c in visible_chars]) % self.alphalen
        return index if index != 0 else self.alphalen

    def add(self, character, visible_chars, keyword_char):
        """ gets the sum of c + E[vc] % len where c is a character, vc is a set of visible characters and len is 26 """
        character_index = self.get_index(character)
        visible_index = self.get_index_from_visible_chars(visible_chars)
        visible_index += self.get_keyword_index(keyword_char)
        index = (character_index + visible_index) % self.alphalen
        return self.get_character(index)

    def subtract(self, character, visible_chars, keyword_char):
        """ inverse of add """
        character_index = self.get_index(character)
        visible_index = self.get_index_from_visible_chars(visible_chars)
        visible_index += self.get_keyword_index(keyword_char)
        index = (character_index - visible_index)
        index = index if index > 0 else (self.alphalen + index)
        return self.get_character(index)

