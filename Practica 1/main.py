def lexer(input_string):
    """
    Convierte la cadena de entrada en una lista de tokens (en este caso, dígitos y el símbolo '$').
    """
    tokens = []
    for char in input_string:
        if char.isdigit():
            tokens.append(char)       # El token es el dígito
        elif char.isspace():
            continue                  # Ignoramos espacios
        else:
            # Cualquier otro carácter se considera inválido en este ejemplo
            raise ValueError(f"Carácter inválido en la entrada: {char}")
    tokens.append('$')  # Agregamos fin de entrada
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]

    def advance(self):
        """
        Avanza al siguiente token de la lista. Si se acaba la lista, self.current_token se vuelve None.
        """
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None

    def parse(self):
        """
        Función principal que inicia el análisis sintáctico.
        Llama a la regla inicial de la gramática: Lista().
        """
        self.Lista()
        # Al terminar, comprobamos que el token actual sea el fin de entrada '$'
        if self.current_token != '$':
            raise SyntaxError("Se esperaban más dígitos o fin de cadena.")
        print("La cadena es válida.")

    # -------------------------------------------------------------------------
    # A partir de aquí definimos una función por cada no terminal de la gramática
    # tal como se ve en tu ejemplo (Lista, Resto_Lista, dígito).
    # -------------------------------------------------------------------------

    def Lista(self):
        """
        Lista -> dígito Resto_Lista
        Según tu imagen y la gramática:
           def Lista():
               if premalink == '0..9':
                   Resto_Lista()
               else:
                   ...
        Aquí en Python, en vez de 'premalink' usamos self.current_token.
        """
        # Checamos si es un dígito
        if self.current_token in ['0','1','2','3','4','5','6','7','8','9']:
            self.digito()       # Consumimos el dígito
            self.Resto_Lista()  # Llamamos a la siguiente parte de la producción
        else:
            # Si no hay dígito, es un error sintáctico
            raise SyntaxError(f"Se esperaba un dígito, se encontró '{self.current_token}'")

    def Resto_Lista(self):
        """
        Resto_Lista -> ε | dígito Resto_Lista
        En la imagen, se ve algo como:
           def Resto_Lista():
               if premalink == '0..9':
                   Resto_Lista()
               else:
                   ...
        Pero la idea es la misma: o es un dígito (y repetimos) o es epsilon (fin de la lista).
        """
        if self.current_token in ['0','1','2','3','4','5','6','7','8','9']:
            self.digito()       # Consumimos el dígito
            self.Resto_Lista()  # Repetimos
        else:
            # Caso ε (epsilon): no hacemos nada y regresamos
            return

    def digito(self):
        """
        dígito -> 0 | 1 | 2 | ... | 9
        En tu imagen hay una función dígito() que comprueba si el token es un dígito.
        """
        if self.current_token in ['0','1','2','3','4','5','6','7','8','9']:
            self.advance()  # Consumimos el token y avanzamos
        else:
            # Si no es un dígito, hay error
            raise SyntaxError(f"Se esperaba un dígito, se encontró '{self.current_token}'")


def main():
    # Ejemplos de prueba
    ejemplos = [
        "12345",
        "0",
        "909090",
        "",
        "12a3"  # Este debe marcar error léxico
    ]

    for ejemplo in ejemplos:
        print(f"Probando la cadena: '{ejemplo}'")
        try:
            tokens = lexer(ejemplo)
            parser = Parser(tokens)
            parser.parse()
        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
        print()

if __name__ == "__main__":
    main()