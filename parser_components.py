import enum


# Stack helper class
class Stack:
    def __init__(self):
        self.arr = []

    def push(self, value):
        self.arr.append(value)

    def pop(self):
        self.arr.pop()

    def top(self, i=0):
        if i >= len(self.arr):
            raise Exception

        return self.arr[-1 * i - 1]

    def check_open_scopes(self, name):
        for d in self.arr:
            if name in d:
                return True

        return False


SCOPE_STACK = Stack()
SCOPE = {}


class TypeMismatchError(Exception):
    pass


class Vocab(enum.Enum):
    EOS = ""
    OPEN_PAREN = "("
    CLOSE_PAREN = ")"
    OPEN_BRACE = "{"
    CLOSE_BRACE = "}"
    OPEN_SQPAR = "["
    CLOSE_SQPAR = "]"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    ID = "id"
    AND = "&&"
    OR = "||"
    ASSIGN = "="
    EQ = "=="
    NEQ = "!="
    LTEQ = "<="
    GTEQ = ">="
    LT = "<"
    GT = ">"
    PLUS = "+"
    MINUS = "-"
    NUM = "integer"
    REAL = "float"
    TRUE = "true"
    FALSE = "false"
    NOT = "!"
    MUL = "*"
    DIV = "/"
    BASIC = "basic"
    SEMICOLON = ";"


class NonTerminals(enum.Enum):
    TERMINAL = 0
    PROGRAM = 1
    BLOCK = 2
    DECLS = 3
    DECL = 4
    TYPE = 5
    TYPECL = 6
    STMT = 7
    STMTS = 7
    LOC = 8
    LOCCL = 9
    BOOL = 10
    BOOLCL = 11
    JOIN = 12
    JOINCL = 13
    EQUALITY = 14
    EQUALCL = 15
    REL = 16
    RELTAIL = 17
    EXPR = 18
    EXPRCL = 19
    TERM = 20
    TERMCL = 21
    UNARY = 22
    FACTOR = 23


class Token:
    def __init__(self, value=0, ttype=Vocab.EOS):
        self.value = value
        self.ttype = ttype

    def __eq__(self, other_token):
        return self.value == other_token.value

    def __hash__(self):
        return hash(self.value)


class Node:
    def __init__(self, token):
        self.token = token
        self.children = []

    @property
    def is_token(self):
        return isinstance(self.token, Token)

    @property
    def is_nonterminal(self):
        return not self.is_token

    def add_child(self, node):
        self.children.append(node)

    def print(self, indent=0):
        symbol = self.print_val()
        if self.is_nonterminal:
            print(f"{' ' * indent} < {symbol} >")
        else:
            print(f"{' ' * indent} < {symbol} >")
        for child in self.children:
            child.print(indent=indent+2)
        if self.is_nonterminal:
            print(f"{' ' * indent} </ {symbol} >")

    def show(self, level_markers=None):
        if level_markers is None:
            level_markers = []

        marker_str = '+--  '
        empty_str = '     '
        conn_string = '|    '

        current_level = len(level_markers)
        mapper = lambda draw: conn_string if draw else empty_str
        # Map the lambda to an array of booleans which tells us which string to print
        # We print the conn_string if true because this node is not the last child if it is the case
        markers = "".join(map(mapper, level_markers[:-1]))
        markers += marker_str if current_level > 0 else ""
        print(markers, end='')
        if not self.is_nonterminal:
            print(self.token.value)
        else:
            print(self.print_val())

        # Call show() recursively on each of its children
        for i, child in enumerate(self.children):
            is_last = i == len(self.children) - 1
            child.show([*level_markers, not is_last])

    def print_val(self):
        if not self.is_nonterminal:
            return self.token.value
        return self.print_nonterminal()

    def print_nonterminal(self):
        if self.token == NonTerminals.PROGRAM:
            return "program"
        elif self.token == NonTerminals.BLOCK:
            return "block"
        elif self.token == NonTerminals.DECLS:
            return "decls"
        elif self.token == NonTerminals.DECL:
            return "decl"
        elif self.token == NonTerminals.TYPE:
            return "type"
        elif self.token == NonTerminals.TYPECL:
            return "typecl"
        elif self.token == NonTerminals.STMTS:
            return "stmts"
        elif self.token == NonTerminals.STMT:
            return "stmt"
        elif self.token == NonTerminals.LOC:
            return "loc"
        elif self.token == NonTerminals.LOCCL:
            return "loccl"
        elif self.token == NonTerminals.BOOL:
            return "bool"
        elif self.token == NonTerminals.BOOLCL:
            return "boolcl"
        elif self.token == NonTerminals.JOIN:
            return "join"
        elif self.token == NonTerminals.JOINCL:
            return "joincl"
        elif self.token == NonTerminals.EQUALITY:
            return "equality"
        elif self.token == NonTerminals.EQUALCL:
            return "equalitycl"
        elif self.token == NonTerminals.REL:
            return "rel"
        elif self.token == NonTerminals.RELTAIL:
            return "reltail"
        elif self.token == NonTerminals.EXPR:
            return "expr"
        elif self.token == NonTerminals.EXPRCL:
            return "exprcl"
        elif self.token == NonTerminals.TERM:
            return "term"
        elif self.token == NonTerminals.TERMCL:
            return "termcl"
        elif self.token == NonTerminals.UNARY:
            return "unary"
        elif self.token == NonTerminals.FACTOR:
            return "factor"
        else:
            return "???"

    def get_types(self):
        raise Exception(f"Not implemented for {self.__class__.__name__}")

    def match_types(self, target_types):
        my_types = self.get_types()
        if any(
            ttype in my_types
            for ttype in target_types
        ):
            return True
        return False

    def raise_type_mismatch_error(self, target):
        raise TypeMismatchError(
            f"Expected these types {self.get_types()}, "
            f"but found {target}"
        )

    def check_semantics(self):
        """Checks the semantics of the tree."""
        self.check_scopes()
        self.check_types()

    def check_types(self):
        for child in self.children:
            child.check_types()

    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def run(self):
        for child in self.children:
            child.run()


class ProgramNode(Node):
    def run(self):
        """
        Note that you can also build the SCOPE while going through
        the scope checking for the declarations.
        """
        global SCOPE

        result = -9
        for child in self.children:
            result = child.run()
        if result in (0,):
            print(f"Successfully ran the program, exited with: {result}")
        else:
            print(f"Failed to run program, exited with: {result}")


class BlockNode(Node):
    def check_scopes(self):
        global SCOPE_STACK
        SCOPE_STACK.push({})

        for child in self.children:
            child.check_scopes()

        SCOPE_STACK.pop()


class DeclNode(Node):
    def check_scopes(self):
        # Build scope
        var_name = self.children[1].token.value
        symbol = {
            'ttype': None,  # TODO: need a way to get the type
            'val': None
        }
        # If var name already exist within scope then error
        if var_name in SCOPE_STACK.top():
            print("CANNOT REDEFINE VARIABLE")
            raise Exception

        SCOPE_STACK.top()[var_name] = symbol


class DeclsNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class TypeNode(Node):
    pass


class TypeclNode(Node):
    pass


class StmtNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class StmtsNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class LocNode(Node):
    def check_scopes(self):
        var_name = self.children[0].token.value

        global SCOPE_STACK
        print(SCOPE_STACK.arr)
        if not SCOPE_STACK.check_open_scopes(var_name):
            print("UNDEFINED VARIABLE")
            raise Exception

        for child in self.children:
            child.check_scopes()


class LocclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class BoolNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class BoolclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()
            

class JoinNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()
    
    
class JoinclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()
            
            
class EqualityNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()
            
            
class EqualityclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()
            
            
class RelNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()
            
            
class ReltailNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()
            
            
class ExprNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class ExprclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class TermNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class TermclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class UnaryNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


class FactorNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()


# ............................... #
# .......... HIS CODE ........... #
# ............................... #

class MinusNode(ProgramNode):
    def get_types(self):
        return ("double", "int")

    def check_scopes(self):
        global SCOPE
        self.operand.check_scopes()

    def check_types(self):
        global SCOPE
        if not self.match_types(self.operand.get_types()):
            self.raise_type_mismatch_error(self.operand.get_types())

    def run(self):
        """ What does this do?

        In this node, you only have one child. We run, the child then
        multiply it's result by -1. In this case, the child MUST return
        an int or a double (hint for type checking above), then we
        return this result.

        Value storage, and retrieval should be done within the scope, e.g.
        the scope entry for an `int i ; i = 10 ;` should look something
        like this within the scope entry:
            SCOPE = {
                "i": {
                    "name": "i"
                    "value": 10
                }
            }
        """
        return self.operand.run() * -1


class NotNode(ProgramNode):
    pass


class _FactorNode(ProgramNode):
    pass


class _UnaryNode(ProgramNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operation_node = None

    def check_scopes(self):
        if self.operation_node:
            self.operation_node.operand = self.operand
        super().check_scopes()

    def check_types(self):
        if self.operation_node:
            self.operation_node.check_types()
        self.operand.check_types()

    def run(self):
        if self.operation_node:
            return self.operation_node.run()
        return self.operand.run()
