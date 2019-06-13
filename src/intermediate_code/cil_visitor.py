import sys
sys.path.append('..')

import commons.cool_ast as ast
import commons.cil_ast as cil
import commons.visitor as visitor
import commons.settings as settings


class CILVisitor:
	"""
	CIL Visitor Class.

	This visitor will process the AST of a Cool program and return the equivalent
	3 address code. 3AC will be represented as another AST, consisting of Function, Statement and Data nodes.
	These nodes denotes the constructs of the 3 address code CIL.
	"""

	def __init__(self):
		# Type declarations of the program
		self.dottype = []

		# String declarations of the program
		self.dotdata = []

		# Function declarations of the program
		self.dotcode = []

		# Data of the class being visited
		self.current_class_name = ""

		# Data of the function being visited
		self.current_function_name = ""
		self.localvars = []
		self.instructions = []

		# Counters to make variable's names unique
		self.internal_count = 0					# LOCAL _internals  --- used to store return/temp values
		self.internal_var_count = 0			# LOCAL variables
		self.internal_label_count = 0			# LABELs


	# ======================================================================
	# =[ UTILS ]============================================================
	# ======================================================================

	#---------- LABELs

	def define_internal_label(self):
		label = f'LABEL_{self.internal_label_count}'
		self.internal_label_count += 1
		return label

	#---------- .TYPE

	def register_type(self, ttype):
		# TODO: map every type to an int
		self.dottype.append(ttype)

	#---------- .DATA

	def register_data(self, value):
		vname = f'data_{len(self.dotdata)}'
		data_node = cil.Data(vname, value)
		self.dotdata.append(data_node)
		return data_node

	#---------- .CODE

	def build_internal_vname(self, vname):
		vname = f'{self.internal_var_count}_{self.current_function_name}_{vname}'
		self.internal_var_count +=1
		return vname

	def register_internal_local(self):
		return self.register_local(f'internal_{self.internal_count}')

	def register_local(self, vname):
		vname = self.build_internal_vname(vname)
		self.localvars.append(cil.LocalDeclaration(vname))
		self.internal_var_count +=1
		return vname

	def register_instruction(self, instruction_type, *args):
		instruction = instruction_type(*args)
		self.instructions.append(instruction)
		return instruction

	def register_function(self, function):
		self.dotcode.append(function)

	# ======================================================================


	@visitor.on('node')
	def visit(self, node):
		return "This hides pylint's errors about visit return type"


################################ PROGRAM, TYPE AND OBJECT ##############################



	@visitor.when(ast.Program)
	def visit(self, node: ast.Program):
		dotcode = []

		for klass in node.classes:
			ttype, functions = self.visit(klass)
			self.dottype.append(ttype)
			dotcode += functions

		return cil.Program(self.dottype, self.dotdata, dotcode)


	@visitor.when(ast.Class)
	def visit(self, node: ast.Class):
		"""
		Translate the COOL Class to a CIL Type.
		At the same time build an initializer function for that Type.
		"""

		attributes = []
		methods = []
		functions = []

		# Translate all the properties (COOL) into attributes (CIL)
		# and build an initializer function
		self.localvars = []
		self.instructions = []
		self.internal_var_count = 0
		self.current_function_name = f'{self.current_class_name}_{settings.INIT_CIL_SUFFIX}'

		for feature in node.features:
			if isinstance(feature, ast.ClassAttribute):
				attributes.append(self.visit(feature))

		# Translate all Class Methods (COOL) into Type Methods (CIL)
		# and return the functions associated
		for feature in node.features:
			if isinstance(feature, ast.ClassMethod):
				method = self.visit(feature)
				methods.append(method)

		return cil.Type(node.name, attributes, methods)


	@visitor.when(ast.ClassAttribute)
	def visit(self, node: ast.ClassAttribute):
		if node.init_expr:
			rname = self.visit(node.init_expr)
			self.register_instruction(cil.SetAttrib, settings.SELF_CIL_NAME, node.name, rname)
		else:
			# TODO: maybe assign here the default value of the node's type if not initialized ?
			self.register_instruction(cil.SetAttrib, settings.SELF_CIL_NAME, node.name, "DEFAULT VALUE HERE")
		return cil.Attribute(node.name)


	@visitor.when(ast.ClassMethod)
	def visit(self, node: ast.ClassMethod):
		self.localvars = []
		self.instructions = []
		self.internal_var_count = 0
		self.current_function_name = f'{self.current_class_name}_{node.name}'

		# ARGUMENTS
		arguments = [cil.ArgDeclaration(settings.SELF_CIL_NAME)]
		for formal_param in node.formal_params:
			arguments.append(self.visit(formal_param))

		self.visit(node.body)

		func = cil.Function(self.current_function_name, arguments, self.localvars, self.instructions)
		self.register_function(func)
		return cil.Method(node.name, func.name)


	@visitor.when(ast.FormalParameter)
	def visit(self, node: ast.FormalParameter):
		# TODO: register in scope
		return cil.ArgDeclaration(node.name)


	################################## INSTANCES ##############################


	@visitor.when(ast.Object)
	def visit(self, node: ast.Object):
		return


	@visitor.when(ast.Self)
	def visit(self, node: ast.Self):
		return


	################################## CONSTANTS ##############################



	@visitor.when(ast.Integer)
	def visit(self, node: ast.Integer):
		return node.content


	@visitor.when(ast.String)
	def visit(self, node: ast.String):
		data_vname = self.register_data(node.content)
		return data_vname


	@visitor.when(ast.Boolean)
	def visit(self, node: ast.Boolean):
		return 1 if node.content == True else 0


	################################## EXPRESSIONS ##############################


	@visitor.when(ast.NewObject)
	def visit(self, node: ast.NewObject):
		vname = self.register_internal_local()
		# TODO: change node.type to the actual type used for CIL AST
		self.register_instruction(cil.Allocate, vname, node.type)
		return vname


	@visitor.when(ast.IsVoid)
	def visit(self, node: ast.IsVoid):
		# LOCAL <isvoid.value>
		# LOCAL <expr.locals>
		# LOCAL <temp_var>
		# 	...
		# <expr.code>
		# <temp_var> = TYPEOF <expr.value>
		# <isvoid.value> = <temp_var> == VOID_TYPE

		# <.locals>
		value = self.register_internal_local()
		ttype = self.register_internal_local()

		# <.code>
		expr_val = self.visit(node.expr)
		self.register_instruction(cil.TypeOf, ttype, expr_val)
		# TODO: replace VOID_TYPE with the actual void type
		self.register_instruction(cil.Equal, value, ttype, "VOID_TYPE")


	@visitor.when(ast.Assignment)
	def visit(self, node: ast.Assignment):
		return


	@visitor.when(ast.Block)
	def visit(self, node: ast.Block):
		return


	@visitor.when(ast.DynamicDispatch)
	def visit(self, node: ast.DynamicDispatch):
		return


	@visitor.when(ast.StaticDispatch)
	def visit(self, node: ast.StaticDispatch):
		return


	@visitor.when(ast.Let)
	def visit(self, node: ast.Let):
		# <let_variables.locals>
		# LOCAL <let.value>
		# 	...
		# <let_variables.inits>
		# <let.body.code>
		# <let.body.value> is the return value of let

		# <.locals>
		# declare initializations's locals recursively
		for variable in node.variables:
			self.visit(variable)

		# <.code>
		return self.visit(node.body)


	@visitor.when(ast.LetVariable)
	def visit(self, node: ast.LetVariable):
		vname = self.register_local(node.name)
		# TODO: return the corresponding computed_type of the variable's initialization expression
		# self.register_instruction(cil.Allocate, vname, "computed_type")


	@visitor.when(ast.If)
	def visit(self, node: ast.If):
		# LOCAL <if.value>
		# 	<condition.locals>
		# 	<else.locals>
		# 	<then.locals>
		# 		...
		# 	<condition.body>
		# if <condition.value> GOTO then_lbl
		# 	<else.code>
		# <if.value> = <else.value>
		# GOTO continue_lbl
		# LABEL then_lbl:
		# 	<then.code>
		# <if.value> = <then.value>
		# LABEL continue_lbl:

		# <.locals>
		if_value = self.register_internal_local()
		then_lbl = self.define_internal_label()
		continue_lbl = self.define_internal_label()

		# <.body>
		condition_value = self.visit(node.condition)
		self.register_instruction(cil.IfGoto, condition_value, then_lbl)
		else_value = self.visit(node.else_body)
		self.register_instruction(cil.Assign, if_value, else_value)
		self.register_instruction(cil.Goto, continue_lbl)
		self.register_instruction(cil.Label, then_lbl)
		then_value = self.visit(node.then_body)
		self.register_instruction(cil.Assign, if_value, then_value)
		self.register_instruction(cil.Label, continue_lbl)

		return if_value


	@visitor.when(ast.WhileLoop)
	def visit(self, node: ast.WhileLoop):
		# LOCAL <while.value>
		# 	<condition.locals>
		# 	<body.locals>
		#  	...
		# LABEL start_lbl
		# 	<condition.code>
		# if <condition.value> GOTO body_lbl
		# GOTO continue_lbl
		# LABEL body_lbl
		# 	<body.code>
		# GOTO start_lbl
		# LABEL continue_lbl
		# <while.value> = 'VOID_TYPE'

		# <.locals>
		while_value = self.register_internal_local()
		start_lbl = self.define_internal_label()
		body_lbl = self.define_internal_label()
		continue_lbl = self.define_internal_label()

		# <.code>
		self.register_instruction(cil.Label, start_lbl)
		condition_value = self.visit(node.condition)		# Generate <condition.body> nad <condition.locals>
		self.register_instruction(cil.IfGoto, condition_value, body_lbl)
		self.register_instruction(cil.Goto, continue_lbl)
		self.register_instruction(cil.Label, body_lbl)
		self.visit(node.body)
		self.register_instruction(cil.Goto, start_lbl)
		self.register_instruction(cil.Label, continue_lbl)
		# TODO: assign VOID type to while return value
		# self.register_instruction(cil.Assign, while_value, "put void type here")

		return while_value


	@visitor.when(ast.Case)
	def visit(self, node: ast.Case):
		return


	@visitor.when(ast.Action)
	def visit(self, node: ast.Action):
		return


	################################ UNARY OPERATIONS ##################################


	@visitor.when(ast.IntegerComplement)
	def visit(self, node: ast.IntegerComplement):
		# <.locals>
		dest_vname = self.register_internal_local()

		# <.code>
		result_vname = self.visit(node.boolean_expr)
		self.register_instruction(cil.Minus, dest_vname, 0, result_vname)
		return dest_vname


	@visitor.when(ast.BooleanComplement)
	def visit(self, node: ast.BooleanComplement):
		# <.locals>
		dest_vname = self.register_internal_local()

		# <.code>
		result_vname = self.visit(node.boolean_expr)
		self.register_instruction(cil.Minus, dest_vname, 1, result_vname)
		return dest_vname


	################################ BINARY OPERATIONS ##################################


	@visitor.when(ast.Addition)
	def visit(self, node: ast.Addition):
		# <.locals>
		dest_vname = self.register_internal_local()

		# <.code>
		left_vname = self.visit(node.left)
		right_vname = self.visit(node.right)
		self.register_instruction(cil.Plus, dest_vname, left_vname, right_vname)
		return dest_vname


	@visitor.when(ast.Subtraction)
	def visit(self, node: ast.Subtraction):
		# <.locals>
		dest_vname = self.register_internal_local()

		# <.code>
		left_vname = self.visit(node.left)
		right_vname = self.visit(node.right)
		self.register_instruction(cil.Minus, dest_vname, left_vname, right_vname)
		return dest_vname


	@visitor.when(ast.Multiplication)
	def visit(self, node: ast.Multiplication):
		# <.locals>
		dest_vname = self.register_internal_local()

		# <.code>
		left_vname = self.visit(node.left)
		right_vname = self.visit(node.right)
		self.register_instruction(cil.Mult, dest_vname, left_vname, right_vname)
		return dest_vname


	@visitor.when(ast.Division)
	def visit(self, node: ast.Division):
		# <.locals>
		dest_vname = self.register_internal_local()

		# <.code>
		left_vname = self.visit(node.left)
		right_vname = self.visit(node.right)
		self.register_instruction(cil.Div, dest_vname, left_vname, right_vname)
		return dest_vname


	@visitor.when(ast.Equal)
	def visit(self, node: ast.Equal):
		# <.locals>
		dest_vname = self.register_internal_local()

		# <.code>
		left_vname = self.visit(node.left)
		right_vname = self.visit(node.right)
		self.register_instruction(cil.Equal, dest_vname, left_vname, right_vname)
		return dest_vname


	@visitor.when(ast.LessThan)
	def visit(self, node: ast.LessThan):
		# <.locals>
		dest_vname = self.register_internal_local()

		# <.code>
		left_vname = self.visit(node.left)
		right_vname = self.visit(node.right)
		self.register_instruction(cil.LessThan, dest_vname, left_vname, right_vname)
		return dest_vname


	@visitor.when(ast.LessThanOrEqual)
	def visit(self, node: ast.LessThanOrEqual):
		# <.locals>
		dest_vname = self.register_internal_local()

		# <.code>
		left_vname = self.visit(node.left)
		right_vname = self.visit(node.right)
		self.register_instruction(cil.EqualOrLessThan, dest_vname, left_vname, right_vname)
		return dest_vname