import tkinter as tk
from tkinter import filedialog, messagebox

# Definición de los tipos de tokens
INTEGER, ID, PLUS, MINUS, TIMES, DIVIDE, LPAREN, RPAREN, ASSIGN, SEMICOLON, EOF = (
    'INTEGER', 'ID', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'ASSIGN', 'SEMICOLON', 'EOF'
)

# Palabras reservadas y tipos C++ mapeados a VAR
RESERVED_KEYWORDS = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'var': 'VAR',
    'int': 'VAR',       # Soporta declaraciones estilo C++
    'float': 'VAR',     # Otros tipos básicos
    'double': 'VAR'
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
        self.symbols = set()
        self.temp_count = 0
        self.code = []

    def new_temp(self):
        name = f't{self.temp_count}'
        self.temp_count += 1
        return name

    def emit(self, op, arg1, arg2, res):
        self.code.append((op, arg1, arg2, res))

    def error(self, msg="Error de sintaxis"):
        raise Exception(msg + f" en token {self.current_token}")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Se esperaba token {token_type}")

    def program(self):
        self.statement_list()
        if self.current_token.type != EOF:
            self.error("Se esperaba fin de archivo")

    def statement_list(self):
        while self.current_token.type in (ID, 'VAR'):
            self.statement()

    def statement(self):
        if self.current_token.type == 'VAR':
            self.eat('VAR')
            var_name = self.current_token.value
            self.eat(ID)
            if self.current_token.type == ASSIGN:
                self.eat(ASSIGN)
                place = self.expr()
                self.emit('=', place, None, var_name)
            self.eat(SEMICOLON)
            self.symbols.add(var_name)
        else:
            var_name = self.current_token.value
            if var_name not in self.symbols:
                self.error(f"Variable '{var_name}' no declarada")
            self.eat(ID)
            self.eat(ASSIGN)
            place = self.expr()
            self.emit('=', place, None, var_name)
            self.eat(SEMICOLON)

    def expr(self):
        left = self.term()
        while self.current_token.type in (PLUS, MINUS):
            op = self.current_token.value
            self.eat(self.current_token.type)
            right = self.term()
            temp = self.new_temp()
            self.emit(op, left, right, temp)
            left = temp
        return left

    def term(self):
        left = self.factor()
        while self.current_token.type in (TIMES, DIVIDE):
            op = self.current_token.value
            self.eat(self.current_token.type)
            right = self.factor()
            temp = self.new_temp()
            self.emit(op, left, right, temp)
            left = temp
        return left

    def factor(self):
        if self.current_token.type == LPAREN:
            self.eat(LPAREN)
            place = self.expr()
            self.eat(RPAREN)
            return place
        elif self.current_token.type == INTEGER:
            value = self.current_token.value
            temp = self.new_temp()
            self.emit('=', value, None, temp)
            self.eat(INTEGER)
            return temp
        elif self.current_token.type == ID:
            name = self.current_token.value
            if name not in self.symbols:
                raise Exception(f"Variable '{name}' no declarada en token {self.current_token}")
            self.eat(ID)
            return name
        else:
            self.error("Se esperaba '(', número o identificador")

# Generación de TAC

def parse_and_generate(source_code):
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    parser.program()
    return parser.code

# GUI
root = tk.Tk()
root.title("Generador de Código de 3 Direcciones")
frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# Abrir archivo

def open_file():
    filepath = filedialog.askopenfilename(
        title="Selecciona el archivo fuente",
        filetypes=[("Archivos C/C++", "*.cpp;*.h;*.c"), ("Todos los archivos", "*.*")]
    )
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, text)

button_open = tk.Button(frame, text="Abrir archivo fuente", command=open_file)
button_open.pack(pady=5)
text_area = tk.Text(frame, width=60, height=15)
text_area.pack(pady=5)

# Botón de análisis y exportación

def generate_and_save_tac():
    source = text_area.get("1.0", tk.END)
    try:
        tac = parse_and_generate(source)
        lines = [f"{i}: {res} = {a1} {op} {a2}" if a2 is not None else f"{i}: {res} = {a1}"
                 for i, (op, a1, a2, res) in enumerate(tac)]
        content = "\n".join(lines)
        # Mostrar en la interfaz
        label_result.config(text=content)
        # Guardar en archivo
        save_path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Archivo de texto', '*.txt')],
            title='Guardar código de 3 direcciones como'
        )
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as out:
                out.write(content)
            messagebox.showinfo('Éxito', f'Archivo guardado en:\n{save_path}')
    except Exception as e:
        messagebox.showerror('Error', str(e))

button_analyze = tk.Button(frame, text="Generar y guardar 3-direcciones", command=generate_and_save_tac)
button_analyze.pack(pady=5)
label_result = tk.Label(frame, text="Resultado:")
label_result.pack(pady=5)

root.mainloop()