from sly import Lexer

class AnalizadorLexico(Lexer):
    tokens = {ID, FLOAT, INT, LE_OP, GE_OP, NE_OP, EQ_OP, AND_OP, OR_OP,IF,ELSE,STRING,PRINTF,
            SCANF, MAIN, RETURN, WHILE, TYPE}
    literals = {'=', '+', '-', '*', '/', '!', ';', '<', '>', '(', ')', '.','{','}', ',', '&'}

    ignore = ' \t'
    ignore_newline = r'\n+'
    ignore_comment = r'//.*'


    # Identifiers and keywords
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['if'] = IF
    ID['else'] = ELSE
    ID['printf'] = PRINTF
    ID['scanf'] = SCANF
    ID['main'] = MAIN
    ID['return'] = RETURN
    ID['while'] = WHILE
    ID['int'] = TYPE    # solo se soporta el tipo int
    ID['void'] = TYPE
    
    # CONST = r'[0-9]+(\.[0-9]*)?'
    FLOAT = r'[0-9]+\.[0-9]+' 
    INT = r'[0-9]+'
    STRING = r'(?P<prefix>(?:\bu8|\b[LuU])?)(?:"(?P<dbl>[^"\\]*(?:\\.[^"\\]*)*)"|\'(?P<sngl>[^\'\\]*(?:\\.[^\'\\]*)*)\')|R"([^"(]*)\((?P<raw>.*?)\)\4"'

    LE_OP = r'<='
    GE_OP = r'>='
    NE_OP = r'!='
    EQ_OP = r'=='
    AND_OP = r'&&'
    OR_OP = r'\|\|'

    def INT(self, token):
        token.value = int(token.value)
        return token

    def FLOAT(self, token):
        token.value = float(token.value)
        return token

    def STRING(self, token):
        token.value = token.value.replace("\\n", "\n")
        token.value = token.value.replace("\"", "")
        return token

    def ignore_newline(self, t):
        self.lineno += len(t.value)

