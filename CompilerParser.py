
class Token:
    def _init_(self, type_, value):
        self.type = type_
        self.value = value

    def _repr_(self):
        return f"Token({self.type}, {self.value})"


class ParseTree:
    def _init_(self, node_type):
        self.node_type = node_type
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def _repr_(self, level=0):
        ret = "  " * level + f"{self.node_type}\n"
        for child in self.children:
            if isinstance(child, ParseTree):
                ret += child._repr_(level + 1)
            else:
                ret += "  " * (level + 1) + repr(child) + "\n"
        return ret


class ParseException(Exception):
    pass


class CompilerParser:
    def _init_(self, tokens):
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
        tree = ParseTree("class")
        tree.add_child(self.mustBe("keyword", "class"))
        tree.add_child(self.mustBe("identifier"))
        tree.add_child(self.mustBe("symbol", "{"))

        while self.have("keyword", "static") or self.have("keyword", "field"):
            tree.add_child(self.compileClassVarDec())

        tree.add_child(self.mustBe("symbol", "}"))
        return tree

    def compileClassVarDec(self):
        tree = ParseTree("classVarDec")
        tree.add_child(self.mustBe("keyword"))  # static or field
        tree.add_child(self.mustBe("keyword"))  # type
        tree.add_child(self.mustBe("identifier"))  # varName
        tree.add_child(self.mustBe("symbol", ";"))
        return tree

    def compileStatements(self):
        tree = ParseTree("statements")
        while self.have("keyword"):
            value = self.current().value
            if value == "let":
                tree.add_child(self.compileLet())
            elif value == "do":
                tree.add_child(self.compileDo())
            elif value == "if":
                tree.add_child(self.compileIf())
            elif value == "while":
                tree.add_child(self.compileWhile())
            elif value == "return":
                tree.add_child(self.compileReturn())
            else:
                break
        return tree

    def compileLet(self):
        tree = ParseTree("letStatement")
        tree.add_child(self.mustBe("keyword", "let"))
        tree.add_child(self.mustBe("identifier"))
        tree.add_child(self.mustBe("symbol", "="))
        tree.add_child(self.compileExpression())
        tree.add_child(self.mustBe("symbol", ";"))
        return tree

    def compileDo(self):
        tree = ParseTree("doStatement")
        tree.add_child(self.mustBe("keyword", "do"))
        tree.add_child(self.compileExpression())
        tree.add_child(self.mustBe("symbol", ";"))
        return tree

    def compileReturn(self):
        tree = ParseTree("returnStatement")
        tree.add_child(self.mustBe("keyword", "return"))
        if self.have("keyword", "skip"):  # allow empty return
            tree.add_child(self.compileExpression())
        tree.add_child(self.mustBe("symbol", ";"))
        return tree

    def compileIf(self):
        tree = ParseTree("ifStatement")
        tree.add_child(self.mustBe("keyword", "if"))
        tree.add_child(self.mustBe("symbol", "("))
        tree.add_child(self.compileExpression())
        tree.add_child(self.mustBe("symbol", ")"))
        tree.add_child(self.mustBe("symbol", "{"))
        tree.add_child(self.compileStatements())
        tree.add_child(self.mustBe("symbol", "}"))
        if self.have("keyword", "else"):
            tree.add_child(self.mustBe("keyword", "else"))
            tree.add_child(self.mustBe("symbol", "{"))
            tree.add_child(self.compileStatements())
            tree.add_child(self.mustBe("symbol", "}"))
        return tree

    def compileWhile(self):
        tree = ParseTree("whileStatement")
        tree.add_child(self.mustBe("keyword", "while"))
        tree.add_child(self.mustBe("symbol", "("))
        tree.add_child(self.compileExpression())
        tree.add_child(self.mustBe("symbol", ")"))
        tree.add_child(self.mustBe("symbol", "{"))
        tree.add_child(self.compileStatements())
        tree.add_child(self.mustBe("symbol", "}"))
        return tree

    def compileExpression(self):
        tree = ParseTree("expression")
        tree.add_child(self.mustBe("keyword", "skip"))
        return tree
