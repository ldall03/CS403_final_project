# CS403_final_project
A parsing and semantics project written in python

# How to run
In a terminal window, run ```python rover.py``` this will
start a rover which will wait for commands to execute.
In another terminal window, run ```python main.py [file_to_parse] [rover_name]```
for example: ```python main.py parsing-tests/dfs_drill.txt Rover1```. By default the rover name
is ```Rover1```.

# Writting parsing tests
You can write your own parsing tests in a .txt file and send commands to the rover. Here is the grammar for our language:

```
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
   <stmt>     ::= ;
                | <loc=> = <bool> ;
                | ROVER . <action> ;
                | PRINT <bool> ;
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
                | ROVER . <get>
                | NUM
                | REAL
                | TRUE
                | FALSE
                | STRING

   <get>      ::= ORIENTATION
                | X_POS
                | Y_POS
                | GOLD
                | SILVER
                | COPPER
                | IRON
                | POWER
                | SONAR
                | MAX_MOVE <direction>
                | CAN_MOVE <direction

    <action>  ::= SCAN
                | DRILL
                | SHOCKWAVE
                | BUILD
                | SONAR
                | PUSH
                | RECHARGE
                | BACKFLIP
                | PRINT_INVENTORY
                | PRINT_MAP
                | PRINT_POS
                | PRINT_ORIENTATION
                | CHANGE_MAP STRING
                | MOVE <direction> <bool>
                | TURN <rotation

    <direction> ::= UP
                  | DOWN
                  | LEFT
                  | RIGHT
    <rotation> ::= LEFT
                 | RIGHT
```

The language is a dumbed down version of c++. Variable declarations must be done before any expressions in a block
and everything has to be done in a block. Check the provided examples in parsing-tests to understand 
how the language works. We also added some more functions to interface with the rover.
