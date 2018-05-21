import random


class Sentence:
    def __init__(self, text, translation, randrange=None, state=None):
        self.text = text
        self.translation = translation
        self.randrange = randrange if randrange else random.randrange
        self.solution = list(text)
        self.selected = [' '] * len(text)
        self.selected_indices = []
        self.hint_size = 0
        if state is not None:
            lines = state.splitlines()
            self.source = list(lines[0])
            if len(lines) > 1:
                to_select = list(lines[1])
                while to_select:
                    c = to_select.pop(0)
                    i = self.source.index(c)
                    self.select(i)
        else:
            self.source = self.solution[:]
            if len(set(self.source)) > 1:
                while True:
                    self.shuffle(self.source)
                    if self.source != self.solution:
                        break
        self.is_solved = False
        self.check_solution()

    def shuffle(self, items):
        # Because random module is not available in voc.
        n = len(items)
        for i in range(n - 1):
            j = i + self.randrange(n - i)
            items[i], items[j] = items[j], items[i]

    def select(self, i):
        target = len(self.selected_indices)
        self.selected[target] = self.source[i]
        self.selected_indices.append(i)
        self.source[i] = ' '
        self.check_solution()

    def replace(self, i):
        index = self.selected_indices.pop(i)
        self.source[index] = self.selected[i]
        self.selected.pop(i)
        self.selected.append(' ')

    def check_solution(self):
        self.is_solved = self.selected == self.solution

    def get_hint(self):
        i = 0
        for i, (goal, button) in enumerate(zip(self.solution, self.selected)):
            if goal != button:
                break
        while self.selected[i] != ' ':
            self.replace(i)
        c = self.solution[i]
        self.select(self.source.index(c))
        self.hint_size = i + 1
        return self.solution[:self.hint_size]
