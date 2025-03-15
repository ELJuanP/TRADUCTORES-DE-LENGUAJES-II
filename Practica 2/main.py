import tkinter as tk

class Parser:
    def __init__(self, input_str):
        self.input = input_str
        self.pos = 0
        self.current_char = self.input[self.pos] if self.input else None

    def error(self, msg="Error de sintaxis"):
        raise Exception(msg)

    def advance(self):
        """Avanza un caracter en la entrada."""
        self.pos += 1
        if self.pos < len(self.input):
            self.current_char = self.input[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self):
        """Salta los espacios en blanco."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """Reconoce un número (varios dígitos)."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return result

    def factor(self):
        """F -> (E) | número"""
        self.skip_whitespace()
        if self.current_char == '(':
            self.advance()  # consumir '('
            result = self.expr()
            self.skip_whitespace()
            if self.current_char == ')':
                self.advance()  # consumir ')'
                return result
            else:
                self.error("Se esperaba ')'")
        elif self.current_char is not None and self.current_char.isdigit():
            num = self.number()
            return num
        else:
            self.error("Error en factor: se esperaba un número o '('")

    def term(self):
        """T -> F { (* | /) F }"""
        self.skip_whitespace()
        result = self.factor()
        while self.current_char is not None and self.current_char in ('*', '/'):
            op = self.current_char
            self.advance()  # consumir el operador
            right = self.factor()
            # Se genera notación postfija: operandos primero y operador al final
            result = result + " " + right + " " + op
        return result

    def expr(self):
        """E -> T { (+ | -) T }"""
        self.skip_whitespace()
        result = self.term()
        while self.current_char is not None and self.current_char in ('+', '-'):
            op = self.current_char
            self.advance()  # consumir el operador
            right = self.term()
            result = result + " " + right + " " + op
        return result

def parse_expression(expression):
    """Función para parsear la expresión y obtener su forma postfija."""
    parser = Parser(expression)
    try:
        postfix = parser.expr()
        parser.skip_whitespace()
        if parser.current_char is not None:
            raise Exception("Entrada extra no válida")
        return postfix
    except Exception as e:
        return "Error: " + str(e)

# Interfaz de usuario usando Tkinter
def convert_expression():
    expr = entry.get()
    result = parse_expression(expr)
    label_result.config(text="Notación postfija: " + result)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Analizador Descendente - Notación Postfija")

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