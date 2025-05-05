import re
import tkinter as tk

class Parser:
    def __init__(self, input_str):
        """Inicializa el analizador con la cadena de entrada y genera la lista de tokens."""
        self.input = input_str
        self.tokens = self.tokenize(input_str)
        self.current = 0
        self.token = self.tokens[self.current]

    def tokenize(self, s):
        """Analizador léxico: divide la entrada en tokens (identificadores, números, operadores y paréntesis)."""
        token_spec = [
            ('NUMBER', r'\d+'),              # Números (más de un dígito)
            ('ID',     r'[a-zA-Z_]\w*'),      # Identificadores
            ('PLUS',   r'\+'),
            ('MINUS',  r'-'),
            ('MULT',   r'\*'),
            ('DIV',    r'/'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('SKIP',   r'[ \t]+'),            # Espacios y tabulaciones (se omiten)
            ('MISMATCH', r'.')                # Cualquier otro carácter (error)
        ]
        regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
        tokens = []
        for mo in re.finditer(regex, s):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                self.error(f"Token inesperado: {value}")
            else:
                tokens.append((kind, value))
        # Token explícito de fin de entrada
        tokens.append(('EOF', None))
        return tokens

    def error(self, msg="Error de sintaxis"):
        """Muestra un mensaje de error y termina la ejecución."""
        raise Exception(msg)

    def advance(self):
        """Avanza al siguiente token."""
        self.current += 1
        if self.current < len(self.tokens):
            self.token = self.tokens[self.current]
        else:
            self.token = ('EOF', None)

    def match(self, expected):
        """Consume el token actual si coincide con el esperado; de lo contrario, reporta error."""
        if self.token[0] == expected:
            self.advance()
        else:
            self.error(f"Se esperaba '{expected}', se encontró {self.token}")

    # E  → T E'
    def parse_E(self):
        result = self.parse_T()
        return self.parse_E_prime(result)

    # E' → + T E' | - T E' | ε
    def parse_E_prime(self, inherited):
        while self.token[0] in ('PLUS', 'MINUS'):
            op = self.token[1]
            self.advance()
            right = self.parse_T()
            inherited = f"{inherited} {right} {op}"
        # FOLLOW(E') = { RPAREN, EOF }
        if self.token[0] not in ('RPAREN', 'EOF'):
            self.error(f"Se esperaba ')' o fin de entrada, se encontró {self.token}")
        return inherited

    # T  → F T'
    def parse_T(self):
        result = self.parse_F()
        return self.parse_T_prime(result)

    # T' → * F T' | / F T' | ε
    def parse_T_prime(self, inherited):
        while self.token[0] in ('MULT', 'DIV'):
            op = self.token[1]
            self.advance()
            right = self.parse_F()
            inherited = f"{inherited} {right} {op}"
        # FOLLOW(T') = { PLUS, MINUS, RPAREN, EOF }
        if self.token[0] not in ('PLUS', 'MINUS', 'RPAREN', 'EOF'):
            self.error(f"Se esperaba operador aritmético, ')' o fin de entrada, se encontró {self.token}")
        return inherited

    # F  → ( E ) | id | num
    def parse_F(self):
        if self.token[0] == 'LPAREN':
            self.advance()
            result = self.parse_E()
            self.match('RPAREN')
            return result
        elif self.token[0] == 'ID':
            id_val = self.token[1]
            self.advance()
            return id_val
        elif self.token[0] == 'NUMBER':
            num_val = self.token[1]
            self.advance()
            return num_val
        else:
            self.error("Se esperaba identificador, número o '('")

    def parse(self):
        """Inicia el análisis y verifica fin de entrada."""
        result = self.parse_E()
        if self.token[0] != 'EOF':
            self.error(f"Entrada extra no válida tras la expresión: {self.token}")
        return result


def parse_expression(expr_str):
    parser = Parser(expr_str)
    return parser.parse()

# --- Interfaz gráfica con Tkinter ---

def convert_expression():
    expr = entry.get()
    try:
        result = parse_expression(expr)
        label_result.config(text="Notación postfija: " + result)
    except Exception as e:
        label_result.config(text="Error: " + str(e))

root = tk.Tk()
root.title("Analizador Descendente Predictivo - Notación Postfija")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="Introduce una expresión aritmética:").pack(pady=5)
entry = tk.Entry(frame, width=40)
entry.pack(pady=5)

button = tk.Button(frame, text="Convertir a postfijo", command=convert_expression)
button.pack(pady=5)

label_result = tk.Label(frame, text="Notación postfija: ")
label_result.pack(pady=5)

root.mainloop()
