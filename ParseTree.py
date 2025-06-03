class ParseTree:
    def __init__(self, node_type):
        self.node_type = node_type
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self, level=0):
        ret = "  " * level + f"{self.node_type}\n"
        for child in self.children:
            if hasattr(child, '__repr__') and callable(child.__repr__):
                ret += child.__repr__(level + 1)
            else:
                ret += "  " * (level + 1) + repr(child) + "\n"
        return ret
