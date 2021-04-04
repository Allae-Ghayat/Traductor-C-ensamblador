from sly import Parser
from AnalizadorLexico import AnalizadorLexico
from Nodos import *

class AnalizadorSintactico(Parser):
    tokens = AnalizadorLexico.tokens
    # debugfile = 'parser.out'

    precedence = (
        ('right', EMPTY), # nivel 1
        ('right', ELSE),  # nivel 2
    )

    # Program
    #  -> global_declaration Program
    #   | function_definition Program
    #   | TYPE main '(' ')' code_block

    @_('global_declaration Program')
    def Program(self, p):
        return StatementNode(p.global_declaration, p.Program)

    @_('function_definition Program')
    def Program(self, p):
        return StatementNode(p.function_definition, p.Program)

    @_('TYPE MAIN "(" ")" code_block')
    def Program(self, p):
        return StatementNode(MainCallNode(p.code_block), Node())

    # global_declaration
    #  -> TYPE ID global_definition ';'

    @_('TYPE ID global_definition ";"')
    def global_declaration(self, p):
        return p.global_definition

    # global_definition
    #  -> ε
    #   | '=' INT   

    @_('EMPTY')
    def global_definition(self, p):
        return GlobalDefinitionNode(p[-3], IdNode(p[-2]), ValueNode(None))

    @_(' "=" INT')
    def global_definition(self, p):
        return GlobalDefinitionNode(p[-4], IdNode(p[-3]), ValueNode(p.INT))

    """
    Esta regla podría factorizarse, pero consideramos que es más legible
    así la gramática que creando nuevas reglas para aceptar un
    parameter_list vacío.
    """
    # function_definition
    #  -> TYPE ID '(' parameter_list ')' '{' code_block '}'
    #   | TYPE ID '(' ')' '{' code_block '}'

    @_('TYPE ID "(" parameter_list ")" "{" statement_list "}"')
    def function_definition(self, p):
        return FunctionDefinitionNode(p.TYPE, IdNode(p.ID), ValueNode(p.parameter_list), p.statement_list)

    @_('TYPE ID "(" ")" "{" statement_list "}"')
    def function_definition(self, p):
        return FunctionDefinitionNode(p.TYPE, IdNode(p.ID), ValueNode(list()), p.statement_list)

    # parameter_list
    #  -> TYPE ID ',' parameter_list
    #   | TYPE ID

    @_('TYPE ID "," parameter_list')
    def parameter_list(self, p):
        return list([(p.TYPE, p.ID)]) + p.parameter_list

    @_('TYPE ID')
    def parameter_list(self, p):
        return list([(p.TYPE, p.ID)]) 

    # statement
    #  -> selection_statement
    #   | while '(' expr ')' code_block
    #   | TYPE ID variable_definition ';'
    #   | expr ';'
    #   | printf '(' argument_list ')' ';'
    #   | scanf '(' argument_list ')' ';'
    #   | return expr ';'

    @_('selection_statement')
    def statement(self, p):
        return p.selection_statement

    @_('WHILE "(" expr ")" code_block ')
    def statement(self,p):
        return WhileStatementNode(p.expr,p.code_block)

    @_('TYPE ID variable_definition ";"')
    def statement(self, p):
        return p.variable_definition;

    # variable_definition
    #  -> '=' expr
    #   | ε

    @_('"=" expr')
    def variable_definition(self, p):
        return VariableDefinitionNode(p[-4], IdNode(p[-3]), p.expr)

    @_('EMPTY')
    def variable_definition(self, p):
        return VariableDefinitionNode(p[-3], IdNode(p[-2]), ValueNode(None))

    @_('expr ";"')
    def statement(self, p):
        return ExpressionNode(p.expr)

    @_('PRINTF "(" argument_list ")" ";"')
    def statement(self, p):
        return PrintfNode(ValueNode(p.argument_list))

    @_('SCANF "(" argument_list ")" ";"')
    def statement(self, p):
        return ScanfNode(ValueNode(p.argument_list))

    @_('RETURN expr ";"')
    def statement(self, p):
        return ReturnNode(p.expr)

    #selection_statement
    #  -> IF '(' expr ')' code_block else_statement
    @_('IF "(" expr ")" code_block else_statement')
    def selection_statement(self,p):
        return SelectionStatementNode(p.expr, p.code_block, p.else_statement) 

    # else_statement
    #  -> ELSE code_block
    #   | ε

    @_('ELSE code_block')
    def else_statement(self,p):
        return p.code_block

    # Para incluir las precedencias en el sistema, es necesario que la regla tenga
    # al menos un token. Como esta no lo tenía (else_statement --> ε), se añade %prec
    @_('%prec EMPTY')
    def else_statement(self,p):
        return Node()

    # code_block 
    #  -> '{' statement_list '}'
    #   | statement

    @_('"{" statement_list "}" ')
    def code_block(self,p):
        return p.statement_list

    @_('statement')
    def code_block(self,p):
        return StatementNode(p.statement, Node())

    # statement_list
    #  -> statement statement_list
    #   | ε

    @_('statement statement_list')
    def statement_list(self, p):
        return StatementNode(p.statement, p.statement_list)

    @_('EMPTY')
    def statement_list(self, p):
        return Node()

    # expr
    #  -> ID '=' expr
    #   | logical_or_expr

    @_('ID "=" expr')
    def expr(self, p):
        return AssignBinaryOpNode(IdNode(p.ID), p.expr)

    @_('logical_or_expr')
    def expr(self, p):
        return p.logical_or_expr

    # logical_or_expr
    #  -> logical_or_expr OR_OP logical_and_expr
    #   | logical_and_expr

    @_('logical_or_expr OR_OP logical_and_expr')
    def logical_or_expr(self, p):
        return OrBinaryOpNode(p.logical_or_expr, p.logical_and_expr)

    @_('logical_and_expr')
    def logical_or_expr(self, p):
        return p.logical_and_expr

    # logical_and_expr
    #  -> logical_and_expr AND_OP equality_expr
    #   | equality_expr

    @_('logical_and_expr AND_OP equality_expr')
    def logical_and_expr(self, p):
        return AndBinaryOpNode(p.logical_and_expr, p.equality_expr)

    @_('equality_expr')
    def logical_and_expr(self, p):
        return p.equality_expr

    # equality_expr
    #  -> equality_expr EQ_OP relational_expr
    #   | equality_expr NE_OP relational_expr
    #   | relational_expr

    @_('equality_expr EQ_OP relational_expr')
    def equality_expr(self, p):
        return EqualBinaryOpNode(p.equality_expr, p.relational_expr)
    
    @_('equality_expr NE_OP relational_expr')
    def equality_expr(self, p):
        return NotEqualBinaryOpNode(p.equality_expr, p.relational_expr)

    @_('relational_expr')
    def equality_expr(self, p):
        return p.relational_expr
    
    # relational_expr
    #  -> relational_expr '<' additive_expr
    #   | relational_expr '>' additive_expr
    #   | relational_expr GE_OP additive_expr
    #   | relational_expr LE_OP additive_expr
    #   | additive_expr
    
    @_('relational_expr "<" additive_expr')
    def relational_expr(self, p):
        return LessBinaryOpNode(p.relational_expr, p.additive_expr)

    @_('relational_expr ">" additive_expr')
    def relational_expr(self, p):
        return GreaterBinaryOpNode(p.relational_expr, p.additive_expr)

    @_('relational_expr GE_OP additive_expr')
    def relational_expr(self, p):
        return GreaterEqualBinaryOpNode(p.relational_expr, p.additive_expr)

    @_('relational_expr LE_OP additive_expr')
    def relational_expr(self, p):
        return LessEqualBinaryOpNode(p.relational_expr, p.additive_expr)

    @_('additive_expr')
    def relational_expr(self, p):
        return p.additive_expr

    # additive_expr
    #  -> additive_expr '+' multiplicative_expr
    #   | additive_expr '-' multiplicative_expr
    #   | multiplicative_expr

    @_('additive_expr "+" multiplicative_expr')
    def additive_expr(self, p):
        return AddBinaryOpNode(p.additive_expr, p.multiplicative_expr)

    @_('additive_expr "-" multiplicative_expr')
    def additive_expr(self, p):
        return SubtractBinaryOpNode(p.additive_expr, p.multiplicative_expr)

    @_('multiplicative_expr')
    def additive_expr(self, p):
        return p.multiplicative_expr

    # multiplicative_expr
    #  -> multiplicative_expr '*' unary_expr
    #   | multiplicative_expr '/' unary_expr
    #   | unary_expr

    @_('multiplicative_expr "*" unary_expr')
    def multiplicative_expr(self, p):
        return MultiplyBinaryOpNode(p.multiplicative_expr, p.unary_expr)

    @_('multiplicative_expr "/" unary_expr')
    def multiplicative_expr(self, p):
        return DivideBinaryOpNode(p.multiplicative_expr, p.unary_expr)

    @_('unary_expr')
    def multiplicative_expr(self, p):
        return p.unary_expr

    # unary_expr
    #  -> '-' unary_expr
    #   | '+' unary_expr
    #   | '!' unary_expr
    #   | '&' value
    #   | value

    @_('"-" unary_expr')
    def unary_expr(self, p):
        return NegationUnaryOpNode(p.unary_expr)

    @_('"+" unary_expr')
    def unary_expr(self, p):
        return PlusUnaryOpNode(p.unary_expr)

    @_('"!" unary_expr')
    def unary_expr(self, p):
        return NotUnaryOpNode(p.unary_expr)

    @_('"&" value')
    def unary_expr(self, p):
        return IdNode(p.value.get_id())

    @_('value')
    def unary_expr(self, p):
        return p.value

    # value
    #  -> ID
    #   | INT
    #   | FLOAT
    #   | STRING
    #   | '(' expr ')'

    @_('ID')
    def value(self, p):
        return IdValueNode(p.ID)

    @_('INT')
    def value(self, p):
        return ValueNode(p.INT)

    @_('FLOAT')
    def value(self, p):
        return ValueNode(p.FLOAT)

    @_('STRING')
    def value(self, p):
        return ValueNode(p.STRING)

    @_('"(" expr ")"')
    def value(self, p):
        return p.expr

    @_('ID "(" argument_list ")"')
    def value(self, p):
        return FunctionCallNode(IdNode(p.ID), ValueNode(p.argument_list))

    # argument_list
    #  -> argument_list_aux
    #   | ε
    @_('argument_list_aux')
    def argument_list(self, p):
        return p.argument_list_aux

    @_('EMPTY')
    def argument_list(self, p):
        return list()

    # argument_list_aux
    #  -> argument_list_aux ',' expr
    #   | expr
    @_('argument_list_aux "," expr')
    def argument_list_aux(self, p):
        return p.argument_list_aux + list([p.expr])

    @_('expr')
    def argument_list_aux(self, p):
        return list([p.expr])

    @_('')
    def EMPTY(self, p):
        pass