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
		self.dotdata = []
		self.current_function_name = ""
		self.localvars = []
		self.instructions = []
		self.internal_count = 0


	# ======================================================================
	# =[ UTILS ]============================================================
	# ======================================================================

	def build_internal_vname(self, vname):
		vname = f'{self.internal_count}_{self.current_function_name}_{vname}'
		self.internal_count +=1
		return vname

	def define_internal_local(self):
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

	def register_data(self, value):
		vname = f'data_{len(self.dotdata)}'
		data_node = cil.Data(vname, value)
		self.dotdata.append(data_node)
		return data_node

	# ======================================================================


	@visitor.on('node')
	def visit(self, node):
		pass


	@visitor.when(ast.Program)
	def visit(self, node: ast.Program):
		pass


	@visitor.when(ast.Class)
	def visit(self, node: ast.Class):
		pass


	@visitor.when(ast.ClassMethod)
	def visit(self, node: ast.ClassMethod):
		# set current_function_name to CIL name
		params_cil = []
		for formal_param in node.formal_params:
			self.visit(formal_param)
			params_cil.append(formal_param.result)
		self.visit(node.body)

		# Return
		node.result = cil.Function(self.current_function_name, params_cil, self.localvars, self.instructions)

		# Clean up
		self.current_function_name = ""
		self.localvars = []
		self.instructions = []
		self.internal_count = 0


	@visitor.when(ast.ClassAttribute)
	def visit(self, node: ast.ClassAttribute):
		pass


	@visitor.when(ast.FormalParameter)
	def visit(self, node: ast.FormalParameter):
		pass


	@visitor.when(ast.Object)
	def visit(self, node: ast.Object):
		pass


	@visitor.when(ast.Self)
	def visit(self, node: ast.Self):
		pass


	@visitor.when(ast.Constant)
	def visit(self, node: ast.Constant):
		pass


	@visitor.when(ast.Integer)
	def visit(self, node: ast.Integer):
		pass


	@visitor.when(ast.String)
	def visit(self, node: ast.String):
		pass


	@visitor.when(ast.Boolean)
	def visit(self, node: ast.Boolean):
		pass


	@visitor.when(ast.Expr)
	def visit(self, node: ast.Expr):
		pass


	@visitor.when(ast.NewObject)
	def visit(self, node: ast.NewObject):
		pass


	@visitor.when(ast.IsVoid)
	def visit(self, node: ast.IsVoid):
		pass


	@visitor.when(ast.Assignment)
	def visit(self, node: ast.Assignment):
		pass


	@visitor.when(ast.Block)
	def visit(self, node: ast.Block):
		pass


	@visitor.when(ast.DynamicDispatch)
	def visit(self, node: ast.DynamicDispatch):
		pass


	@visitor.when(ast.StaticDispatch)
	def visit(self, node: ast.StaticDispatch):
		pass


	@visitor.when(ast.Let)
	def visit(self, node: ast.Let):
		pass


	@visitor.when(ast.If)
	def visit(self, node: ast.If):
		pass


	@visitor.when(ast.WhileLoop)
	def visit(self, node: ast.WhileLoop):
		pass


	@visitor.when(ast.Case)
	def visit(self, node: ast.Case):
		pass


	@visitor.when(ast.Action)
	def visit(self, node: ast.Action):
		pass


	@visitor.when(ast.IntegerComplement)
	def visit(self, node: ast.IntegerComplement):
		pass


	@visitor.when(ast.BooleanComplement)
	def visit(self, node: ast.BooleanComplement):
		pass


	@visitor.when(ast.Addition)
	def visit(self, node: ast.Addition):
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		dest_vinfo = self.define_internal_local()
		self.register_instruction(cil.Plus, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.Subtraction)
	def visit(self, node: ast.Subtraction):
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		dest_vinfo = self.define_internal_local()
		self.register_instruction(cil.Minus, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.Multiplication)
	def visit(self, node: ast.Multiplication):
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		dest_vinfo = self.define_internal_local()
		self.register_instruction(cil.Mult, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.Division)
	def visit(self, node: ast.Division):
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		dest_vinfo = self.define_internal_local()
		self.register_instruction(cil.Div, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.Equal)
	def visit(self, node: ast.Equal):
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		dest_vinfo = self.define_internal_local()
		self.register_instruction(cil.Equal, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.LessThan)
	def visit(self, node: ast.LessThan):
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		dest_vinfo = self.define_internal_local()
		self.register_instruction(cil.LessThan, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo


	@visitor.when(ast.LessThanOrEqual)
	def visit(self, node: ast.LessThanOrEqual):
		left_vinfo = self.visit(node.left)
		right_vinfo = self.visit(node.right)
		dest_vinfo = self.define_internal_local()
		self.register_instruction(cil.EqualOrLessThan, dest_vinfo, left_vinfo, right_vinfo)
		return dest_vinfo