class ParseTree:
    def __init__(self, node_type):
        self.type = node_type
        self.value = node_type
        self.children = []

    def addChild(self, child):  # ✅ Required method name
        self.children.append(child)

    def getType(self):          # ✅ Required
        return self.type

    def getValue(self):         # ✅ Required
        return self.value

    def __repr__(self, level=0):
        ret = "  " * level + f"{self.value}\\n"
        for child in self.children:
            if isinstance(child, ParseTree):
                ret += child.__repr__(level + 1)
            else:
                ret += "  " * (level + 1) + repr(child) + "\\n"
        return ret
