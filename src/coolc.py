import sys
from lexing.lexer import CoolLexer
from parsing.parser import CoolParser
from semantics.semanalyzer import Semananalyzer
from intermediate_code.cil_visitor import CILVisitor
from code_generation.mips_visitor import MipsVisitor


##################################

def lexical_analysis(code):
	return CoolLexer().test(code)

def syntax_analysis(code):
	return CoolParser().parse(code)

def semantic_analysis(ast):
	return Semananalyzer().analyze(ast)

def intermediate_code(ast):
	s = CILVisitor()
	return s.visit(ast), s.inherit_graph

def generate_mips(ast, inherit_graph, output_file):
	return MipsVisitor(inherit_graph, output_file).visit(ast)


######### MAIN ###################

def main():
	files = sys.argv[1:]
	if files == []:
		files = ["..\\examples\\mytest.cl"]

	if len(files) == 0:
		print("No file is given to coolc compiler.")
		return

	# Check all files have the *.cl extension.
	for file in files:
		if not str(file).endswith(".cl"):
			print("Cool program files must end with a .cl extension.")
			return
	
	program_code = ""
	
	# Read all files source codes and store it in memory.
	for file in files:
		try:
			with open(file, encoding="utf-8") as file:
				program_code += file.read()
		except (IOError, FileNotFoundError):
			print("Error! File \"{0}\" was not found".format(file))
			return

	#===========   Lexical Analysis
	# lexical_analysis(program_code)

	#===========   Syntax Analysis (includes lexical analysis)
	ast = syntax_analysis(program_code)
	if not ast:
		return
	# print(ast)

	#===========   Semantic Analysis
	anotated_ast = semantic_analysis(ast)
	if not anotated_ast:
		return
	# print(anotated_ast)

	#===========   Intermediate Code
	cil, inherit_graph = intermediate_code(anotated_ast)
	# print(cil)

	#===========   Code Generation
	generate_mips(cil, inherit_graph, files[0][:-3] + ".mips")

if __name__ == "__main__":
	main()