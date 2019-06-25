from lexing.lexer import CoolLexer
from parsing.parser import CoolParser
from semantics.semanalyzer import Semananalyzer
from intermediate_code.cil_visitor import CILVisitor
from code_generation.mips_visitor import MipsVisitor

def lexical_analysis(code):
	return CoolLexer().test(code)

def syntax_analysis(code):
	return CoolParser().parse(code)

def semantic_analysis(ast):
	return Semananalyzer().analyze(ast)

def intermediate_code(ast):
	s = CILVisitor()
	return s.visit(ast), s.inherit_graph

def generate_mips(ast, inherit_graph):
	return MipsVisitor(inherit_graph).visit(ast)


######### MAIN ###################

def main():
	# TODO parse arguments and read .cl's
	files = ["..\\examples\\mytest.cl"]
	
	program_code = ""
	
	# Read all files source codes and store it in memory.
	for file in files:
		try:
			with open(file, encoding="utf-8") as file:
				program_code += file.read()
		except (IOError, FileNotFoundError):
			print("Error! File \"{0}\" was not found".format(file))
		except Exception:
			print("An unexpected error occurred!")


	# Lexical Analysis
	# lexical_analysis(program_code)

	# Lexical and Syntax Analysis
	ast = syntax_analysis(program_code)
	if not ast:
		return
	# print(ast)

	# Semantic Analysis
	anotated_ast = semantic_analysis(ast)
	if not anotated_ast:
		return
	# print(anotated_ast)

	# Generate Intermediate Code
	cil, inherit_graph = intermediate_code(anotated_ast)
	# print(cil)

	# Mips code generation
	generate_mips(cil, inherit_graph)

if __name__ == "__main__":
	main()