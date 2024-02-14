import re, json, sys
from collections import namedtuple

TOKEN_DEFINITIONS = {
    'INTEGER': r'\d+(_\d+)*',
    'ATOM': r':[a-zA-Z_][a-zA-Z0-9_]*',
    'COMMA': r',',
    'COLON': r':',
    'KEY': r'[a-zA-Z_][a-zA-Z0-9_]*:',
    'VALUE': r'''(['"])(.?)\d+(_\d+)\1''',
    'BOOLEAN': r'\b(true|false)\b',
    'LEFT_SQUARE_BRACKET': r'\[',
    'RIGHT_SQUARE_BRACKET': r'\]',
    'LEFT_CURLY_BRACE': r'\{',
    'RIGHT_CURLY_BRACE': r'\}',
    'PERCENTAGE_LEFT_CURLY_BRACE': r'%\{',
    'RIGHT_ARROW': r'=>',
    'UNDERSCORE': r'_',
    'EMPTY_SPACE': r'[ \t]+',
    'EOF': r'<EOF>'
}


def parse(toks):
    def peek():
        if toks:
            return toks[0][0]
        return None

    def consume():
        if toks:
            return toks.pop(0)
        return None
    
    def check_token(token_kind):
        if toks and peek() == token_kind:
            return consume()
        return None

    def literal():
        try: 
            token = check_token('LEFT_SQUARE_BRACKET')
            if token:
                return parse_list_literal()
            token = check_token('LEFT_CURLY_BRACE')
            if token:
                return parse_tuple_literal()
            token = check_token('PERCENTAGE_LEFT_CURLY_BRACE')
            if token:
                return parse_map_literal()
            token = check_token('COLON')
            if token:
                return check_token('COLON')
            token = check_token('RIGHT_ARROW')
            if token:
                return check_token('RIGHT_ARROW')
            token = check_token('ATOM')
            if token:
                return AtomElement(token[1])
            token = check_token('KEY')
            if token:
                return KeyElement(token[1])
            token = check_token('VALUE')
            if token:
                return ValueElement(token[1])
            token = check_token('EOF')
            if token:
                return check_token('EOF')
            token = check_token('INTEGER')
            if token:
                return IntegerElement(token[1])
            token = check_token('BOOLEAN')
            if token:
                return BooleanElement(token[1])
            raise ValueError(f"Unexpected token: {toks[0]}")
        except:
            print("Unexpected token error")
            sys.exit(1)

    def sentence():
        literals = []
        while toks and any([True for token_kind in TOKEN_DEFINITIONS.keys() if peek() == token_kind]):
            literals.append(literal())
        return SentenceElement(literals)
    
    def parse_list_literal():
        literals = []
        check_token('LEFT_SQUARE_BRACKET')
        while toks and peek() != 'RIGHT_SQUARE_BRACKET':
            # print(toks)
            literals.append(literal())
            if toks and peek() == 'COMMA':
                check_token('COMMA')
                if(peek() == 'RIGHT_SQUARE_BRACKET'):
                    sys.exit(1)
        if(check_token('RIGHT_SQUARE_BRACKET') == None):
            sys.exit(1)
        return ListLiteralElement(literals)

    def parse_tuple_literal():
        literals = []
        check_token('LEFT_CURLY_BRACE')
        while toks and peek() != 'RIGHT_CURLY_BRACE':
            literals.append(literal())
            if toks and peek() == 'COMMA':
                check_token('COMMA')
                if(peek() == 'RIGHT_CURLY_BRACE'):
                    sys.exit(1)
        if(check_token('RIGHT_CURLY_BRACE')==None):
            sys.exit(1)
        return TupleLiteralElement(literals)

    def parse_map_literal():
        key_pairs = []
        check_token('PERCENTAGE_LEFT_CURLY_BRACE')
        while toks and peek() != 'RIGHT_CURLY_BRACE':
            key_pairs.append(parse_key_pair())
            if toks and peek() == 'COMMA':
                check_token('COMMA')
                if(peek() == 'RIGHT_CURLY_BRACE'):
                    sys.exit(1)
        if(check_token('RIGHT_CURLY_BRACE') == None):
            sys.exit(1)
        return MapLiteralElement(key_pairs)

    def parse_key_pair():
        try: 
            key = literal()
            if toks and peek() == 'RIGHT_ARROW':
                check_token('RIGHT_ARROW')
                value = literal()
                return KeyPairElement(key, value)
            elif toks and peek() == 'COLON':
                check_token('COLON')
                value = literal()
                return KeyPairElement(key, value)
            elif toks:
                value = literal()
                return KeyPairElement(key, value)
            else:
                raise ValueError(f"Invalid key-pair: {toks[0]}")
        except:
            print("Invalid key-pair")
            sys.exit(1)

    root_node = LanguageElement(sentence())
    return root_node

class Element:
    def as_json(self):
        return {}

class LanguageElement(Element):
    def __init__(self, text):
        self.text = text
        
    def as_json(self):
        return self.text.as_json()

class SentenceElement(Element):
    def __init__(self, literals):
        self.literals = literals

    def as_json(self):
        return [data_literal.as_json() for data_literal in self.literals if data_literal]
    

class DataLiteralElement(Element):
    def __init__(self, value):
        self.value = value

    def as_json(self):
        return {"DataLiteral": self.value}
        
class KeyElement(DataLiteralElement):
    def __init__(self, key):
        self.key = key

    def as_json(self):
        return self.key
        
class ValueElement(DataLiteralElement):
    def __init__(self, value):
        self.value = value

    def as_json(self):
        return self.value

class ListLiteralElement(DataLiteralElement):
    def __init__(self, literals):
        self.literals = literals

    def as_json(self):
        return {"%k":"list", "%v": [data_literal.as_json() for data_literal in self.literals if data_literal]}
    

class TupleLiteralElement(DataLiteralElement):
    def __init__(self, literals):
        self.literals = literals
        
    def as_json(self):
        return {"%k":"tuple", "%v": [data_literal.as_json() for data_literal in self.literals if data_literal]}
    

class MapLiteralElement(DataLiteralElement):
    def __init__(self, key_pairs):
        self.key_pairs = key_pairs

    def as_json(self):
        return {"%k":"map", "%v": [key_pair.as_json() for key_pair in self.key_pairs if key_pair]}
    

class PrimitiveLiteralElement(DataLiteralElement):
    def __init__(self, value):
        self.value = value

    def as_json(self):
        return {"primitive": self.value}

class IntegerElement(PrimitiveLiteralElement):
    def __init__(self, value):
        self.value = value

    def as_json(self):
        return {"%k":"int", "%v": int(self.value)}

class AtomElement(PrimitiveLiteralElement):
    def __init__(self, value):
        self.value = value

    def as_json(self):
        return {"%k": "atom", "%v": self.value}

class KeyElement(PrimitiveLiteralElement):
    def __init__(self, value):
        self.value = value

    def as_json(self):
        return {"%k":"atom", "%v": self.value[-1::-1]}

class BooleanElement(PrimitiveLiteralElement):
    def __init__(self, value):
        self.value = value

    def as_json(self):
        if(self.value == "true"): return {"%k":"bool", "%v": True}
        else: return {"%k":"bool", "%v": False}

class KeyPairElement(Element):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def as_json(self):
        return [self.key.as_json(), self.value.as_json()]
        


########################### Lexer ############################
SKIP_RE = re.compile(r'(( |\t|\n)|\#.*)+')
Token = namedtuple('Token', 'kind lexeme loc')

def tokenize(input_str):
    toks = []
    loc = 0
    
    try:
        while loc < len(input_str):
            match = None
            match = SKIP_RE.match(input_str, loc)
            if match:
                loc += len(match.group())
            if loc >= len(input_str): 
                break
            
            for token_kind, regex_pattern in TOKEN_DEFINITIONS.items():
                regex = re.compile(regex_pattern)
                match = regex.match(input_str, loc)
                if match:
                    lexeme = match.group(0)
                    loc+=len(lexeme)
                    toks.append(Token(token_kind, lexeme, loc))
                    break
            if not match: 
                raise ValueError(f"Invalid token at locition {loc}: {input_str[loc:]}")
    except:
        print(f"Invalid token at Position {loc}")
        sys.exit(1)
        
    toks.append(Token('EOF', '<EOF>', loc+1))
    return toks




################################## Main #################################
input_string = sys.stdin.read()
toks = tokenize(input_string)
ast = parse(toks)
json_output = json.dumps(ast.as_json(), indent=2)
print(json_output)




'''
ebnf grammar

<language> ::= <sentence>

<sentence> ::= { <data-literal> }

<data-literal> ::= <list-literal> | <tuple-literal> | <map-literal> | <primitive-literal>

<primitive-literal> ::= <integer> | <atom> | <boolean>

<list-literal> ::= "[" [ <data-literal> { "," <data-literal> } ] "]"

<tuple-literal> ::= "{" [ <data-literal> { "," <data-literal> } ] "}"

<map-literal> ::= "%{" [ <key-pair> { "," <key-pair> } ] "}"

<key-pair> ::= <data-literal> "=>" <data-literal> | <key> <data-literal>

<integer> ::= <digit> { <digit> | "_" }

<atom> ::= ":" <alphabetic> { <alphanumeric> | "_" }

<key> ::= <alphabetic> { <alphanumeric> | "_" } ":"

<boolean> ::= "true" | "false"

<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<alphabetic> ::= "a" | "b" | "c" | ... | "z" | "A" | "B" | ... | "Z"

<alphanumeric> ::= <alphabetic> | <digit>

'''

