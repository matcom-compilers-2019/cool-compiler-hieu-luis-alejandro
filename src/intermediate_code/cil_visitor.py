import sys
sys.path.append('..')

import commons.cool_ast as ast
import commons.cil_ast as cil
import commons.visitor as visitor


class CILVisitor:
	"""
	CIL Visitor Class.

	This visitor will process the AST of a Cool program and return the equivalent
	3 address code. 3AC will be represented as another AST, consisting of Function, Statement and Data nodes.
	These nodes denotes the constructs of the 3 address code CIL.
	"""

	def __init__(self):
		pass


	@visitor.on('node')
	def visit(self, node, tabs):
		pass


	@visitor.when(ast.Program)
	def visit(self, node: ast.Program, tabs):
		pass


	@visitor.when(ast.Class)
	def visit(self, node: ast.Class, tabs):
		pass


	@visitor.when(ast.ClassFeature)
	def visit(self, node: ast.ClassFeature, tabs):
		pass


	@visitor.when(ast.ClassMethod)
	def visit(self, node: ast.ClassMethod, tabs):
		pass


	@visitor.when(ast.ClassAttribute)
	def visit(self, node: ast.ClassAttribute, tabs):
		pass


	@visitor.when(ast.FormalParameter)
	def visit(self, node: ast.FormalParameter, tabs):
		pass


	@visitor.when(ast.Object)
	def visit(self, node: ast.Object, tabs):
		pass


	@visitor.when(ast.Self)
	def visit(self, node: ast.Self, tabs):
		pass


	@visitor.when(ast.Constant)
	def visit(self, node: ast.Constant, tabs):
		pass


	@visitor.when(ast.Integer)
	def visit(self, node: ast.Integer, tabs):
		pass


	@visitor.when(ast.String)
	def visit(self, node: ast.String, tabs):
		pass


	@visitor.when(ast.Boolean)
	def visit(self, node: ast.Boolean, tabs):
		pass


	@visitor.when(ast.Expr)
	def visit(self, node: ast.Expr, tabs):
		pass


	@visitor.when(ast.NewObject)
	def visit(self, node: ast.NewObject, tabs):
		pass


	@visitor.when(ast.IsVoid)
	def visit(self, node: ast.IsVoid, tabs):
		pass


	@visitor.when(ast.Assignment)
	def visit(self, node: ast.Assignment, tabs):
		pass


	@visitor.when(ast.Block)
	def visit(self, node: ast.Block, tabs):
		pass


	@visitor.when(ast.DynamicDispatch)
	def visit(self, node: ast.DynamicDispatch, tabs):
		pass


	@visitor.when(ast.StaticDispatch)
	def visit(self, node: ast.StaticDispatch, tabs):
		pass


	@visitor.when(ast.Let)
	def visit(self, node: ast.Let, tabs):
		pass


	@visitor.when(ast.If)
	def visit(self, node: ast.If, tabs):
		pass


	@visitor.when(ast.WhileLoop)
	def visit(self, node: ast.WhileLoop, tabs):
		pass


	@visitor.when(ast.Case)
	def visit(self, node: ast.Case, tabs):
		pass


	@visitor.when(ast.Action)
	def visit(self, node: ast.Action, tabs):
		pass


	@visitor.when(ast.UnaryOperation)
	def visit(self, node: ast.UnaryOperation, tabs):
		pass


	@visitor.when(ast.IntegerComplement)
	def visit(self, node: ast.IntegerComplement, tabs):
		pass


	@visitor.when(ast.BooleanComplement)
	def visit(self, node: ast.BooleanComplement, tabs):
		pass


	@visitor.when(ast.BinaryOperation)
	def visit(self, node: ast.BinaryOperation, tabs):
		pass


	@visitor.when(ast.Addition)
	def visit(self, node: ast.Addition, tabs):
		pass


	@visitor.when(ast.Subtraction)
	def visit(self, node: ast.Subtraction, tabs):
		pass


	@visitor.when(ast.Multiplication)
	def visit(self, node: ast.Multiplication, tabs):
		pass


	@visitor.when(ast.Division)
	def visit(self, node: ast.Division, tabs):
		pass


	@visitor.when(ast.Equal)
	def visit(self, node: ast.Equal, tabs):
		pass


	@visitor.when(ast.LessThan)
	def visit(self, node: ast.LessThan, tabs):
		pass


	@visitor.when(ast.LessThanOrEqual)
	def visit(self, node: ast.LessThanOrEqual, tabs):
		pass