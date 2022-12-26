import enum


# Stack helper class
class Stack:
    def __init__(self):
        self.arr = []

    def push(self, value):
        self.arr.append(value)

    def pop(self):
        self.arr.pop()

    # Returns the top of the stack or an index
    def top(self, i=0):
        if i >= len(self.arr):
            raise Exception

        return self.arr[-1 * i - 1]

    # Checks if the name is in one of the open scopes
    def check_open_scopes(self, name):
        # Reverse array to get the innermost scope first
        for d in self.arr[::-1]:
            if name in d:
                return True

        return False

    # Returns info about the name found in the open scope
    def get_name(self, name):
        # Reverse array to get the innermost scope first
        for d in self.arr[::-1]:
            if name in d:
                return d[name]
        raise UndefinedVariableError(name)

    # Assign a value to a variable in open scopes
    def assign(self, obj, value):
        name = obj['name']  # name of the variable
        ttype = obj['ttype']  # type of the variable (used for in casting)
        if ttype == 'int':  # cast to int cuz we might get a double from python division
            value = int(value)

        if len(obj['arr_info']) == 0:  # if not dealing with an array
            # Reverse array to get the innermost scope first
            for d in self.arr[::-1]:
                if name in d:
                    d[name]['value'] = value
        else:
            instance = []
            # Reverse array to get the innermost scope first
            for d in self.arr[::-1]:  # first get the full array (stored in scope)
                if name in d:
                    instance = d[name]['value']
            for i in obj['arr_info'][0:-1]:  # get selected innermost array
                instance = instance[i]

            instance[obj['arr_info'][-1]] = value  # Change its value, this changes the value in the scope as well

# Store scopes in a stack where the top scope
# is the innermost scope.
# When we get out of a scope we pop it
SCOPE_STACK = Stack()


class TypeMismatchError(Exception):
    def __init__(self, expected, t, extra=None):
        self.expected = expected
        self.type = t
        self.extra = extra
        global SCOPE_STACK
        SCOPE_STACK = Stack()

    def __str__(self):
        if self.extra is not None:
            return f"[SEMANTIC ERROR]: expected '{self.expected}' but got '{self.type}' instead.\n {self.extra}"
        return f"[SEMANTIC ERROR]: expected '{self.expected}' but got '{self.type}' instead."


class UndefinedVariableError(Exception):
    def __init__(self, name):
        self.name = name
        global SCOPE_STACK
        SCOPE_STACK = Stack()

    def __str__(self):
        return f'[SEMANTIC ERROR]: variable {self.name} is undefined or out of scope.'


class RedefinedVariableError(Exception):
    def __init__(self, name):
        self.name = name
        global SCOPE_STACK
        SCOPE_STACK = Stack()

    def __str__(self):
        return f'[SEMANTIC ERROR]: variable {self.name} is defined more than once.'


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
    STRING = "string"
    TRUE = "true"
    FALSE = "false"
    NOT = "!"
    MUL = "*"
    DIV = "/"
    BASIC = "basic"
    SEMICOLON = ";"

    PRINT = "print"
    DOT = "."
    ROVER = "rover"

    ORIENTATION = "orientation"
    X_POS = "x_pos"
    Y_POS = "y_pos"
    GOLD = "gold"
    SILVER = "silver"
    COPPER = "copper"
    IRON = "iron"
    POWER = "power"
    MAX_MOVE = "max_move"
    CAN_MOVE = "can_move"

    SCAN = "scan"
    DRILL = "drill"
    SHOCKWAVE = "shockwave"
    BUILD = "build"
    SONAR = "sonar"
    PUSH = "push"
    RECHARGE = "recharge"
    BACKFLIP = "backflip"
    PRINT_INVENTORY = "print_inventory"
    PRINT_MAP = "print_map"
    PRINT_POS = "print_pos"
    PRINT_ORIENTATION = "print_orientation"
    CHANGE_MAP = "change_map"
    MOVE = "move"
    TURN = "turn"

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class NonTerminals(enum.Enum):
    TERMINAL = 0
    PROGRAM = 1
    BLOCK = 2
    DECLS = 3
    DECL = 4
    TYPE = 5
    TYPECL = 6
    STMT = 28
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

    GET = 24
    ACTION = 25
    DIRECTION = 26
    ROTATION = 27


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

    # Method to print the tree in XML like fashion
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

    # Method to print the tree in a tree like fashion
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

        # Rover non-terminals
        elif self.token == NonTerminals.DIRECTION:
            return "direction"
        elif self.token == NonTerminals.ROTATION:
            return "rotation"
        elif self.token == NonTerminals.ACTION:
            return "action"
        elif self.token == NonTerminals.GET:
            return "get"
        else:
            return "__UNKNOWN_TOKEN__"

    def check_semantics(self):
        for child in self.children:
            child.check_semantics()


'''
When check_semantics() returns somthing it is a dictionary with the following information:
{
    'ttype': t,
    'is_array': bool,
    'dim': 0..*,        # if we have an array this is the dimension of the array
    'value': None
}

access dict key with:
    dict['key_name']
'''


class ProgramNode(Node):
    pass


# <block>    ::= { <decls> <stmts> }
class BlockNode(Node):
    def check_semantics(self):
        global SCOPE_STACK
        # Add a new scope to the stack since a new block is found
        SCOPE_STACK.push({})

        for child in self.children:
            child.check_semantics()

        print(SCOPE_STACK.top())
        # Pop the stack once we get out of the scope
        SCOPE_STACK.pop()

    def run(self, rover):
        global SCOPE_STACK
        SCOPE_STACK.push({})  # create a new scope

        self.children[0].run(rover)
        self.children[1].run(rover)

        SCOPE_STACK.pop()  # remove scope when done


# <decl>     ::= <type> ID ;
class DeclNode(Node):
    def check_semantics(self):
        type_info = self.children[0].check_semantics()
        name = self.children[1].token.value  # name of ID

        # If the name already exist in current scope raise error
        if name in SCOPE_STACK.top():
            raise RedefinedVariableError(name)
        # Add variable to symbol table
        SCOPE_STACK.top()[name] = type_info

    def run(self, rover):
        type_obj = self.children[0].run(rover)  # get type info (array information as well)
        name = self.children[1].token.value  # get var name

        global SCOPE_STACK
        SCOPE_STACK.top()[name] = type_obj  # add variable to scope


# <decls>    ::= e
#              | <decl> <decls>
class DeclsNode(Node):
    def check_semantics(self):
        for child in self.children:
            # Stops checking when a node has no children
            child.check_semantics()

    def run(self, rover):
        for child in self.children:
            # Stops checking when a node has no children
            child.run(rover)

# <type>     ::= BASIC <typecl>
class TypeNode(Node):
    def check_semantics(self):
        ttype = self.children[0].token.value  # variable type
        type_info = self.children[1].check_semantics()  # returns info on if it is an array or not
        type_info['ttype'] = ttype

        return type_info

    def run(self, rover):
        ttype = self.children[0].token.value  # get the type
        arr_info = self.children[1].run(rover)  # info about dealing with arrays

        if arr_info is None:  # not dealing with an array
            return {
                'ttype': ttype,
                'value': None
            }

        return {  # dealing with array
            'ttype': ttype,
            # arr_info is an array [i, j, k, ...] where i j k are the length for each subarray respectively
            # ex: int [ i ] [ j ] [ k ] array ; -> [i, j, k]
            'value': arr_info  # if we have an array we initialize with an array of correct size of None values
        }


# <typecl>   ::= e
#              | [ NUM ] <typecl>
class TypeclNode(Node):
    def check_semantics(self):
        # If there is children then we are dealing with an array
        if len(self.children) > 0:
            type_info = self.children[1].check_semantics()  # Info on dim > 1 arrays
            type_info['dim'] = type_info['dim'] + 1  # Add a dimension every iteration
            type_info['is_arr'] = True  # Set is_arr flag to true
            return type_info

        # No children then just basic type
        return {
            'ttype': None,
            'is_arr': False,
            'dim': 0,
            'val': None
        }

    def run(self, rover):
        # If no children then empty
        if len(self.children) == 0:
            return None

        length = int(self.children[0].token.value)  # length of current array to create
        val = self.children[1].run(rover)  # get the value to put in the array (either None or a subarray of None)
        ret = []  # array to return

        for i in range(length):  # fill ret with the value found length times
            ret.append(val)
        return ret


# <stmt>     ::= <loc> = <bool> ;
#              | ROVER . <action> ;
#              | PRINT <bool> ;
#              | IF ( <bool> ) <stmt>
#              | IF ( <bool> ) <stmt> ELSE <stmt>
#              | WHILE ( <bool> ) <stmt>
#              | <block>
class StmtNode(Node):
    def check_semantics(self):
        # If there is a loc node
        if isinstance(self.children[0], LocNode):
            symbol = self.children[0].check_semantics()  # Returns info from symbol table
            type_info = self.children[2].check_semantics()  # Info on the assignment type
            # If types don't match OR the symbol is an array then we cannot assign the value
            if (
                    not (
                            symbol['ttype'] == type_info['ttype']
                            or (symbol['ttype'] == 'double' and type_info['ttype'] == 'int')
                    )
                    or symbol['is_arr']
            ):
                raise TypeMismatchError(symbol['ttype'], type_info['ttype'])

        # If we have a block node
        elif isinstance(self.children[0], BlockNode):
            self.children[0].check_semantics()  # Just evaluate the block semantics

        elif self.children[0].token.ttype == Vocab.ROVER:
            self.children[1].check_semantics()  # Just evaluate the action semantics

        elif self.children[0].token.ttype == Vocab.PRINT:
            self.children[1].check_semantics()  # Just evaluate the bool semantics

        # for an IF or WHILE token:
        elif self.children[0].token.ttype in [Vocab.IF, Vocab.WHILE]:
            # Make sure the condition in the statement is of type bool
            cond_info = self.children[1].check_semantics()
            if cond_info['ttype'] != 'bool':
                raise TypeMismatchError('bool', cond_info['ttype'], "condition must be a boolean.")

            # Evaluate the stmt nodes
            self.children[2].check_semantics()
            if len(self.children) == 5:  # if we have an ELSE stmt
                self.children[4].check_semantics()

    def run(self, rover):
        # If loc node
        if isinstance(self.children[0], LocNode):
            name_obj = self.children[0].run(rover)  # get info about variable
            bool_obj = self.children[2].run(rover)  # evaluate to bool stmt

            global SCOPE_STACK
            SCOPE_STACK.assign(name_obj, bool_obj)  # assign the value to the correct variable in scope

        # If block node
        elif isinstance(self.children[0], BlockNode):
            self.children[0].run(rover)  # Just run the block

        # TODO:
        elif self.children[0].token.ttype == Vocab.ROVER:
            return None

        # If print
        elif self.children[0].token.ttype == Vocab.PRINT:
            bool_obj = self.children[1].run(rover)  # eval the bool
            print(bool_obj)  # print the value

        # If stmt
        elif self.children[0].token.ttype == Vocab.IF:
            bool_obj = self.children[1].run(rover)  # eval the bool
            if bool_obj:  # if true then run the first stmt
                self.children[2].run(rover)
            elif len(self.children) == 5:  # else if we have an else then run the second stmt
                self.children[4].run(rover)

        # If while
        elif self.children[0].token.ttype == Vocab.WHILE:
            while True:  # keep going
                bool_obj = self.children[1].run(rover)
                if not bool_obj:  # break if the bool is false
                    break

                self.children[2].run(rover)  # keep running the stmt


# <stmts>    ::= e
#              | <stmt> <stmts>
class StmtsNode(Node):
    def check_semantics(self):
        for child in self.children:
            # Stops checking when a node has no children
            child.check_semantics()

    def run(self, rover):
        for child in self.children:
            # Stops checking when a node has no children
            child.run(rover)


# <loc>      ::= ID <loccl>
class LocNode(Node):
    def check_semantics(self):
        name = self.children[0].token.value  # name of variable for assignment

        # Check if the name is found in the open scopes
        global SCOPE_STACK
        if not SCOPE_STACK.check_open_scopes(name):
            raise UndefinedVariableError(name)

        # Handle array types
        # Can only assign to a basic type
        # So can only assign to the deepest indices of arrays
        symbol = SCOPE_STACK.get_name(name)  # Get info from symbol table
        type_info = self.children[1].check_semantics()  # Check if we ask for an array index
        type_dim = symbol['dim'] - type_info['dim']  # Gets the dimension of the assignment
        if type_dim < 0:
            # If negative then we asked for higher dimension than the array has
            raise TypeMismatchError('valid subscript', 'invalid subscript', extra='Wrong array subscript type')
        is_arr = True if type_dim > 0 else False  # if type_dim is 0 then it is a basic type

        return {
            'ttype': symbol['ttype'],
            'is_arr': is_arr,
            'dim': type_dim,
            'value': None
        }

    def run(self, rover):
        global SCOPE_STACK
        name = self.children[0].token.value
        obj = SCOPE_STACK.get_name(name)  # get variable from stack

        # arr_info is [i, j, k] where i, j, k are the indices to check when calling arr[i][j][k]
        arr_info = self.children[1].run(rover)  # check if it is an array

        if arr_info is None:  # if not an array
            return {
                'name': name,
                'value': obj['value'],
                'ttype': obj['ttype'],
                'arr_info': []
            }

        return {
            'name': name,
            'value': obj['value'],
            'ttype': obj['ttype'],
            'arr_info': arr_info
        }


# <loccl>    ::= e
#              | [ <bool> ] <loccl>
class LocclNode(Node):
    def check_semantics(self):
        # If there is children we are dealing with an array
        if len(self.children) > 0:
            # Make sure the index of the array evaluates to type 'int'
            index_info = self.children[0].check_semantics()
            if index_info['ttype'] != 'int':
                raise TypeMismatchError('int', index_info['ttype'], extra='Array index must by of type int')

            loccl_info = self.children[1].check_semantics()  # info about higher dim arrays
            loccl_info['dim'] = loccl_info['dim'] + 1  # add 1 to the dimension
            loccl_info['is_arr'] = True  # set is_arr flag to true
            return loccl_info

        # If no child then dealing with basic types
        # Type will be determined by upper node
        return {
            'ttype': None,
            'is_arr': False,
            'dim': 0,
            'value': None
        }

    def run(self, rover):
        # If no children then empty
        if len(self.children) == 0:
            return None

        bool_obj = self.children[0].run(rover)  # get index (from the bool node)
        loccl_info = self.children[1].run(rover)  # get array info

        if loccl_info is None:  # no subarray
            return [bool_obj]
        return [bool_obj] + loccl_info  # return [this index, next index]


# <bool>     ::= <join> <boolcl>
class BoolNode(Node):
    def check_semantics(self):
        join_info = self.children[0].check_semantics()
        boolcl_info = self.children[1].check_semantics()
        # If boolcl is empty then we only had a join node so return that (could be any type)
        if boolcl_info is None:
            return join_info

        # If we have boolcl then we have an || so both sides must be of type 'bool'
        if not (join_info['ttype'] == 'bool' and boolcl_info['ttype'] == 'bool'):
            raise TypeMismatchError('bool', '[int, double, string]')

        return join_info  # Only ttype will be used by upper nodes

    def run(self, rover):
        join_obj = self.children[0].run(rover)
        bool_obj = self.children[1].run(rover, join_obj)  # send join down to calculate the right order
        return bool_obj


# <boolcl>   ::= e
#              | || <join> <boolcl>
class BoolclNode(Node):
    def check_semantics(self):
        # If no child then node is empty
        if len(self.children) == 0:
            return None

        join_info = self.children[1].check_semantics()
        boolcl_info = self.children[2].check_semantics()
        # If boolcl is empty we just have a join node so return that (could be any type)
        if boolcl_info is None:
            return join_info

        # If we have boolcl we have || so both sides must be of type 'bool'
        if not (join_info['ttype'] == 'bool' and boolcl_info['ttype'] == 'bool'):
            raise TypeMismatchError('bool', '[int, double, string]')

        return join_info

    def run(self, rover, boolcl):
        # If no children then send most recent result
        if len(self.children) == 0:
            return boolcl

        join_obj = self.children[1].run(rover)
        join_obj = boolcl or join_obj  # calculate this bool

        bool_obj = self.children[2].run(rover, join_obj)  # recursive call
        return bool_obj


# <join>     ::= <equality> <joincl>
class JoinNode(Node):
    def check_semantics(self):
        equality_info = self.children[0].check_semantics()
        joincl_info = self.children[1].check_semantics()
        # If joincl is empty we just have an equality node so return that (could be any type)
        if joincl_info is None:
            return equality_info

        # If we have joincl then we have && so both sides must be of type 'bool'
        if not (equality_info['ttype'] == 'bool' and joincl_info['ttype'] == 'bool'):
            raise TypeMismatchError('bool', '[int, double, string]')
        return equality_info

    def run(self, rover):
        eq_obj = self.children[0].run(rover)
        join_obj = self.children[1].run(rover, eq_obj)  # send eq down to calculate the right order
        return join_obj
    

# <joincl>   ::= e
#              | && <equality> <joincl>
class JoinclNode(Node):
    def check_semantics(self):
        # If no children then the node is empty
        if len(self.children) == 0:
            return None

        equality_info = self.children[1].check_semantics()
        joincl_info = self.children[2].check_semantics()
        # If joincl is empty then we only have equality node so return that (could be any type)
        if joincl_info is None:
            return equality_info

        # If we have joincl then we have && so both sides must be of type 'bool'
        if not (equality_info['ttype'] == 'bool' and joincl_info['ttype'] == 'bool'):
            raise TypeMismatchError('bool', '[int, double, string]')
        return equality_info

    def run(self, rover, join):
        # If no children then send most recent result
        if len(self.children) == 0:
            return join

        eq_obj = self.children[1].run(rover)
        eq_obj = join and eq_obj  # calculate current join

        join_obj = self.children[2].run(rover, eq_obj)  # recursive call
        return join_obj
            

# <equality> ::= <rel> <equalcl>
class EqualityNode(Node):
    def check_semantics(self):
        rel_info = self.children[0].check_semantics()
        equalcl_info = self.children[1].check_semantics()
        # If equalcl is empty we only have rel node so return that (could be any type)
        if equalcl_info is None:
            return rel_info

        # No support for comparing strings
        if rel_info == 'string' or equalcl_info == 'string':
            raise TypeMismatchError('[int, double]', 'string')
        # If we have equalcl then we have == so both sides much match types or be 'int' or 'double'
        if not (
                rel_info['ttype'] == equalcl_info['ttype'] or
                (rel_info['ttype'] in ['int', 'double'] and equalcl_info['ttype'] in ['int', 'double'])
        ):
            raise TypeMismatchError(rel_info['ttype'], equalcl_info['ttype'])

        rel_info['ttype'] = 'bool'  # == returns a boolean
        return rel_info

    def run(self, rover):
        rel_obj = self.children[0].run(rover)
        equalcl_obj = self.children[1].run(rover, rel_obj)  # send rel down to calculate right order
        return equalcl_obj


# <equalcl>  ::= e
#              | == <rel> <equalcl>
#              | != <rel> <equalcl>
class EqualityclNode(Node):
    def check_semantics(self):
        # If no children then the node is empty
        if len(self.children) == 0:
            return None

        rel_info = self.children[1].check_semantics()
        equalcl_info = self.children[2].check_semantics()
        # If equalcl is empty we only have rel node so return that (could be any type)
        if equalcl_info is None:
            return rel_info

        # No support for comparing strings
        if rel_info == 'string' or equalcl_info == 'string':
            raise TypeMismatchError('[int, double]', 'string')
        # If we have equalcl we have == so both sides must match types or be 'int' or 'double'
        if not (
                rel_info['ttype'] == equalcl_info['ttype'] or
                (rel_info['ttype'] in ['int', 'double'] and equalcl_info['ttype'] in ['int', 'double'])
        ):
            raise TypeMismatchError(rel_info['ttype'], equalcl_info['ttype'])

        rel_info['ttype'] = 'bool'  # == returns a boolean
        return rel_info

    def run(self, rover, rel):
        # If no children then send most recent result
        if len(self.children) == 0:
            return rel

        op = self.children[0].token.value  # get operator
        rel_obj = self.children[1].run(rover)

        # Check and for equality depending on the operator
        if op == '==':
            rel_obj = rel == rel_obj
        else:
            rel_obj = rel != rel_obj

        equalcl_obj = self.children[2].run(rover, rel_obj)  # recursive call
        return equalcl_obj
            

# <rel>      ::= <expr> <reltail>
class RelNode(Node):
    def check_semantics(self):
        expr_info = self.children[0].check_semantics()
        reltail_info = self.children[1].check_semantics()

        # If reltail is empty we only have expr node so return that (could be any type)
        if reltail_info is None:
            return expr_info

        if expr_info == 'bool' or reltail_info == 'bool':
            raise TypeMismatchError('[int, double]', 'bool')
        if expr_info == 'string' or reltail_info == 'string':
            raise TypeMismatchError('[int, double]', 'string')

        expr_info['ttype'] = 'bool'  # A relation returns a boolean
        return expr_info

    def run(self, rover):
        expr_obj = self.children[0].run(rover)
        reltail_obj = self.children[1].run(rover, expr_obj)  # send expr down to calculate right order
        return reltail_obj


# <reltail>  ::= e
#              | <= <expr>
#              | >= <expr>
#              | > <expr>
#              | < <expr>
class ReltailNode(Node):
    def check_semantics(self):
        # If no children then node is empty
        if len(self.children) == 0:
            return None

        # Just need to evaluate the expression
        expr_info = self.children[1].check_semantics()
        return expr_info

    def run(self, rover, expr):
        # If no child then send most recent result
        if len(self.children) == 0:
            return expr

        # Get operator and evaluate expr and return evaluation
        op = self.children[0].token.value
        expr_obj = self.children[1].run(rover)
        if op == '<=':
            return expr <= expr_obj
        elif op == '>=':
            return expr >= expr_obj
        elif op == '>':
            return expr > expr_obj
        else:
            return expr < expr_obj


# <expr>     ::= <term> <exprcl>
class ExprNode(Node):
    def check_semantics(self):
        term_info = self.children[0].check_semantics()
        exprcl_info = self.children[1].check_semantics()

        # If exprecl is empty we only have term node so return that (could be any type)
        if exprcl_info is None:
            return term_info

        term_t = term_info['ttype']  # get type
        expr_t = exprcl_info['ttype']  # get type
        # Cannot add or subtract 'bool'
        if term_t == 'bool' or expr_t == 'bool':
            raise TypeMismatchError('[int, double]', 'bool')
        if term_t == 'string' or term_t == 'string':
            raise TypeMismatchError('[int, double]', 'string')

        if term_t == expr_t:  # Return the type if match (int or double)
            return term_info

        # If don't match but have double or int return double (super typing)
        if term_t in ['int', 'double'] and expr_t in ['int', 'double']:
            term_info['ttype'] = 'double'
            return term_info

    def run(self, rover):
        term_obj = self.children[0].run(rover)
        exprcl_obj = self.children[1].run(rover, term_obj)  # Send term so we can calculate in right order

        return exprcl_obj


# <exprcl>   ::= e
#              | + <term> <exprcl>
#              | - <term> <exprcl>
class ExprclNode(Node):
    # If no child then the node is empty
    def check_semantics(self):
        if len(self.children) == 0:
            return None

        term_info = self.children[1].check_semantics()
        exprcl_info = self.children[2].check_semantics()

        # If exprcl is empty then we only have term node so return that (could be any type)
        if exprcl_info is None:
            return term_info

        term_t = term_info['ttype']  # Get type
        expr_t = exprcl_info['ttype']  # get type
        # Cannot add or subtract 'bool'
        if term_t == 'bool' or expr_t == 'bool':
            raise TypeMismatchError('[int, double]', 'bool')
        if term_t == 'string' or term_t == 'string':
            raise TypeMismatchError('[int, double]', 'string')

        if term_t == expr_t:  # if types match return type (int or double)
            return term_info

        # If don't match but have double or int return double (super typing)
        if term_t in ['int', 'double'] and expr_t in ['int', 'double']:
            term_info['ttype'] = 'double'
            return term_info

    def run(self, rover, expr):
        # If no children then return most recent result
        if len(self.children) == 0:
            return expr

        term_obj = self.children[1].run(rover)
        op = self.children[0].token.value

        # Calculate the term with the term sent by parent node
        if op == '+':
            term_obj = expr + term_obj
        else:
            term_obj = expr - term_obj

        exprcl_obj = self.children[2].run(rover, term_obj)  # recursive call
        return exprcl_obj


# <term>     ::= <unary> <termcl>
class TermNode(Node):
    def check_semantics(self):
        unary_info = self.children[0].check_semantics()
        termcl_info = self.children[1].check_semantics()

        # If termcl empty then we only have unary node so return that (could be any type)
        if termcl_info is None:
            return unary_info

        unary_t = unary_info['ttype']  # get type
        term_t = termcl_info['ttype']  # get type
        # Cannot mult or div 'bool'
        if unary_t == 'bool' or term_t == 'bool':
            raise TypeMismatchError('[int, double]', 'bool')
        if unary_t == 'string' or term_t == 'string':
            raise TypeMismatchError('[int, double]', 'string')

        if unary_t == term_t:  # If types match just return type (int or double)
            return unary_info

        # If don't match but have double or int return double (super typing)
        if unary_t in ['int', 'double'] and term_t in ['int', 'double']:
            unary_info['ttype'] = 'double'
            return unary_info

    def run(self, rover):
        unary_obj = self.children[0].run(rover)
        termcl_obj = self.children[1].run(rover, unary_obj)  # Send unary so we can calculate in right order
        return termcl_obj


# <termcl>   ::= e
#              | * <unary> <termcl>
#              | / <unary> <termcl>
class TermclNode(Node):
    def check_semantics(self):
        # If no children then the node is empty
        if len(self.children) == 0:
            return None

        unary_info = self.children[1].check_semantics()
        termcl_info = self.children[2].check_semantics()

        # If termcl is empty we only have unary node so return that (could be any type)
        if termcl_info is None:
            return unary_info

        unary_t = unary_info['ttype']  # get type
        term_t = termcl_info['ttype']  # get type
        if unary_t == 'bool' or term_t == 'bool':
            raise TypeMismatchError('[int, double]', 'bool')
        if unary_t == 'string' or term_t == 'string':
            raise TypeMismatchError('[int, double]', 'string')

        if unary_t == term_t:  # If types match just return type (int or double)
            return unary_info

        # If don't match but have double or int return double (super typing)
        if unary_t in ['int', 'double'] and term_t in ['int', 'double']:
            unary_info['ttype'] = 'double'
            return unary_info

    def run(self, rover, term):
        # If no children then send most recent result
        if len(self.children) == 0:
            return term

        unary_val = self.children[1].run(rover)
        op = self.children[0].token.value

        # Calculate unary with the unary sent by parent node
        if op == '*':
            unary_val = term * unary_val
        else:
            if unary_val == 0:
                raise ZeroDivisionError
            unary_val = term / unary_val

        termcl_val = self.children[2].run(rover, unary_val)  # recursive call
        return termcl_val


# <unary>    ::= ! <unary>
#              | - <unary>
#              | <factor>
class UnaryNode(Node):
    def check_semantics(self):
        # If only 1 child we have factor node so just check its semantics
        if len(self.children) == 1:
            return self.children[0].check_semantics()

        unary_info = self.children[1].check_semantics()  # info about the unary node
        op = self.children[0].token.value  # operator ('!' or '-')
        unary_t = unary_info['ttype']  # Type of the unary node

        if op == '!' and unary_t == 'bool':  # not op must operate on 'bool'
            return unary_info
        if op == '-' and unary_t in ['int', 'double']:  # negate op must operate on numerals
            return unary_info

        # Else we got a string
        raise TypeMismatchError('bool, int, double', 'string')

    def run(self, rover):
        # If only one child we only have a factor node so evaluate that
        if len(self.children) == 1:
            return self.children[0].run(rover)

        unary_obj = self.children[1].run(rover)
        op = self.children[0].token.value

        # Calculate the unary depending on operator and return
        if op == '!':
            return not unary_obj
        else:
            return - unary_obj


# <factor>   ::= ( <bool> )
#              | <loc>
#              | ROVER . <get>
#              | NUM
#              | REAL
#              | TRUE
#              | FALSE
class FactorNode(Node):
    def check_semantics(self):
        # If we have ( <bool> ) just check semantics for <bool>
        if isinstance(self.children[0], BoolNode):
            return self.children[0].check_semantics()

        # If we have Loc node return the type of variable to assign
        if isinstance(self.children[0], LocNode):
            type_info = self.children[0].check_semantics()
            # If type is arr error because factor cannot have an array (cannot mul, div, add, sub, compare arrays)
            if type_info['is_arr']:
                print("Factor must be basic type")
                raise TypeMismatchError('basic type', 'array', extra='Factor must be basic type')
            return type_info

        # ===== BASIC types (base cases and rover attr.) ===== #
        if self.children[0].token.ttype == Vocab.ROVER:
            info = self.children[1].check_semantics()
            return info

        # If int return the int base type in dictionary
        if self.children[0].token.ttype == Vocab.NUM:
            return {
                'ttype': 'int',
                'is_arr': False,
                'dim': 0,
                'value': None
            }

        # If double return base type in dictionary
        if self.children[0].token.ttype == Vocab.REAL:
            return {
                'ttype': 'double',
                'is_arr': False,
                'dim': 0,
                'value': None
            }

        # If bool return base type in dictionary
        if self.children[0].token.ttype in [Vocab.TRUE, Vocab.FALSE]:
            return {
                'ttype': 'bool',
                'is_arr': False,
                'dim': 0,
                'value': None
            }

        if self.children[0].token.ttype == Vocab.STRING:
            return {
                'ttype': 'string',
                'is_arr': False,
                'dim': 0,
                'value': None
            }

    def run(self, rover):
        def _get_arr_index(obj):
            arr = obj['value']  # the full array stored in scope
            # arr_info is [i, j, k] where i, j, k are the indices to check when calling arr[i][j][k]
            for i in obj['arr_info'][0:-1]:  # Get each correct index until deepest array
                arr = arr[i]
            return arr[obj['arr_info'][-1]]  # return the correct deepest index value

        # If bool node
        if isinstance(self.children[0], BoolNode):
            return self.children[0].run(rover)

        # If loc node
        if isinstance(self.children[0], LocNode):
            loc_info = self.children[0].run(rover)  # get variable arr info
            # If variable is an array then use _get_arr_index to access the correct index
            value = loc_info['value'] if len(loc_info['arr_info']) == 0 else _get_arr_index(loc_info)
            return value

        # TODO:
        if self.children[0].token.ttype == Vocab.ROVER:
            return None

        # If int
        if self.children[0].token.ttype == Vocab.NUM:
            return int(self.children[0].token.value)  # cast string value to int

        # If double
        if self.children[0].token.ttype == Vocab.REAL:
            return float(self.children[0].token.value)  # cast string value to float

        # If true
        if self.children[0].token.ttype == Vocab.TRUE:  # return boolean True
            return True

        # if false
        if self.children[0].token.ttype == Vocab.FALSE:  # return boolean False
            return False

        # if string
        if self.children[0].token.ttype == Vocab.STRING:  # return the string
            return self.children[0].token.value


# ROVER NODES
class DirectionNode(Node):
    pass


class RotationNode(Node):
    pass


# <get>     ::= ORIENTATION
#             | X_POS
#             | Y_POS
#             | GOLD
#             | SILVER
#             | COPPER
#             | IRON
#             | POWER
#             | MAX_MOVE <direction>
#             | CAN_MOVE <direction
class GetNode(Node):
    def check_semantics(self):
        if self.children[0].token.ttype == Vocab.CAN_MOVE:  # can_move returns a bool
            return {
                'ttype': 'bool',
                'is_arr': False,
                'dim': 0,
                'value': None
            }
        else:  # the rest all return ints
            return {
                'ttype': 'int',
                'is_arr': False,
                'dim': 0,
                'value': None
            }


# <action>  ::= SCAN
#             | DRILL
#             | SHOCKWAVE
#             | BUILD
#             | SONAR
#             | PUSH
#             | RECHARGE
#             | BACKFLIP
#             | PRINT_INVENTORY
#             | PRINT_MAP
#             | PRINT_POS
#             | PRINT_ORIENTATION
#             | CHANGE_MAP
#             | MOVE <direction> <bool>
#             | TURN <rotation
class ActionNode(Node):
    def check_semantics(self):
        # If move we need to evaluate the bool expr and make sure it is an int
        if self.children[0].token.ttype == Vocab.MOVE:
            bool_info = self.children[2].check_semantics()
            if bool_info['ttype'] != 'int':
                raise TypeMismatchError('int', bool_info['ttype'])
