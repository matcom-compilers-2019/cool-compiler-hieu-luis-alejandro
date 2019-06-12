import sys
sys.path.append('..')

import commons.cool_ast as ast
import commons.cil_ast as cil
import commons.visitor as visitor
# from commons.scope import VariableInfo



class VariableInfo:
    def __init__(self, name):
        self.name = name
        self.vmholder = None

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

		# Data of the function being visited
		self.current_function_name = ""
		self.localvars = []
		self.instructions = []

		# Counters to make variable's names unique
		self.internal_count = 0					# LOCAL variables
		self.internal_label_count = 0			# LABELs


	# ======================================================================
	# =[ UTILS ]============================================================
	# ======================================================================

	#---------- LABELs

	def define_internal_label(self):
		label = f'LABEL_{self.internal_label_count}'
		self.internal_label_count += 1
		return label

	#---------- .DATA

	def register_data(self, value):
		vname = f'data_{len(self.dotdata)}'
		data_node = cil.Data(vname, value)
		self.dotdata.append(data_node)
		return data_node

	#---------- .CODE

	def build_internal_vname(self, vname):
		vname = f'{self.internal_count}_{self.current_function_name}_{vname}'
		self.internal_count +=1
		return vname

	def register_internal_local(self):
		vinfo = VariableInfo('internal')
		return self.register_local(vinfo)

	def register_local(self, vinfo):
		vinfo.name = f'{self.internal_count}_{self.current_function_name}_{vinfo.name}'
		vinfo.vmholder = len(self.localvars)
		local_node = cil.LocalDeclaration(vinfo)
		self.localvars.append(local_node)
		self.internal_count +=1
		return vinfo

	def register_instruction(self, instruction_type, *args):
		instruction = instruction_type(*args)
		self.instructions.append(instruction)
		return instruction

	# ======================================================================


	@visitor.on('node')
	def visit(self, node):
		return "This hides pylint's errors about visit return type"


################################ PROGRAM, TYPE AND OBJECT ##############################



	@visitor.when(ast.Program)
	def visit(self, node: ast.Program):
		return


	@visitor.when(ast.Class)
	def visit(self, node: ast.Class):
		return


	@visitor.when(ast.ClassMethod)
	def visit(self, node: ast.ClassMethod):
		# Resets
		self.current_function_name = ""
		self.localvars = []
		self.instructions = []
		self.internal_count = 0
		# TODO: set current_function_name to CIL name


		# ARGUMENTS
		params_cil = []
		for formal_param in node.formal_params:
			self.visit(formal_param)

		self.visit(node.body)
		return cil.Function(self.current_function_name, params_cil, self.localvars, self.instructions)


	@visitor.when(ast.ClassAttribute)
	def visit(self, node: ast.ClassAttribute):
		return


	@visitor.when(ast.FormalParameter)
	def visit(self, node: ast.FormalParameter):
		return


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
		data_vinfo = self.register_data(node.content)
		return data_vinfo


	@visitor.when(ast.Boolean)
	def visit(self, node: ast.Boolean):
		return 1 if node.content == True else 0


	################################## EXPRESSIONS ##############################


	@visitor.when(ast.NewObject)
	def visit(self, node: ast.NewObject):
		vinfo = self.register_internal()
		# TODO: change node.type to the actual type used for CIL AST
		self.register_instruction(cil.Allocate, vinfo, node.type)
		return vinfo


	@visitor.when(ast.IsVoid)
	def visit(self, node: ast.IsVoid):
		return


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
		# <.locals> 
		# declare initializations's locals recursively
		for variable in node.variables:
			self.visit(variable)
		let_value = self.register_internal_local()

		# <.code>
		vinfo = self.visit(node.body)
		self.register_instruction(cil.CILAssign, let_value, vinfo)  # *** Actually necesary !?
		return vinfo


	@visitor.when(ast.LetVariable)
	def visit(self, node: ast.LetVariable):
		vinfo = self.register_local(VariableInfo(node.name))
		# TODO: return the corresponding computed_type of the variable's initialization expression
		# self.register_instruction(cil.Allocate, vinfo, "computed_type")


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
		dest_vinfo = self.register_internal_local()

		# <.code>
		result_vinfo = self.visit(node.boolean_expr)
		self.register_instruction(cil.Minus, dest_vinfo, 0, result_vinfo)
		return dest_vinfo


	@visitor.when(ast.BooleanComplement)
	def visit(self, node: ast.BooleanComplement):
		# <.locals>
		dest_vinfo = self.register_internal_local()

		# <.code>
		result_vinfo = self.visit(node.boolean_expr)
		self.register_instruction(cil.Minus, dest_vinfo, 1, result_vinfo)
		return dest_vinfo


	################################ BINARY OPERATIONS ##################################


	@visitor.when(ast.Addition)
	def visit(self, node: ast.Addition):
		# <.locals>
		dest_vinfo = self.register_internal_local()

		# <.code>
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		self.register_instruction(cil.Plus, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.Subtraction)
	def visit(self, node: ast.Subtraction):
		# <.locals>
		dest_vinfo = self.register_internal_local()

		# <.code>
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		self.register_instruction(cil.Minus, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.Multiplication)
	def visit(self, node: ast.Multiplication):
		# <.locals>
		dest_vinfo = self.register_internal_local()

		# <.code>
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		self.register_instruction(cil.Mult, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.Division)
	def visit(self, node: ast.Division):
		# <.locals>
		dest_vinfo = self.register_internal_local()

		# <.code>
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		self.register_instruction(cil.Div, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.Equal)
	def visit(self, node: ast.Equal):
		# <.locals>
		dest_vinfo = self.register_internal_local()

		# <.code>
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		self.register_instruction(cil.Equal, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.LessThan)
	def visit(self, node: ast.LessThan):
		# <.locals>
		dest_vinfo = self.register_internal_local()

		# <.code>
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		self.register_instruction(cil.LessThan, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.LessThanOrEqual)
	def visit(self, node: ast.LessThanOrEqual):
		# <.locals>
		dest_vinfo = self.register_internal_local()

		# <.code>
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		self.register_instruction(cil.EqualOrLessThan, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo