import re
import tkinter as tk

class Token:
    def __init__(self, type_, value=None):
        self.type = type_  # Define el tipo del token
        self.value = value  # Valor para números

    def __repr__(self):
        return f"Token({self.type}, {self.value})"  # Representación del token

def lexer(text):
    token_specification = [
        ('INT',    r'\d+'),    # Números enteros
        ('PLUS',   r'\+'),     # Suma
        ('MINUS',  r'-'),      # Resta
        ('MUL',    r'\*'),     # Multiplicación
        ('DIV',    r'/'),      # División
        ('LPAREN', r'\('),     # Paréntesis abierto
        ('RPAREN', r'\)'),     # Paréntesis cerrado
        ('SKIP',   r'[ \t]+'), # Espacios
        ('MISMATCH', r'.'),    # Carácter no permitido
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)  # Une patrones
    get_token = re.compile(tok_regex).match  # Compila el regex
    tokens = []  # Lista de tokens
    pos = 0
    mo = get_token(text, pos)
    while mo is not None:
        typ = mo.lastgroup  # Tipo de token encontrado
        if typ == 'INT':
            val = mo.group(typ)
            tokens.append(Token('INT', int(val)))  # Agrega número entero
        elif typ == 'PLUS':
            tokens.append(Token('PLUS'))  # Agrega +
        elif typ == 'MINUS':
            tokens.append(Token('MINUS'))  # Agrega -
        elif typ == 'MUL':
            tokens.append(Token('MUL'))  # Agrega *
        elif typ == 'DIV':
            tokens.append(Token('DIV'))  # Agrega /
        elif typ == 'LPAREN':
            tokens.append(Token('LPAREN'))  # Agrega (
        elif typ == 'RPAREN':
            tokens.append(Token('RPAREN'))  # Agrega )
        elif typ == 'SKIP':
            pass  # Ignora espacios
        elif typ == 'MISMATCH':
            raise ValueError(f"Carácter ilegal: '{mo.group(typ)}' en la posición {pos}")  # Error
        pos = mo.end()  # Avanza posición
        mo = get_token(text, pos)
    tokens.append(Token('$'))  # Agrega fin de entrada
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # Lista de tokens
        self.pos = 0  # Posición actual
        self.current_token = self.tokens[self.pos]  # Token actual

    def error(self, message="Error de sintaxis"):
        raise SyntaxError(message)  # Lanza error

    def advance(self):
        self.pos += 1  # Avanza a siguiente token
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token('$')  # Fin de entrada

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.advance()  # Consume token
        else:
            self.error(f"Se esperaba '{token_type}', se encontró '{self.current_token.type}'.")  # Error

    def parse(self):
        self.E()  # Inicia con la regla E
        if self.current_token.type != '$':
            self.error("Fin de la expresión esperado.")  # Error

    # E -> T E'
    def E(self):
        self.T()  
        self.Ep()

    # E' -> + T E' | - T E' | ε
    def Ep(self):
        if self.current_token.type == 'PLUS':
            self.eat('PLUS')  # Consume +
            self.T()  # E' -> + T E'
            self.Ep()
        elif self.current_token.type == 'MINUS':
            self.eat('MINUS')  # Consume -
            self.T()  # E' -> - T E'
            self.Ep()
        else:
            pass  # Epsilon

    # T -> F T'
    def T(self):
        self.F()  
        self.Tp()

    # T' -> * F T' | / F T' | ε
    def Tp(self):
        if self.current_token.type == 'MUL':
            self.eat('MUL')  # Consume *
            self.F()  # T' -> * F T'
            self.Tp()
        elif self.current_token.type == 'DIV':
            self.eat('DIV')  # Consume /
            self.F()  # T' -> / F T'
            self.Tp()
        else:
            pass  # Epsilon

    # F -> (E) | INT
    def F(self):
        if self.current_token.type == 'LPAREN':
            self.eat('LPAREN')  # Consume (
            self.E()  # F -> (E)
            self.eat('RPAREN')  # Consume )
        elif self.current_token.type == 'INT':
            self.eat('INT')  # Consume número
        else:
            self.error(f"Se esperaba número o '(', se encontró '{self.current_token.type}'.")  # Error

def parse_input():
    expression = entry.get()  # Obtiene la expresión
    try:
        tokens = lexer(expression)  # Tokeniza
        parser = Parser(tokens)  # Crea parser
        parser.parse()  # Analiza sintácticamente
        result_label.config(text="La expresión es válida.", fg="green")  # Muestra éxito
    except (SyntaxError, ValueError) as e:
        result_label.config(text=f"Error: {e}", fg="red")  # Muestra error

root = tk.Tk()  # Crea ventana principal
root.title("Analizador Sintáctico Predictivo")

label = tk.Label(root, text="Ingresa una expresión:")  # Etiqueta de entrada
label.pack(pady=5)

entry = tk.Entry(root, width=40)  # Caja de texto
entry.pack(pady=5)

button = tk.Button(root, text="Analizar", command=parse_input)  # Botón de análisis
button.pack(pady=5)

result_label = tk.Label(root, text="", font=("Helvetica", 12))  # Etiqueta de resultado
result_label.pack(pady=10)

root.mainloop()  # Inicia la interfaz
