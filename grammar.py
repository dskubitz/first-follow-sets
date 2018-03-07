import itertools

"""
Script which calculates the FIRST and FOLLOW sets of a grammar file. 
"""

class Stack:
    def __init__(self):
        self._list = []

    def push(self, item):
        self._list.append(item)

    def top(self):
        return self._list[len(self._list) - 1]

    def pop(self):
        return self._list.pop()

    def empty(self):
        return len(self._list) == 0

    def size(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def clear(self):
        self._list.clear()


class Grammar:
    def __init__(self, filename: str):
        self.terminals = set()
        self.nonterminals = set()
        self.productions = {}
        self.start = '$accept'
        self.accept = '$end'
        self.first = {}
        self.follow = {}
        self.nullable = set()
        self._parse(filename)
        self._compute_first_sets()
        self._compute_follow_sets()

    def _compute_first_sets(self):
        for terminal in self.terminals:
            self.first[terminal] = {terminal}

        for nonterminal in self.nonterminals:
            self.first[nonterminal] = set()
            for production in self.productions[nonterminal]:
                if not production:
                    self.nullable.add(nonterminal)

        while True:
            updated = False
            for A, productions in self.productions.items():
                for rule in productions:
                    old_size = len(self.first[A])
                    old_null_size = len(self.nullable)
                    first_set, nullable = self.calculate_first_set(rule)
                    self.first[A] |= first_set
                    if nullable:
                        self.nullable.add(A)
                    if len(self.first[A]) != old_size:
                        updated = True
                    elif len(self.nullable) != old_null_size:
                        updated = True
            if not updated:
                break

    def _compute_follow_sets(self):
        for nonterminal in self.nonterminals:
            self.follow[nonterminal] = set()
        self.follow[self.start] = {self.accept}

        while True:
            updated = False
            for A, productions in self.productions.items():
                for rule in productions:
                    N = len(rule)
                    for i in range(N):
                        B = rule[i]
                        if B not in self.nonterminals:
                            continue
                        old_size = len(self.follow[B])
                        substr = itertools.islice(rule, i + 1)
                        first_set, nullable = self.calculate_first_set(substr)
                        self.follow[B] |= first_set
                        if nullable or i + 1 == N:
                            self.follow[B] |= self.follow[A]
                        if old_size != len(self.follow[B]):
                            updated = True

            if not updated:
                break

    def calculate_first_set(self, symbols):
        first_set = set()
        nullable = True

        for symbol in symbols:
            first_set |= self.first[symbol]
            if symbol not in self.nullable:
                nullable = False
                break
        return first_set, nullable

    @staticmethod
    def _file_iterator(inputfile: str):
        for line in inputfile:
            for string in line.split():
                yield string

    def _parse(self, filename: str):
        strings = Stack()
        nonterminal = None
        first_symbol = None

        with open(filename) as f:
            stream = Grammar._file_iterator(f)
            for string in stream:
                if string == ':':
                    if first_symbol is None:
                        first_symbol = strings.top()
                    nonterminal = strings.pop()
                    self.nonterminals.add(nonterminal)
                    self.productions[nonterminal] = []
                elif string == '|' or string == ';':
                    self.productions[nonterminal].append(tuple(strings))
                    strings.clear()
                elif string == '/*':
                    while string != '*/':
                        string = next(stream)
                elif string.startswith('\''):
                    strings.push(string.strip('\''))
                else:
                    strings.push(string)

        for productions in self.productions.values():
            for production in productions:
                for symbol in production:
                    if symbol not in self.nonterminals:
                        self.terminals.add(symbol)

        self.nonterminals.add(self.start)
        self.productions[self.start] = [(first_symbol, self.accept)]
        self.terminals.add(self.accept)


if __name__ == '__main__':
    grammar = Grammar('test.txt')
    for nonterminal in grammar.nonterminals:
        print('FIRST({})  = '.format(nonterminal), grammar.first[nonterminal])
    for nonterminal in grammar.nonterminals:
        print('FOLLOW({}) = '.format(nonterminal), grammar.follow[nonterminal])
