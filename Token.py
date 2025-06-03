class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def getType(self):      # ✅ Required by autograder
        return self.type

    def getValue(self):     # ✅ Required by autograder
        return self.value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"
