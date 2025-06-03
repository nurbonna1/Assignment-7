class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def getType(self):
        return self.type

    def getValue(self):
        return self.value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class ParseTree:
    def __init__(self, node_type):
        self.node_type = node_type
        self.children = []

    def addChild(self, child):
        self.children.append(child)

    def __repr__(self, level=0):
        ret = "  " * level + f"{self.node_type}\n"
        for child in self.children:
            if isinstance(child, ParseTree):
                ret += child.__repr__(level + 1)
            else:
                ret += "  " * (level + 1) + repr(child) + "\n"
        return ret


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
            return token.getType() == type_
        return token.getType() == type_ and token.getValue() == value

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
        tree.addChild(self.mustBe("keyword", "class"))
        tree.addChild(self.mustBe("identifier"))
        tree.addChild(self.mustBe("symbol", "{"))

        while self.have("keyword", "static") or self.have("keyword", "field"):
            tree.addChild(self.compileClassVarDec())

        while self.have("keyword", "constructor") or self.have("keyword", "function") or self.have("keyword", "method"):
            tree.addChild(self.compileSubroutine())

        tree.addChild(self.mustBe("symbol", "}"))
        return tree

    def compileClassVarDec(self):
        tree = ParseTree("classVarDec")
        tree.addChild(self.mustBe("keyword"))
        tree.addChild(self.mustBe("keyword"))
        tree.addChild(self.mustBe("identifier"))
        while self.have("symbol", ","):
            tree.addChild(self.mustBe("symbol"))
            tree.addChild(self.mustBe("identifier"))
        tree.addChild(self.mustBe("symbol", ";"))
        return tree

    def compileSubroutine(self):
        tree = ParseTree("subroutine")
        tree.addChild(self.mustBe("keyword"))  # constructor/function/method
        tree.addChild(self.mustBe("keyword"))  # return type
        tree.addChild(self.mustBe("identifier"))
        tree.addChild(self.mustBe("symbol", "("))
        tree.addChild(self.compileParameterList())
        tree.addChild(self.mustBe("symbol", ")"))
        tree.addChild(self.compileSubroutineBody())
        return tree

    def compileParameterList(self):
        tree = ParseTree("parameterList")
        if self.have("keyword"):
            tree.addChild(self.mustBe("keyword"))
            tree.addChild(self.mustBe("identifier"))
            while self.have("symbol", ","):
                tree.addChild(self.mustBe("symbol"))
                tree.addChild(self.mustBe("keyword"))
                tree.addChild(self.mustBe("identifier"))
        return tree

    def compileSubroutineBody(self):
        tree = ParseTree("subroutineBody")
        tree.addChild(self.mustBe("symbol", "{"))
        while self.have("keyword", "var"):
            tree.addChild(self.compileVarDec())
        tree.addChild(self.compileStatements())
        tree.addChild(self.mustBe("symbol", "}"))
        return tree

    def compileVarDec(self):
        tree = ParseTree("varDec")
        tree.addChild(self.mustBe("keyword", "var"))
        tree.addChild(self.mustBe("keyword"))
        tree.addChild(self.mustBe("identifier"))
        while self.have("symbol", ","):
            tree.addChild(self.mustBe("symbol"))
            tree.addChild(self.mustBe("identifier"))
        tree.addChild(self.mustBe("symbol", ";"))
        return tree

    def compileStatements(self):
        tree = ParseTree("statements")
        while self.have("keyword"):
            value = self.current().getValue()
            if value == "let":
                tree.addChild(self.compileLet())
            elif value == "do":
                tree.addChild(self.compileDo())
            elif value == "if":
                tree.addChild(self.compileIf())
            elif value == "while":
                tree.addChild(self.compileWhile())
            elif value == "return":
                tree.addChild(self.compileReturn())
            else:
                break
        return tree

    def compileLet(self):
        tree = ParseTree("letStatement")
        tree.addChild(self.mustBe("keyword", "let"))
        tree.addChild(self.mustBe("identifier"))
        tree.addChild(self.mustBe("symbol", "="))
        tree.addChild(self.compileExpression())
        tree.addChild(self.mustBe("symbol", ";"))
        return tree

    def compileDo(self):
        tree = ParseTree("doStatement")
        tree.addChild(self.mustBe("keyword", "do"))
        tree.addChild(self.compileExpression())
        tree.addChild(self.mustBe("symbol", ";"))
        return tree

    def compileReturn(self):
        tree = ParseTree("returnStatement")
        tree.addChild(self.mustBe("keyword", "return"))
        if not self.have("symbol", ";"):
            tree.addChild(self.compileExpression())
        tree.addChild(self.mustBe("symbol", ";"))
        return tree

    def compileIf(self):
        tree = ParseTree("ifStatement")
        tree.addChild(self.mustBe("keyword", "if"))
        tree.addChild(self.mustBe("symbol", "("))
        tree.addChild(self.compileExpression())
        tree.addChild(self.mustBe("symbol", ")"))
        tree.addChild(self.mustBe("symbol", "{"))
        tree.addChild(self.compileStatements())
        tree.addChild(self.mustBe("symbol", "}"))
        if self.have("keyword", "else"):
            tree.addChild(self.mustBe("keyword", "else"))
            tree.addChild(self.mustBe("symbol", "{"))
            tree.addChild(self.compileStatements())
            tree.addChild(self.mustBe("symbol", "}"))
        return tree

    def compileWhile(self):
        tree = ParseTree("whileStatement")
        tree.addChild(self.mustBe("keyword", "while"))
        tree.addChild(self.mustBe("symbol", "("))
        tree.addChild(self.compileExpression())
        tree.addChild(self.mustBe("symbol", ")"))
        tree.addChild(self.mustBe("symbol", "{"))
        tree.addChild(self.compileStatements())
        tree.addChild(self.mustBe("symbol", "}"))
        return tree

    def compileExpression(self):
        tree = ParseTree("expression")
        tree.addChild(self.compileTerm())
        while self.have("symbol", "+") or self.have("symbol", "-"):
            tree.addChild(self.mustBe("symbol"))
            tree.addChild(self.compileTerm())
        return tree

    def compileTerm(self):
        tree = ParseTree("term")
        if self.have("integerConstant"):
            tree.addChild(self.mustBe("integerConstant"))
        elif self.have("identifier"):
            tree.addChild(self.mustBe("identifier"))
        elif self.have("symbol", "("):
            tree.addChild(self.mustBe("symbol", "("))
            tree.addChild(self.compileExpression())
            tree.addChild(self.mustBe("symbol", ")"))
        else:
            raise ParseException("Unexpected token in term")
        return tree



   
