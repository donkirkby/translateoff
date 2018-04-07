import random


class Sentence:
    def __init__(self, text, translation, randrange=None):
        self.text = text
        self.translation = translation
        self.randrange = randrange if randrange else random.randrange
        self.solution = list(text)

    def get_buttons(self):
        shuffled = self.solution[:]
        if len(set(shuffled)) == 1:
            return shuffled
        while True:
            self.shuffle(shuffled)
            if shuffled != self.solution:
                return shuffled

    def shuffle(self, items):
        # Because random module is not available in voc.
        n = len(items)
        for i in range(n - 1):
            j = i + self.randrange(n - i)
            items[i], items[j] = items[j], items[i]

    def is_solved(self, buttons):
        return buttons == self.solution
