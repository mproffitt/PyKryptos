class Decipher():
    ciphertext = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR'
    current_cipher_char = ''
    cipher_index = 0

    replacements = [('A', 'E'), ('Q', 'L'), ('U', 'O')]
    alphabet = [
        'W', 'X', 'Y', 'Z',
        'S', 'T', 'U', 'V',
        'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'P', 'Q', 'R',
        'A', 'B', 'C', 'D'
    ]

    alpha_index = 0

    def __init__(self, args):
        self.alphabet     = args.alphabet
        self.replacements = args.replace

    def get_next(self):
        c = self.alphabet[self.alpha_index]
        self.alpha_index += 1
        return c


    def get_next_cipher(self):
        c = self.ciphertext[self.cipher_index]
        self.cipher_index = 0 if self.cipher_index == len(self.ciphertext)-1 else self.cipher_index + 1
        return c

    def get_index(self, character):
        try:
            return self.alphabet.index(character)
        except ValueError:
            for pair in self.replacements:
                if pair[1] == character:
                    return self.get_index(pair[0])

    def get_character(self, index):
        return self.alphabet[index]


