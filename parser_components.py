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
        for d in self.arr[::-1]:
            if name in d:
                return True

        return False

    def get_name(self, name):
        for d in self.arr[::-1]:
            if name in d:
                return d
        raise UndefinedVariableError


SCOPE_STACK = Stack()
SCOPE = {}


class TypeMismatchError(Exception):
    def __init__(self):
        global SCOPE_STACK
        SCOPE_STACK = Stack()


class UndefinedVariableError(Exception):
    def __init__(self):
        global SCOPE_STACK
        SCOPE_STACK = Stack()


class RedefinedVariableError(Exception):
    def __init__(self):
        global SCOPE_STACK
        SCOPE_STACK = Stack()


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
        pass
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

    def check_semantics(self):
        global SCOPE_STACK
        SCOPE_STACK.push({})

        for child in self.children:
            child.check_semantics()

        print(SCOPE_STACK.top())
        SCOPE_STACK.pop()


class DeclNode(Node):
    def check_scopes(self):
        # Build scope
        var_name = self.children[1].token.value
        symbol = {
            'ttype': None,
            'is_arr': False,
            'dim': 0,
            'val': None
        }
        # If var name already exist within scope then error
        if var_name in SCOPE_STACK.top():
            print("CANNOT REDEFINE VARIABLE")
            raise RedefinedVariableError

        SCOPE_STACK.top()[var_name] = symbol

    def check_semantics(self):
        name = self.children[1].token.value
        type_info = self.children[0].check_semantics()
        if name in SCOPE_STACK.top():
            print("CANNOT REDEFINE VARIABLE")
            raise RedefinedVariableError
        SCOPE_STACK.top()[name] = type_info


class DeclsNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        for child in self.children:
            child.check_semantics()


class TypeNode(Node):
    def check_semantics(self):
        ttype = self.children[0].token.value
        type_info = self.children[1].check_semantics()
        type_info['ttype'] = ttype

        return type_info


class TypeclNode(Node):
    def check_semantics(self):
        if len(self.children) > 0:
            type_info = self.children[1].check_semantics()
            type_info['dim'] = type_info['dim'] + 1
            type_info['is_arr'] = True
            return type_info

        return {
            'ttype': None,
            'is_arr': False,
            'dim': 0,
            'val': None
        }


class StmtNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if isinstance(self.children[0], LocNode):
            symbol = self.children[0].check_semantics()
            type_info = self.children[2].check_semantics()
            if (
                    not (
                            symbol['ttype'] == type_info['ttype']
                            or (symbol['ttype'] == 'double' and type_info['ttype'] == 'int')
                    )
                    or symbol['is_arr']
            ):
                raise TypeMismatchError

        elif isinstance(self.children[0], BlockNode):
            self.children[0].check_semantics()

        elif self.children[0].token.ttype in [Vocab.IF, Vocab.WHILE]:
            cond_info = self.children[1].check_semantics()
            if cond_info['ttype'] != 'bool':
                print("Condition must be a boolean")
                raise TypeMismatchError

            self.children[2].check_semantics()
            if len(self.children) == 5:
                self.children[4].check_semantics()


class StmtsNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        for child in self.children:
            child.check_semantics()


class LocNode(Node):
    def check_scopes(self):
        var_name = self.children[0].token.value

        global SCOPE_STACK
        if not SCOPE_STACK.check_open_scopes(var_name):
            print("UNDEFINED VARIABLE")
            raise UndefinedVariableError

        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        name = self.children[0].token.value

        global SCOPE_STACK
        if not SCOPE_STACK.check_open_scopes(name):
            print("UNDEFINED VARIABLE")
            raise UndefinedVariableError

        symbol = SCOPE_STACK.get_name(name)[name]  # Get info from symbol table
        type_info = self.children[1].check_semantics()  # Check if we ask for an array index
        type_dim = symbol['dim'] - type_info['dim']  # Gets the dimension of the assignment
        if type_dim < 0:
            raise TypeMismatchError  # If negative then we asked for higher dimension than the array has
        is_arr = True if type_dim > 0 else False  # if type_dim is 0 then it is a basic type

        return {
            'ttype': symbol['ttype'],
            'is_arr': is_arr,
            'dim': type_dim,
            'value': None
        }


class LocclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if len(self.children) > 0:
            index_info = self.children[0].check_semantics()
            if index_info['ttype'] != 'int':
                print("Array index must be of type int")
                raise TypeMismatchError

            loccl_info = self.children[1].check_semantics()
            loccl_info['dim'] = loccl_info['dim'] + 1
            loccl_info['is_arr'] = True
            return loccl_info

        return {
            'ttype': None,
            'is_arr': False,
            'dim': 0,
            'value': None
        }


class BoolNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        join_info = self.children[0].check_semantics()
        boolcl_info = self.children[1].check_semantics()
        if boolcl_info is None:
            return join_info

        if not (join_info['ttype'] == 'bool' and boolcl_info['ttype'] == 'bool'):
            raise TypeMismatchError

        return join_info


class BoolclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if len(self.children) == 0:
            return None

        join_info = self.children[1].check_semantics()
        boolcl_info = self.children[2].check_semantics()
        if boolcl_info is None:
            return join_info

        if not (join_info['ttype'] == 'bool' and boolcl_info['ttype'] == 'bool'):
            raise TypeMismatchError

        return join_info


class JoinNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        equality_info = self.children[0].check_semantics()
        joincl_info = self.children[1].check_semantics()
        if joincl_info is None:
            return equality_info

        if not (equality_info['ttype'] == 'bool' and joincl_info['ttype'] == 'bool'):
            raise TypeMismatchError

        return equality_info
    
    
class JoinclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if len(self.children) == 0:
            return None

        equality_info = self.children[1].check_semantics()
        joincl_info = self.children[2].check_semantics()
        if joincl_info is None:
            return equality_info

        if not (equality_info['ttype'] == 'bool' and joincl_info['ttype'] == 'bool'):
            raise TypeMismatchError

        return equality_info
            
            
class EqualityNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        rel_info = self.children[0].check_semantics()
        equalcl_info = self.children[1].check_semantics()
        if equalcl_info is None:
            return rel_info

        if not (
                rel_info['ttype'] == equalcl_info['ttype'] or
                (rel_info['ttype'] in ['int', 'double'] and equalcl_info['ttype'] in ['int', 'double'])
        ):
            raise TypeMismatchError

        rel_info['ttype'] = 'bool'
        return rel_info

            
class EqualityclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if len(self.children) == 0:
            return None

        rel_info = self.children[1].check_semantics()
        equalcl_info = self.children[2].check_semantics()
        if equalcl_info is None:
            return rel_info

        if not (
                rel_info['ttype'] == equalcl_info['ttype'] or
                (rel_info['ttype'] in ['int', 'double'] and equalcl_info['ttype'] in ['int', 'double'])
        ):
            raise TypeMismatchError

        rel_info['ttype'] = 'bool'
        return rel_info
            
            
class RelNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        expr_info = self.children[0].check_semantics()
        reltail_info = self.children[1].check_semantics()

        if reltail_info is None:
            return expr_info

        if not (expr_info['ttype'] in ['int', 'double'] and reltail_info['ttype'] in ['int', 'double']):
            raise TypeMismatchError

        expr_info['ttype'] = 'bool'
        return expr_info
            
            
class ReltailNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if len(self.children) == 0:
            return None

        expr_info = self.children[1].check_semantics()
        return expr_info
            
            
class ExprNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        term_info = self.children[0].check_semantics()
        exprcl_info = self.children[1].check_semantics()

        if exprcl_info is None:
            return term_info

        term_t = term_info['ttype']
        expr_t = exprcl_info['ttype']
        if term_t == 'bool' or expr_t == 'bool':
            raise TypeMismatchError

        if term_t == expr_t:
            return term_info

        if term_t in ['int', 'double'] and expr_t in ['int', 'double']:
            term_info['ttype'] = 'double'
            return term_info

        raise TypeMismatchError


class ExprclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if len(self.children) == 0:
            return None

        term_info = self.children[1].check_semantics()
        exprcl_info = self.children[2].check_semantics()

        if exprcl_info is None:
            return term_info

        term_t = term_info['ttype']
        expr_t = exprcl_info['ttype']
        if term_t == 'bool' or expr_t == 'bool':
            raise TypeMismatchError

        if term_t == expr_t:
            return term_info

        if term_t in ['int', 'double'] and expr_t in ['int', 'double']:
            term_info['ttype'] = 'double'
            return term_info

        raise TypeMismatchError


class TermNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        unary_info = self.children[0].check_semantics()
        termcl_info = self.children[1].check_semantics()

        if termcl_info is None:
            return unary_info

        unary_t = unary_info['ttype']
        term_t = termcl_info['ttype']
        if unary_t == 'bool' or term_t == 'bool':
            raise TypeMismatchError

        if unary_t == term_t:
            return unary_info

        if unary_t in ['int', 'double'] and term_t in ['int', 'double']:
            unary_info['ttype'] = 'double'
            return unary_info

        raise TypeMismatchError


class TermclNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if len(self.children) == 0:
            return None

        unary_info = self.children[1].check_semantics()
        termcl_info = self.children[2].check_semantics()

        if termcl_info is None:
            return unary_info

        unary_t = unary_info['ttype']
        term_t = termcl_info['ttype']
        if unary_t == 'bool' or term_t == 'bool':
            raise TypeMismatchError

        if unary_t == term_t:
            return unary_info

        if unary_t in ['int', 'double'] and term_t in ['int', 'double']:
            unary_info['ttype'] = 'double'
            return unary_info

        raise TypeMismatchError


class UnaryNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if len(self.children) == 1:
            return self.children[0].check_semantics()

        unary_info = self.children[1].check_semantics()
        op = self.children[0].token.value
        unary_t = unary_info['ttype']

        if op == '!' and unary_t == 'bool':
            return unary_info
        if op == '-' and unary_t in ['int', 'double']:
            return unary_info

        raise TypeMismatchError


class FactorNode(Node):
    def check_scopes(self):
        for child in self.children:
            child.check_scopes()

    def check_semantics(self):
        if isinstance(self.children[0], BoolNode):
            return self.children[0].check_semantics()

        if isinstance(self.children[0], LocNode):
            type_info = self.children[0].check_semantics()
            if type_info['is_arr']:
                print("Factor must be basic type")
                raise TypeMismatchError
            return type_info

        if self.children[0].token.ttype == Vocab.NUM:
            return {
                'ttype': 'int',
                'is_arr': False,
                'dim': 0,
                'value': None
            }

        if self.children[0].token.ttype == Vocab.REAL:
            return {
                'ttype': 'double',
                'is_arr': False,
                'dim': 0,
                'value': None
            }

        if self.children[0].token.ttype in [Vocab.TRUE, Vocab.FALSE]:
            return {
                'ttype': 'bool',
                'is_arr': False,
                'dim': 0,
                'value': None
            }
