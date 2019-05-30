
def lexical_analysis(code):
	pass

def syntax_analysis(code):
	return None

def semantic_analysis(ast):
	pass


######### MAIN ###################

def main():
	# TODO parse arguments and read .cl's
	files = []
	
	program_code = ""
	
	# Read all files source codes and store it in memory.
	for file in files:
		try:
			with open(file, encoding="utf-8") as file:
					file_code += file.read()
		except (IOError, FileNotFoundError):
			print("Error! File \"{0}\" was not found".format(file))
		except Exception:
			print("An unexpected error occurred!")


	# Lexical Analysis
	lexical_analysis(program_code)

	# Syntax Analysis
	syntax_analysis(program_code)

	# Semantic Analysis
	semantic_analysis(syntax_analysis(program_code))


if __name__ == "__main__":
	main()