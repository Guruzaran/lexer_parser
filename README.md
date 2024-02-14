Name:		    Gurusaran Venkatachalam Rajarajacholan
B-Number:	    B01038679
Email:		gvenkatachal@binghamton.edu

Language Used: PYTHON


Description:
The lexer and parser are designed to tokenize input strings and generate an abstract syntax tree (AST) respectively, based on the grammar rules provided.

Token Definitions:
Token definition is the dictionary with token as a key and regex as values, which will be used to tokenize the input strings.
The TOKEN_DEFINITIONS dictionary contains regular expressions defining different token types.

Methods:
LEXER:
The tokenize() function takes an input string and returns a list of tokens
Tokenizes input strings based on predefined token definitions.
Skips whitespace characters (spaces, tabs, newlines) and comments.
Identifies tokens such as integers, atoms, commas, colons, keys, values, booleans, brackets, and end of file marker.
Ignores whitespace and #-to-end-of-line comments, if any. Note that there could be a sequence of alternating whitespace and #-comments.
Checks whether the prefix of the text after the whitespace/comments matches a possible multiple character token.
Otherwise returns the first character in the text as a single character token. This works particularly well if these tokens have the token kind set to the lexeme. This will allow any illegal characters to be delivered to the parser which has better context to report errors.

PARSER:
Parses tokenized input strings into a hierarchical structure represented by an abstract syntax tree (AST).
Recognizes various literal elements such as integers, atoms, lists, tuples, maps, and booleans.
Handles different types of literals and their combinations based on grammar rules.





