import tkinter as tk
from tkinter import filedialog

# Definición de los tipos de tokens
INTEGER, ID, PLUS, MINUS, TIMES, DIVIDE, LPAREN, RPAREN, ASSIGN, SEMICOLON, EOF = (
    'INTEGER', 'ID', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'ASSIGN', 'SEMICOLON', 'EOF'
)

# Palabras reservadas
RESERVED_KEYWORDS = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'var': 'VAR'
}

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'
    def __repr__(self):
        return self.__str__()

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[self.pos] if text else None

    def error(self):
        raise Exception(f'Error léxico en la posición {self.pos}')

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()

    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        token_type = RESERVED_KEYWORDS.get(result, ID)
        return Token(token_type, result)

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace(); continue
            if self.current_char == '#':
                self.skip_comment(); continue
            if self.current_char.isalpha():
                return self.identifier()
            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())
            if self.current_char == '+': self.advance(); return Token(PLUS, '+')
            if self.current_char == '-': self.advance(); return Token(MINUS, '-')
            if self.current_char == '*': self.advance(); return Token(TIMES, '*')
            if self.current_char == '/': self.advance(); return Token(DIVIDE, '/')
            if self.current_char == '(': self.advance(); return Token(LPAREN, '(')
            if self.current_char == ')': self.advance(); return Token(RPAREN, ')')
            if self.current_char == '=': self.advance(); return Token(ASSIGN, '=')
            if self.current_char == ';': self.advance(); return Token(SEMICOLON, ';')
            self.error()
        return Token(EOF, None)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
        self.symbols = set()  # tabla de símbolos

    def error(self, msg="Error de sintaxis"):
        raise Exception(msg + f" en token {self.current_token}")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Se esperaba token {token_type}")

    # Programa → ListaDeSentencias EOF
    def program(self):
        self.statement_list()
        if self.current_token.type != EOF:
            self.error("Se esperaba fin de archivo")

    # ListaDeSentencias → Sentencia ListaDeSentencias | ε
    def statement_list(self):
        while self.current_token.type in (ID, 'VAR'):
            self.statement()

    # Sentencia → VAR ID (= Expr)? ;  | ID = Expr ;
    def statement(self):
        # Declaración con var
        if self.current_token.type == 'VAR':
            self.eat('VAR')
            var_name = self.current_token.value
            self.eat(ID)
            # opcional inicializador
            if self.current_token.type == ASSIGN:
                self.eat(ASSIGN)
                self.expr()
            self.eat(SEMICOLON)
            self.symbols.add(var_name)
        else:
            # Asignación a variable existente
            var_name = self.current_token.value
            if var_name not in self.symbols:
                self.error(f"Variable '{var_name}' no declarada")
            self.eat(ID)
            self.eat(ASSIGN)
            self.expr()
            self.eat(SEMICOLON)
            # ya estaba declarada, no volvemos a agregar

    # Expr → Term ExprRest
    def expr(self):
        self.term()
        self.expr_rest()

    def expr_rest(self):
        while self.current_token.type in (PLUS, MINUS):
            self.eat(self.current_token.type)
            self.term()

    # Term → Factor TermRest
    def term(self):
        self.factor()
        self.term_rest()

    def term_rest(self):
        while self.current_token.type in (TIMES, DIVIDE):
            self.eat(self.current_token.type)
            self.factor()

    # Factor → ( Expr ) | INTEGER | ID
    def factor(self):
        if self.current_token.type == LPAREN:
            self.eat(LPAREN)
            self.expr()
            self.eat(RPAREN)
        elif self.current_token.type == INTEGER:
            self.eat(INTEGER)
        elif self.current_token.type == ID:
            name = self.current_token.value
            if name not in self.symbols:
                raise Exception(f"Variable '{name}' no declarada en token {self.current_token}")
            self.eat(ID)
        else:
            self.error("Se esperaba '(', número o identificador")

# Función para parsear el código fuente
def parse_source(source_code):
    try:
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        parser.program()
        return "Programa válido."
    except Exception as e:
        return f"Error: {e}"

# Interfaz gráfica con Tkinter
def open_file():
    filepath = filedialog.askopenfilename(
        title="Selecciona el archivo fuente",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
    )
    if filepath:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, content)

root = tk.Tk()
root.title("Analizador Sintáctico Descendente")
frame = tk.Frame(root, padx=10, pady=10)
frame.pack()
button_open = tk.Button(frame, text="Abrir archivo fuente", command=open_file)
button_open.pack(pady=5)
text_area = tk.Text(frame, width=80, height=20)
text_area.pack(pady=5)
button_analyze = tk.Button(frame, text="Analizar programa", command=lambda: label_result.config(text=parse_source(text_area.get("1.0", tk.END))))
button_analyze.pack(pady=5)
label_result = tk.Label(frame, text="Resultado del análisis:")
label_result.pack(pady=5)
root.mainloop()