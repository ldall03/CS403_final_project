"""
Create nodes + parse tree using grammar:

   <program>  ::= <block>
   <block>    ::= { <decls> <stmts> }
   <decls>    ::= e 
                | <decl> <decls>
   <decl>     ::= <type> ID ;
   <type>     ::= BASIC <typecl>
   <typecl>   ::= e 
                | [ NUM ] <typecl>
   <stmts>    ::= e 
                | <stmt> <stmts>
   <stmt>     ::= <loc> = <bool> ;
                | IF ( <bool> ) <stmt>
                | IF ( <bool> ) <stmt> ELSE <stmt>
                | WHILE ( <bool> ) <stmt>
                | <block>
   <loc>      ::= ID <loccl>
   <loccl>    ::= e 
                | [ <bool> ] <loccl>
   <bool>     ::= <join> <boolcl>
   <boolcl>   ::= e 
                | || <join> <boolcl>
   <join>     ::= <equality> <joincl>
   <joincl>   ::= e 
                | && <equality> <joincl>
   <equality> ::= <rel> <equalcl>
   <equalcl>  ::= e 
                | == <rel> <equalcl> 
                | != <rel> <equalcl>
   <rel>      ::= <expr> <reltail>
   <reltail>  ::= e 
                | <= <expr>
                | >= <expr>
                | > <expr>
                | < <expr>
   <expr>     ::= <term> <exprcl>
   <exprcl>   ::= e
                | + <term> <exprcl>
                | - <term> <exprcl>
   <term>     ::= <unary> <termcl>
   <termcl>   ::= e
                | * <unary> <termcl>
                | / <unary> <termcl>
   <unary>    ::= ! <unary>
                | - <unary>
                | <factor>
   <factor>   ::= ( <bool> )
                | <loc>
                | NUM
                | REAL
                | TRUE
                | FALSE
"""

import enum
import sys
import pathlib

from parser_components import (
    MinusNode,
    Node,
    NonTerminals,
    NotNode,
    Token,
    Vocab,

    FactorNode,
    UnaryNode,
    TermNode,
    TermclNode,
    ExprNode,
    ExprclNode,
    RelNode,
    ReltailNode,
    EqualityNode,
    EqualityclNode,
    JoinNode,
    JoinclNode,
    BoolNode,
    BoolclNode,
    LocNode,
    LocclNode,
    StmtNode,
    StmtsNode,
    TypeNode,
    TypeclNode,
    DeclNode,
    DeclsNode,
    BlockNode,
    ProgramNode
)

CURR_TOKEN = None
FILE_CONTENT = []
TYPES = ["int", "char", "bool", "double"]

TERMINALS = (
        set(
            [e.value for e in Vocab] + TYPES
        ) - {"integer", "float", "basic", "id"}
)


class UnexpectedTokenError(Exception):
    pass


def is_str(val):
    return val.startswith('"') and val.endswith('"')


def is_integer(val):
    try:
        if is_str(val):
            return False
        t = int(val)
        if str(t) != val:
            # If we've reached here, then we have a double
            # and the decimals were cut off
            return False
    except Exception:
        return False
    return True


def is_double(val):
    try:
        if is_str(val):
            return False
        t = float(val)
        if str(t) != val:
            return False
        if is_integer(val):
            # A float value would fail
            # the integer check
            return False
    except Exception:
        return False
    return True


def get_token():
    # Check if there's anything left in the file
    if len(FILE_CONTENT) == 0:
        return Token()

    def _get_vocab_entry(curr):
        for entry in Vocab:
            if entry.value == curr:
                return entry
        return None

    # Handle all the standard lexemes, types get a special one
    curr = FILE_CONTENT.pop()
    if curr in TERMINALS:
        if curr in TYPES:
            return Token(curr, Vocab.BASIC)
        return Token(curr, _get_vocab_entry(curr))

    # Handle number literals
    if is_integer(curr):
        return Token(curr, Vocab.NUM)
    if is_double(curr):
        return Token(curr, Vocab.REAL)

    # Everything else is an identifier
    return Token(curr, Vocab.ID)


def must_be(terminal):
    global CURR_TOKEN
    if Vocab[CURR_TOKEN.ttype.name] != terminal:
        raise UnexpectedTokenError(
            f"Unexpected token found: {CURR_TOKEN.value}, "
            f"expected: {terminal}"
        )
    CURR_TOKEN = get_token()
    return True


def match_cases(*cases):
    for case in cases:
        if CURR_TOKEN.ttype == case:
            return True
    return False


# <factor>   ::= ( <bool> )
#              | <loc>
#              | NUM
#              | REAL
#              | TRUE
#              | FALSE
def Factor():
    global CURR_TOKEN
    current = FactorNode(NonTerminals.FACTOR)
    if match_cases(
            Vocab.NUM,
            Vocab.REAL,
            Vocab.TRUE,
            Vocab.FALSE,
    ):
        current.add_child(Node(CURR_TOKEN))
        CURR_TOKEN = get_token()
    elif match_cases(Vocab.ID):
        current.add_child(Loc())
    else:
        must_be(Vocab.OPEN_PAREN)
        current.add_child(Bool())
        must_be(Vocab.CLOSE_PAREN)
    return current


# <unary>    ::= ! <unary>
#              | - <unary>
#              | <factor>
def Unary():
    global CURR_TOKEN
    current = UnaryNode(NonTerminals.UNARY)
    if match_cases(
            Vocab.NOT,
            Vocab.MINUS,
    ):
        if match_cases(Vocab.NOT):
            n = NotNode(CURR_TOKEN)
        else:
            n = MinusNode(CURR_TOKEN)
        current.add_child(n)
        current.operation_node = n

        CURR_TOKEN = get_token()

        unode = Unary()
        current.add_child(unode)
        current.operand = unode
    else:
        fnode = Factor()
        current.add_child(fnode)
        current.operand = fnode
    return current


# <termcl>   ::= e
#              | * <unary> <termcl>
#              | / <unary> <termcl>
def Termcl():
    global CURR_TOKEN
    current = TermclNode(NonTerminals.TERMCL)
    if match_cases(
            Vocab.MUL,
            Vocab.DIV,
    ):
        current.add_child(Node(CURR_TOKEN))
        CURR_TOKEN = get_token()
        current.add_child(Unary())
        current.add_child(Termcl())
    return current


# <term>     ::= <unary> <termcl>
def Term():
    current = TermNode(NonTerminals.TERM)
    current.add_child(Unary())
    current.add_child(Termcl())
    return current


# <exprcl>   ::= e
#              | + <term> <exprcl>
#              | - <term> <exprcl>
def Exprcl():
    global CURR_TOKEN
    current = ExprclNode(NonTerminals.EXPRCL)
    if match_cases(
            Vocab.PLUS,
            Vocab.MINUS,
    ):
        current.add_child(Node(CURR_TOKEN))
        CURR_TOKEN = get_token()
        current.add_child(Term())
        current.add_child(Exprcl())
    return current


# <expr>     ::= <term> <exprcl>
def Expr():
    current = ExprNode(NonTerminals.EXPR)
    current.add_child(Term())
    current.add_child(Exprcl())
    return current


# <reltail>  ::= e 
#              | <= <expr>
#              | >= <expr>
#              | > <expr>
#              | < <expr>
def Reltail():
    global CURR_TOKEN
    current = ReltailNode(NonTerminals.RELTAIL)
    if match_cases(
            Vocab.LTEQ,
            Vocab.GTEQ,
            Vocab.LT,
            Vocab.GT,
    ):
        current.add_child(Node(CURR_TOKEN))
        CURR_TOKEN = get_token()
        current.add_child(Expr())
    return current


# <rel>      ::= <expr> <reltail>
def Rel():
    current = RelNode(NonTerminals.REL)
    current.add_child(Expr())
    current.add_child(Reltail())
    return current


# <equalcl>  ::= e 
#              | == <rel> <equalcl> 
#              | != <rel> <equalcl>
def Equalcl():
    global CURR_TOKEN
    current = EqualityclNode(NonTerminals.EQUALCL)
    if match_cases(
            Vocab.EQ,
            Vocab.NEQ,
    ):
        current.add_child(Node(CURR_TOKEN))
        CURR_TOKEN = get_token()
        current.add_child(Rel())
        current.add_child(Equalcl())
    return current


# <equality> ::= <rel> <equalcl>
def Equality():
    current = EqualityNode(NonTerminals.EQUALITY)
    current.add_child(Rel())
    current.add_child(Equalcl())
    return current


# <joincl>   ::= e 
#              | && <equality> <joincl>
def Joincl():
    global CURR_TOKEN
    current = JoinclNode(NonTerminals.JOINCL)
    if match_cases(Vocab.AND):
        current.add_child(Node(CURR_TOKEN))
        CURR_TOKEN = get_token()
        current.add_child(Equality())
        current.add_child(Joincl())
    return current


# <join>     ::= <equality> <joincl>
def Join():
    current = JoinclNode(NonTerminals.JOIN)
    current.add_child(Equality())
    current.add_child(Joincl())
    return current


# <boolcl>   ::= e 
#              | || <join> <boolcl>
def Boolcl():
    global CURR_TOKEN
    current = BoolclNode(NonTerminals.BOOLCL)
    if match_cases(Vocab.OR):
        current.add_child(Node(CURR_TOKEN))
        CURR_TOKEN = get_token()
        current.add_child(Join())
        current.add_child(Boolcl())
    return current


# <bool>     ::= <join> <boolcl>
def Bool():
    current = BoolNode(NonTerminals.BOOL)
    current.add_child(Join())
    current.add_child(Boolcl())
    return current


# <loccl>    ::= e 
#              | [ <bool> ] <loccl>
def Loccl():
    global CURR_TOKEN
    current = LocclNode(NonTerminals.LOCCL)
    if match_cases(Vocab.OPEN_SQPAR):
        CURR_TOKEN = get_token()
        current.add_child(Bool())
        must_be(Vocab.CLOSE_SQPAR)
        current.add_child(Loccl())
    return current


# <loc>      ::= ID <loccl>
def Loc():
    global CURR_TOKEN
    current = LocNode(NonTerminals.LOC)
    current.add_child(Node(CURR_TOKEN))
    must_be(Vocab.ID)
    current.add_child(Loccl())
    return current


# <stmt>     ::= <loc> = <bool> ;
#              | IF ( <bool> ) <stmt>
#              | IF ( <bool> ) <stmt> ELSE <stmt>
#              | WHILE ( <bool> ) <stmt>
#              | <block>
def Stmt():
    global CURR_TOKEN
    current = StmtNode(NonTerminals.STMT)
    if match_cases(Vocab.IF):
        current.add_child(Node(CURR_TOKEN))
        CURR_TOKEN = get_token()

        must_be(Vocab.OPEN_PAREN)
        current.add_child(Bool())
        must_be(Vocab.CLOSE_PAREN)
        current.add_child(Stmt())

        if match_cases(Vocab.ELSE):
            current.add_child(Node(CURR_TOKEN))
            CURR_TOKEN = get_token()
            current.add_child(Stmt())

    elif match_cases(Vocab.WHILE):
        current.add_child(Node(CURR_TOKEN))
        CURR_TOKEN = get_token()

        must_be(Vocab.OPEN_PAREN)
        current.add_child(Bool())
        must_be(Vocab.CLOSE_PAREN)
        current.add_child(Stmt())

    elif match_cases(Vocab.OPEN_BRACE):
        current.add_child(Block())
    else:
        current.add_child(Loc())
        current.add_child(Node(CURR_TOKEN))

        must_be(Vocab.ASSIGN)
        current.add_child(Bool())
        must_be(Vocab.SEMICOLON)
    return current


# <stmts>    ::= e 
#              | <stmt> <stmts>
def Stmts():
    current = StmtsNode(NonTerminals.STMTS)
    if match_cases(
            Vocab.CLOSE_BRACE,  # More concise to start with Follow(<stmts>)
    ):
        pass
    else:
        current.add_child(Stmt())
        current.add_child(Stmts())
    return current


# <typecl>   ::= e 
#              | [ NUM ] <typecl>
def Typecl():
    global CURR_TOKEN
    current = TypeclNode(NonTerminals.TYPECL)
    if match_cases(Vocab.OPEN_SQPAR):
        CURR_TOKEN = get_token()
        current.add_child(Node(CURR_TOKEN))
        must_be(Vocab.NUM)
        must_be(Vocab.CLOSE_SQPAR)
        current.add_child(Typecl())
    return current


# <type>     ::= BASIC <typecl>
def Type():
    global CURR_TOKEN
    current = TypeNode(NonTerminals.TYPE)
    current.add_child(Node(CURR_TOKEN))
    must_be(Vocab.BASIC)
    current.add_child(Typecl())
    return current


# <decl>     ::= <type> ID ;
def Decl():
    global CURR_TOKEN
    current = DeclNode(NonTerminals.DECL)
    current.add_child(Type())
    current.add_child(Node(CURR_TOKEN))
    must_be(Vocab.ID)
    must_be(Vocab.SEMICOLON)
    return current


# <decls>    ::= e 
#              | <decl> <decls>
# Note: Follow(<decls>) = First(<stmt>) + Follow(<stmts>)
def Decls():
    current = DeclsNode(NonTerminals.DECLS)
    if match_cases(
            Vocab.IF,
            Vocab.WHILE,
            Vocab.OPEN_BRACE,
            Vocab.ID,
            Vocab.CLOSE_BRACE,
    ):
        pass
    else:
        current.add_child(Decl())
        current.add_child(Decls())
    return current


# <block>    ::= { <decls> <stmts> }
def Block():
    current = BlockNode(NonTerminals.BLOCK)
    must_be(Vocab.OPEN_BRACE)
    current.add_child(Decls())
    current.add_child(Stmts())
    must_be(Vocab.CLOSE_BRACE)
    return current


# <program>  ::= <block>
def Program():
    current = ProgramNode(NonTerminals.PROGRAM)
    current.add_child(Block())
    return current


def get_parse_tree(file_content):
    """Returns a parse tree (AST) for the given file content.

    The file content needs to be a string. It will be split, and
    reversed by this method.
    """
    global FILE_CONTENT
    global CURR_TOKEN

    if not file_content:
        raise Exception("Empty program given! Cannot produce a parse tree.")

    # Split the content, then reverse the list so we
    # can use it like a stack
    FILE_CONTENT = file_content.split()[::-1]
    CURR_TOKEN = get_token()

    return Program()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Missing file path to parse.")
    elif len(sys.argv) > 2:
        raise Exception("Only 1 argument is needed, but more were given.")

    fcontent = None
    filepath = pathlib.Path(sys.argv[1])
    with filepath.open() as f:
        fcontent = f.read()

    program = get_parse_tree(fcontent)
    program.check_semantics()
    program.run()
