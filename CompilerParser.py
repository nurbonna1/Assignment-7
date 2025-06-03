class ParseException(Exception):
    pass


class CompilerParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0

    def next(self):
        self.current_index += 1

    def current(self):
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        raise ParseException("Out of tokens")

    def have(self, type_, value=None):
        if self.current_index >= len(self.tokens):
            return False
        token = self.tokens[self.current_index]
        if value is None:
            return token.type == type_
        return token.type == type_ and token.value == value

    def mustBe(self, type_, value=None):
        if not self.have(type_, value):
            raise ParseException(f"Expected {type_} {value}, but got {self.current()}")
        token = self.current()
        self.next()
        return token

    def compileProgram(self):
        if not self.have("keyword", "class"):
            raise ParseException("Program must start with a class")
        return self.compileClass()

    def compileClass(self):
        from ParseTree import ParseTree
        tree = ParseTree("class")
        tree.add_child(self.mustBe("keyword", "class"))
        tree.add_child(self.mustBe("identifier"))
        tree.add_child(self.mustBe("symbol", "{"))

        while self.have("keyword", "static") or self.have("keyword", "field"):
            tree.add_child(self.compileClassVarDec())

        tree.add_child(self.mustBe("symbol", "}"))
        return tree

    def compileClassVarDec(self):
        from ParseTree import ParseTree
        tree = ParseTree("classVarDec")
        tree.add_child(self.mustBe("keyword"))  # static or field
        tree.add_child(self.mustBe("keyword"))  # type
        tree.add_child(self.mustBe("identifier"))  # varName
        tree.add_child(self.mustBe("symbol", ";"))
        return tree
