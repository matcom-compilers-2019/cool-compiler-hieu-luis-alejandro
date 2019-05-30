import ply.lex as lex
from ply.lex import TOKEN


class CoolLexer:

	# ############################## LEXER DEFINITIONS	######################################

	#	 Collection of COOL Syntax Tokens.
	token_names = (
		# Identifiers
		"ID", "TYPE",

		# Primitive Types
		"INTEGER", "STRING", "BOOLEAN",

		# Literals
		"LPAREN", "RPAREN", "LBRACE", "RBRACE", "COLON", "COMMA", "DOT", "SEMICOLON", "AT",

		# Operators
		"PLUS", "MINUS", "MULTIPLY", "DIVIDE", "EQ", "LT", "LTEQ", "ASSIGN", "INT_COMP", "NOT",

		# Special Operators
		"ARROW"
	)

	#	 Map of COOL reserved keywords.
	cool_reserved = {
		"case": "CASE",
		"class": "CLASS",
		"else": "ELSE",
		"esac": "ESAC",
		"fi": "FI",
		"if": "IF",
		"in": "IN",
		"inherits": "INHERITS",
		"isvoid": "ISVOID",
		"let": "LET",
		"loop": "LOOP",
		"new": "NEW",
		"of": "OF",
		"pool": "POOL",
		"self": "SELF",
		"then": "THEN",
		"while": "WHILE",
		"not": "NOT"
	}