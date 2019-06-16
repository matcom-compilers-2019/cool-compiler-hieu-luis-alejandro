import ply.lex as lex
from ply.lex import TOKEN


class CoolLexer:
	"""
	CoolLexer Class.

	Deals with lexical analysis of Cool programs

	To use the lexer, create an object from the class and feed the source code to the object by calling
	'input(str)', where 'str' is the program's code as a string.

	New tokens are fetched from the lexer using the 'token()' function (1 by 1).

	To access the last token that was fetched without moving on to a new token, use 'last_token' property
	"""

	def __init__(self):
		# Properties used by ply.lex
		self.tokens = self.token_names + tuple(self.reserved_keywords.values())  # ply tokens collection
		self.reserved = self.reserved_keywords.keys()  # ply reserved keywords map

		# Build Ply.Lex
		self.lexer = lex.lex(module=self)

		# Save program's code to check for error's columns
		self.program = ""

	def test(self,input):
		"""
		Prints all tokens from the input source code to stdout.
		"""
		self.input(input)
		a = self.lexer.token()
		while a:
			print(a)
			a = self.lexer.token()

	def input(self, input):
		"""
		Feeds input source code to the lexical analyzer.
		"""
		self.lexer.input(input)

	def token(self):
		"""
		Returns the next token in the program's code. This token can be accessed
		again with the last_token property.
		"""
		self.last_token = self.lexer.token()
		return self.last_token

   #################################### ITERATOR PROTOCOL ############################################

	def __iter__(self):
		return self

	def __next__(self):
		t = self.token()
		if t is None:
			raise StopIteration
		return t

	def next(self):
		return self.__next__()

	# ####################################	TOKENS DEFINITIONS	######################################

	#	 Collection of COOL Syntax Tokens.
	token_names = (
		# Identifiers
		"ID", "TYPE",

		# Primitive Types
		"INTEGER", "STRING", "BOOLEAN",

		# Literals
		"LPAREN", "RPAREN", "LBRACE", "RBRACE", "COLON", "COMMA", "DOT", "SEMICOLON", "AT",

		# Operators
		"PLUS", "MINUS", "MULTIPLY", "DIVIDE", "EQ", "LT", "LTEQ", "ASSIGN", "INT_COMP",

		# Special Operators
		"ARROW"
	)

	#	 Map of COOL reserved keywords.
	reserved_keywords = {
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

	# #################################### LEXICAL RULES	######################################

	# Ignore rule for single line comments
	t_ignore_SINGLE_LINE_COMMENT = r"\-\-[^\n]*"

	# Simple tokens
	t_LPAREN = r'\('        # (
	t_RPAREN = r'\)'        # )
	t_LBRACE = r'\{'        # {
	t_RBRACE = r'\}'        # }
	t_COLON = r'\:'         # :
	t_COMMA = r'\,'         # ,
	t_DOT = r'\.'           # .
	t_SEMICOLON = r'\;'     # ;
	t_AT = r'\@'            # @
	t_MULTIPLY = r'\*'      # *
	t_DIVIDE = r'\/'        # /
	t_PLUS = r'\+'          # +
	t_MINUS = r'\-'         # -
	t_INT_COMP = r'~'       # ~
	t_LT = r'\<'            # <
	t_EQ = r'\='            # =
	t_LTEQ = r'\<\='        # <=
	t_ASSIGN = r'\<\-'      # <-
	t_ARROW = r'\=\>'       # =>

	@TOKEN(r"(true|false)")
	def t_BOOLEAN(self, token):
		token.value = True if token.value == "true" else False
		return token

	@TOKEN(r"\d+")
	def t_INTEGER(self, token):
		token.value = int(token.value)
		return token

	@TOKEN(r"[A-Z][a-zA-Z_0-9]*")
	def t_TYPE(self, token):
		token.type = self.reserved_keywords.get(token.value, 'TYPE')
		return token

	@TOKEN(r"[a-z_][a-zA-Z_0-9]*")
	def t_ID(self, token):
		token.type = self.reserved_keywords.get(token.value, 'ID')
		return token

	@TOKEN(r"\n+")
	def t_newline(self, token):
		token.lexer.lineno += len(token.value)

	# Ignore Whitespace Character Rule
	t_ignore = ' \t\r\f'

	########################## STATEFUL LEXICAL RULES ###############################

	# LEXER STATES
	@property
	def states(self):
		return (
			("STRING", "exclusive"),
			("COMMENT", "exclusive")
		)

	######################### THE STRING STATE #####################

	@TOKEN(r"\"")
	def t_start_string(self, token):
		token.lexer.push_state("STRING")
		token.lexer.string_backslashed = False
		token.lexer.stringbuf = ""

	@TOKEN(r"\n")
	def t_STRING_newline(self, token):
		token.lexer.lineno += 1
		if not token.lexer.string_backslashed:
			print("String newline not escaped")
			token.lexer.skip(1)
		else:
			token.lexer.string_backslashed = False

	@TOKEN(r"\"")
	def t_STRING_end(self, token):
		if not token.lexer.string_backslashed:
			token.lexer.pop_state()
			token.value = token.lexer.stringbuf
			token.type = "STRING"
			return token
		else:
			token.lexer.stringbuf += '"'
			token.lexer.string_backslashed = False

	@TOKEN(r"[^\n]")
	def t_STRING_anything(self, token):
		if token.lexer.string_backslashed:
			if token.value == 'b':
					token.lexer.stringbuf += '\b'
			elif token.value == 't':
					token.lexer.stringbuf += '\t'
			elif token.value == 'n':
					token.lexer.stringbuf += '\n'
			elif token.value == 'f':
					token.lexer.stringbuf += '\f'
			elif token.value == '\\':
					token.lexer.stringbuf += '\\'
			else:
					token.lexer.stringbuf += token.value
			token.lexer.string_backslashed = False
		else:
			if token.value != '\\':
					token.lexer.stringbuf += token.value
			else:
					token.lexer.string_backslashed = True

	# STRING error handler
	def t_STRING_error(self, token):
		print("Illegal character! Line: {0}, character: {1}".format(token.lineno, token.value[0]))
		token.lexer.skip(1)

	# STRING ignored characters
	t_STRING_ignore = ''

	####################### THE COMMENT STATE ######################
	@TOKEN(r"\(\*")
	def t_start_comment(self, token):
		token.lexer.push_state("COMMENT")
		token.lexer.comment_count = 0

	@TOKEN(r"\(\*")
	def t_COMMENT_startanother(self, t):
		t.lexer.comment_count += 1

	@TOKEN(r"\*\)")
	def t_COMMENT_end(self, token):
		if token.lexer.comment_count == 0:
			token.lexer.pop_state()
		else:
			token.lexer.comment_count -= 1

	# COMMENT error rule
	def t_COMMENT_error(self, token):
		token.lexer.skip(1)

	# COMMENT ignored characters
	t_COMMENT_ignore = ''

	##################### ERROR REPORTING RULE ######################

	def t_error(self, token):
		line_start = self.program.rfind('\n', 0, token.lexpos) + 1
		column = (token.lexpos - line_start) + 1
		print("Illegal character! Line: {0}, Column: {1}".format(token.lineno, column))
		token.lexer.skip(1)

		
# #----------- TESTS

# s = CoolLexer()
# fpath = "D:\Scripts\cool-compiler-hieu-luis-alejandro\examples\\graph.cl"
# with open(fpath, encoding="utf-8") as file:
# 	cool_program_code = file.read()
# 	s.test(cool_program_code)