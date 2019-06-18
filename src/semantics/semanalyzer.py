
"""
# Semantic Analysis

## Checks

1. All identifiers are declared.
2. Types.
3. Inheritance relationships.
4. Classes defined only once.
5. Methods in a class defined only once.
6. Reserved identifiers are not misused.


## Scope

### Identifier Bindings:

Cool Identifier Bindings are introduced by:

* Class declarations (introduce class names)
* Method definitions (introduce method names) – Let expressions (introduce object id’s)
* Formal parameters (introduce object id’s)
* Attribute definitions (introduce object id’s)
* Case expressions (introduce object id’s)

### Class Definitions:

* Cannot be nested.
* Are globally visible throughout the program.
* Class names can be used before they are defined.

### Class Attributes:

* Attribute names are global within the class in which they are defined

### Class Methods:

* Method names have complex rules.
* A method need not be defined in the class in which it is used, but in some parent class.
* Methods may also be redefined (overridden).


## Type System

### Type Operations:

* Type Checking. The process of verifying fully typed programs
* Type Inference. The process of filling in missing type information

### Types in Cool:

1. Class names: Builtins (Int; String; Bool; Object; IO) and User Defined.
2. SELF_TYPE.

### Sub-Typing:

* Types can be thought of as sets of attributes and operations defined on these sets.
* All types are subtypes of the `Object` type.
* Types can inherit from other types other than the `Object` type.
* No type is allowed to inherit from the following types only: `Int`, `Bool`, `String` and `SELF_TYPE`.
* All type relations can be thought of as a tree where `Object` is at the root and all other types branching down from
	it, this is also called the `inheritance tree`.
* A least upper bound (`lub`) relation of two types is their least common ancestor in the inheritance tree.
* Subclasses only add attributes or methods.
* Methods can be redefined but with same type.
* All operations that can be used on type `C` can also be used on type `C'`, where `C'` <= `C`, meaning `C'` is a
	subtype of `C`.

### Typing Methods:

* Method and Object identifiers live in different name spaces.
	+ A method `foo` and an object `foo` can coexist in the same scope.
* Logically, Cool Type Checking needs the following 2 Type Environments:
	+ `O`: a function providing mapping from types to Object Identifiers and vice versa.
	+ `M`: a function providing mapping from types to Method Names and vice versa.
* Due to `SELF_TYPE`, we need to know the class name at all points of Type Checking methods.
	+ `C`: a function providing the name of the current class (Type).

### SELF_TYPE:

`SELF_TYPE` is not a Dynamic Type, it is a Static Type.

`SELF_TYPE` is the type of the `self` parameter in an instance. In a method dispatch, `SELF_TYPE` might be a subtype of
the class in which the subject method appears.

#### Usage:

* `SELF_TYPE` can be used with `new T` expressions.
* `SELF_TYPE` can be used as the return type of class methods.
* `SELF_TYPE` can be used as the type of expressions (i.e. let expressions: `let x : T in expr`).
* `SELF_TYPE` can be used as the type of the actual arguments in a method dispatch.
* `SELF_TYPE` can **not** be used as the type of class attributes.
* `SELF_TYPE` can **not** be used with Static Dispatch (i.e. `T` in `m@T(expr1,...,exprN)`).
* `SELF_TYPE` can **not** be used as the type of Formal Parameters.

#### Least-Upper Bound Relations:

* `lub(SELF_TYPE.c, SELF_TYPE.c) = SELF_TYPE.c`.
* `lub(SELF_TYPE.c, T) = lub(C, T)`.
* `lub(T, SELF_TYPE.c) = lub(C, T)`.


## Semantic Analysis Passes

**[incomplete]**

1. Gather all class names.
2. Gather all identifier names.
3. Ensure no undeclared identifier is referenced.
4. Ensure no undeclared class is referenced.
3. Ensure all Scope Rules are satisfied (see: above).
4. Compute Types in a bottom-up pass over the AST.


## Error Recovery

Two solutions:

1. Assign the type `Object` to ill-typed expressions.
2. Introduce a new type called `No_Type` for use with ill-typed expressions.

Solution 1 is easy to implement and will enforce the type inheritance and class hierarchy tree structures.

Solution 2 will introduce further adjustments. First, every operation will be treated as defined for `No_Type`. Second,
the inheritance tree and class hierarchy will change from being Trees to Graphs. The reason for that is that expressions
will ultimately either be of type `Object` or `No_Type`, which will make the whole representation look like a graph with
two roots.
"""

import sys
sys.path.append('..')

import commons.cool_ast as AST
from commons.settings import *
import commons.visitor as visitor

from semantics.scope import scope
from parsing.parser import CoolParser


#################### SEMANTIC EXCEPTION CLASSES #########################################

class SemanticAnalysisError(Exception):
	pass

class SemanticAnalysisWarning(Warning):
	pass

#########################################################################################



class Semananalyzer:
	"""
	Semananalyzer Class.

	Handles Cool semantics analysis.

	Usage: call 'analyze()' passing in a the output of the parser (AST)
	"""

	def __init__(self):
		"""
		This class serves as a container for the visitors implemented to do 
		semantic analysis
		"""
		pass

	@staticmethod
	def _add_builtin_types(program_ast: AST.Program) -> AST.Program:
		"""
		Initializes the COOL Builtin Classes: Object, IO, Int, Bool and String, and then adds them to the Program AST node.
		:param program_ast: an AST.Program class instance, represents a COOL program AST.
		"""
		global UNBOXED_PRIMITIVE_VALUE_TYPE, UNBOXED_PRIMITIVE_DEFAULT_ZERO, OBJECT_CLASS, IO_CLASS, INTEGER_CLASS, STRING_CLASS, BOOLEAN_CLASS

		if program_ast is None:
			raise SemanticAnalysisError("Program AST cannot be None.")

		if not isinstance(program_ast, AST.Program):
			raise SemanticAnalysisError("Expected argument to be of type AST.Program, but got {} instead.".
													format(type(program_ast)))

		# Object Class
		object_class = AST.Class(name=OBJECT_CLASS, parent=None, features=[
			# Abort method: halts the program.
			AST.ClassMethod(name="abort", formal_params=[], return_type="Object", body=None),

			# Copy method: copies the object.
			AST.ClassMethod(name="copy", formal_params=[], return_type="SELF_TYPE", body=None),

			# type_name method: returns a string representation of the class name.
			AST.ClassMethod(name="type_name", formal_params=[], return_type="String", body=None)
		])

		# IO Class
		io_class = AST.Class(name=IO_CLASS, parent="Object", features=[
			# in_int: reads an integer from stdio
			AST.ClassMethod(name="in_int", formal_params=[], return_type="Int", body=None),

			# in_string: reads a string from stdio
			AST.ClassMethod(name="in_string", formal_params=[], return_type="String", body=None),

			# out_int: outputs an integer to stdio
			AST.ClassMethod(name="out_int",
									formal_params=[AST.FormalParameter("arg", "Int")],
									return_type="SELF_TYPE",
									body=None),

			# out_string: outputs a string to stdio
			AST.ClassMethod(name="out_string",
									formal_params=[AST.FormalParameter("arg", "String")],
									return_type="SELF_TYPE",
									body=None)
		])

		# Int Class
		int_class = AST.Class(name=INTEGER_CLASS, parent=object_class.name, features=[
			# _val attribute: integer un-boxed value
			AST.ClassAttribute(name="_val", attr_type=UNBOXED_PRIMITIVE_DEFAULT_ZERO, init_expr=None)
		])

		# Bool Class
		bool_class = AST.Class(name=BOOLEAN_CLASS, parent=object_class.name, features=[
			# _val attribute: boolean un-boxed value
			AST.ClassAttribute(name="_val", attr_type=UNBOXED_PRIMITIVE_DEFAULT_ZERO, init_expr=None)
		])

		# String Class
		string_class = AST.Class(name=STRING_CLASS, parent=object_class.name, features=[
			# _val attribute: string length
			AST.ClassAttribute(name='_val', attr_type='Int', init_expr=None),

			# _str_field attribute: an un-boxed, untyped string value
			AST.ClassAttribute('_str_field', UNBOXED_PRIMITIVE_DEFAULT_EMPTY, None),

			# length method: returns the string's length
			AST.ClassMethod(name='length', formal_params=[], return_type='Int', body=None),

			# concat method: concatenates this string with another
			AST.ClassMethod(name='concat',
									formal_params=[AST.FormalParameter('arg', 'String')],
									return_type='String',
									body=None),

			# substr method: returns the substring between two integer indices
			AST.ClassMethod(name='substr',
									formal_params=[AST.FormalParameter('arg1', 'Int'), AST.FormalParameter('arg2', 'Int')],
									return_type='String',
									body=None)
		])

		# Built in classes collection
		builtin_classes = (object_class, io_class, int_class, bool_class, string_class)

		# All classes
		all_classes = builtin_classes + program_ast.classes
		
		return AST.Program(classes=all_classes)

	def analyze(self, ast_node):
		"""
		params: ast_node :: AST.Program
		"""
		ast = self._add_builtin_types(ast_node)
		sc = scope(None)
		errs = []
		if not self.visit(ast, sc, errs):
			print('Se produjo un error semantico')
			print('----------------------------')
			for e in errs:
				print(e)

	def orden(self, classes):
		inheritance = { x.name: { y.name:0 for y in classes } for x in classes }
		for clss in classes:
			if clss.parent:
				inheritance[clss.name][clss.parent] = 1
		
		# line = ''
		# for key, val in inheritance.items():
		# 		line = key + ' '
		# 		for v in val.values():
		# 			line += str(v)
		# 		print(line)

		m = {c.name: c for c in classes}
		orden = []
		added = True
		while added:
			added = False
			l = []
			for key, val in inheritance.items():
				count = 0
				for v in val.values():
					count += v
				if count == 0:
					added = True
					orden.append(key)
					l.append(key)
			for val in inheritance.values():
				for name in l:
					val[name] = 0
			for name in l:
				inheritance.pop(name)
		circle = inheritance.keys()
		# print(orden)
		# print(circle)
		return [(m[name], True) for name in orden] + [(m[name], False) for name in circle]

	@visitor.on('node')
	def visit(self, node, scope, errs):
		pass

	@visitor.when(AST.Program)
	def visit(self, prog, scope, errs):
		classes = self.orden(prog.classes)
		for c, v in classes:
			if not v:
				errs.append("can not inherit from {} and form a recursive inheritance at line <NotImplemented>, column <NotImplemented>".format(c.parent))
				return False
			if c.parent:
				if not scope.is_define_type(c.parent):
					errs.append("Cannot inherits from '{}' at line <NotImplemented>, column <NotImplemented>".format(c.parent.name))
					return False
				if c.parent == 'Int' or c.parent == 'Bool' or c.parent == 'String':
					errs.append("Cannot inherits from '{}' at line <NotImplemented>, column <NotImplemented>".format(c.parent.name))
					return False
			if scope.is_define_type(c.name):
				errs.append('Class {} cannot be defined twice at line <NotImplemented>, column <NotImplemented>'.format(c.name))
				return False
			else:
				scope.to_define_type(c.name, c.parent)
		
		scss = {}
		for c, _ in classes:
			if c.parent is None:
				scss[c.name] = scope.createChildScope(c.name)
			else:
				scss[c.name] = scss[c.parent].createChildScope(c.name)

			for feature in c.features:
				if isinstance(feature, AST.ClassAttribute):
					if scss[c.name].is_define_obj(feature.name):
						errs.append("Attribute '{}' cannot be defined twice at line <NotImplemented>, column <NotImplemented>. Type '{}' doesn't exists".format(attr.name, attr.attr_type))
						return False
					else:
						scss[c.name].O(feature.name, feature.attr_type)
				elif isinstance(feature, AST.ClassMethod):
					m_sig = scss[c.name].is_define_method(c.name, feature.name)
					f_sig = tuple([param.param_type for param in feature.formal_params] + [feature.return_type])
					if m_sig and f_sig != m_sig:
						errs.append('Method {} cannot be defined at line <NotImplemented>, column <NotImplemented>'.format(feature.name))
						return False
					else:
						f_tuple = tuple([feature.name]) + f_sig
						scss[c.name].M(c.name, f_tuple)
				
		for c, _ in classes:
			if not self.visit(c, scss[c.name], errs):
				return False
		return True
				

	@visitor.when(AST.Class)
	def visit(self, clss, scope, errs):
		
		if not clss.name in BUILT_IN_CLASSES:
			for feature in clss.features:
				if not self.visit(feature, scope, errs):
					return False
		return True

	@visitor.when(AST.Object)
	def visit(self, o, scope, errs):
		t = scope.is_define_obj(o.name)
		if not t:
			errs.append('Object {} not define'.format(o.name))
			return False
		o.static_type = scope.is_define_obj('self') if t == 'SELF_TYPE' else t
		return True

	@visitor.when(AST.Self)
	def visit(self, s, scope, errs):
		s.static_type = scope.is_define_obj('self')
		return True

	@visitor.when(AST.Assignment)
	def visit(self, Assign, scope, errs):
		if not self.visit(Assign.instance, scope, errs):
			return False
		if not self.visit(Assign.expr, scope, errs):
			return False
		if not scope.inherit(Assign.expr.static_type, Assign.instance.static_type):
			errs.append('Not concorse Type {} and Type {}'.format(Assign.instance.static_type, Assign.expr.static_type))
			return False
		Assign.static_type = Assign.expr.static_type
		return True

	@visitor.when(AST.Boolean)
	def visit(self, boolean, scope, errs):
		boolean.static_type = 'Bool'
		return True

	@visitor.when(AST.Integer)
	def visit(self, integer, scope, errs):
		integer.static_type = 'Int'
		return True

	@visitor.when(AST.String)
	def visit(self, string, scope, errs):
		string.static_type = 'String'
		return True
		
	@visitor.when(AST.NewObject)
	def visit(self, newObj, scope, errs):
		t = scope.is_define_obj('self') if newObj.type == 'SELF_TYPE' else newObj.type
		if not scope.is_define_type(t):
			errs.append('Type {} not define'.format(t))
			return False
		newObj.static_type = t
		return True
			
	@visitor.when(AST.DynamicDispatch)
	def visit(self, ddispatch, scope, errs):
		if not self.visit(ddispatch.instance, scope, errs):
			return False
		for arg in ddispatch.arguments:
			if not self.visit(arg, scope, errs):
				return False
		m = scope.is_define_method(ddispatch.instance.static_type, ddispatch.method)
		if not m:
			errs.append('Method {} not found'.format(ddispatch.method))
			return False
		if len(ddispatch.arguments) != len(m) - 1:
			errs.append('Need same number of params')
			return False
		for i in range(len(ddispatch.arguments)):
			if not scope.inherit(ddispatch.arguments[i].static_type, m[i]):
				errs.append('Types must to be confor')
				return False
		ddispatch.static_type = ddispatch.instance.static_type if m[-1] == 'SELF_TYPE' else m[-1]
		return True

	@visitor.when(AST.StaticDispatch)
	def visit(self, sdispatch, scope, errs):
		if not self.visit(sdispatch.instance, scope, errs):
			return False
		t = scope.is_define_obj('self') if sdispatch.dispatch_type == 'SELF_TYPE' else sdispatch.dispatch_type
		if not scope.is_define_type(t):
			errs.append('Type {} not define'.format(t))
			return False
		if not scope.inherit(sdispatch.instance.static_type, t):
			errs.append('Types must to confor')
			return False
		for arg in sdispatch.arguments:
			if not self.visit(arg, scope, errs):
				return False
		m = scope.is_define_method(sdispatch.instance.static_type, sdispatch.method)
		if not m:
			errs.append('Method {} not found'.format(sdispatch.method))
			return False
		if len(sdispatch.arguments) != len(m) - 1:
			errs.append('Need same number of params')
			return False
		for i in range(len(sdispatch.arguments)):
			if not scope.inherit(sdispatch.arguments[i].static_type, m[i]):
				errs.append('Types must to be confor')
				return False
		sdispatch.static_type = sdispatch.instance.static_type if m[-1] == 'SELF_TYPE' else m[-1]
		return True

	@visitor.when(AST.If)
	def visit(self, cond, scope, errs):
		if not self.visit(cond.predicate, scope, errs):
			return False
		if not cond.predicate.static_type == 'Bool':
			errs.append('Predicate must to be Bool static type')
			return False
		if not self.visit(cond.then_body, scope, errs):
			return False
		if not self.visit(cond.else_body, scope, errs):
			return False
		cond.static_type = scope.join(cond.then_body.static_type, cond.else_body.static_type)
		return True

	@visitor.when(AST.Block)
	def visit(self, block, scope, errs):
		for e in block.expr_list:
			if not self.visit(e, scope, errs):
				return False
		block.static_type = block.expr_list[-1].static_type
		return True
	
	@visitor.when(AST.Let)
	def visit(self, let, scope, errs):
		child = scope.createChildScope()
		for letvar in let.variables:
			if not self.visit(letvar, child, errs):
				return False
		if not self.visit(let.body, child, errs):
			return False
		let.static_type = let.body.static_type
		return True

	@visitor.when(AST.LetVariable)
	def visit(self, letvar, scope, errs):
		t = scope.is_define_obj('self') if letvar.ttype == 'SELF_TYPE' else letvar.ttype
		if not scope.is_define_type(t):
			errs.append('Type {} not define'.format(t))
			return False
		if letvar.initialization:
			if not self.visit(letvar.initialization, scope, errs):
				return False
			if not scope.inherit(letvar.initialization.static_type, t):
				errs.append("Type not confor {} {}". format(letvar.initialization.static_type, t))
				return False
		scope.O(letvar.name, t)
		letvar.static_type = letvar.initialization.static_type if letvar.initialization else t
		return True

	@visitor.when(AST.Case)
	def visit(self, case, scope, errs):
		if not self.visit(case.expr, scope, errs):
			return False
		for act in case.actions:
			if not self.visit(act, scope, errs):
				return False
		static_type = case.actions[0].static_type
		for act in case.actions[1:]:
			static_type = scope.join(static_type, act.static_type)
		case.static_type = static_type
		return True
			
	@visitor.when(AST.Action)
	def visit(self, action, scope, errs):
		t = scope.is_define_obj('self') if action.action_type == 'SELF_TYPE' else action.action_type
		if not scope.is_define_type(t):
			errs.append('Not definde type {}'.format(action.action_type))
			return False
		child = scope.createChildScope()
		child.O(action.name, t)
		if not self.visit(action.body, child, errs):
			return False
		action.static_type = action.body.static_type
		return True

	@visitor.when(AST.WhileLoop)
	def visit(self, loop, scope, errs):
		if not self.visit(loop.predicate, scope, errs):
			return False
		if loop.predicate.static_type != 'Bool':
			errs.append('Predicate must have Bool type')
			return False
		if not self.visit(loop.body, scope, errs):
			return False
		loop.static_type = 'Object'
		return True

	@visitor.when(AST.IsVoid)
	def visit(self, void, scope, errs):
		if not self.visit(void.expr, scope, errs):
			return False
		void.static_type = 'Bool'
		return True
		
	@visitor.when(AST.BooleanComplement)
	def visit(self, bcompl, scope, errs):
		if not self.visit(bcompl.boolean_expr, scope, errs):
			return False
		if not bcompl.boolean_expr.static_type == 'Bool':
			errs.append('Expression have to be Bool type')
			return False
		bcompl.static_type = 'Bool'
		return True

	@visitor.when(AST.LessThan)
	def visit(self, comp, scope, errs):
		if not self.visit(comp.first, scope, errs):
			return False
		if not self.visit(comp.second, scope, errs):
			return False
		if comp.first.static_type != 'Int' or comp.second.static_type != 'Int':
			errs.append('Comparison must to be betuwen to intergers')
			return False
		comp.static_type = 'Bool'
		return True

	@visitor.when(AST.LessThanOrEqual)
	def visit(self, comp, scope, errs):
		if not self.visit(comp.first, scope, errs):
			return False
		if not self.visit(comp.second, scope, errs):
			return False
		if comp.first.static_type != 'Int' or comp.second.static_type != 'Int':
			errs.append('Comparison must to be betuwen to intergers')
			return False
		comp.static_type = 'Bool'
		return True

	@visitor.when(AST.IntegerComplement)
	def visit(self, icompl, scope, errs):
		if not self.visit(icompl.integer_expr, scope, errs):
			return False
		if not icompl.integer_expr.static_type == 'Int':
			errs.append('Expression have to be Int type')
			return False
		icompl.static_type = 'Int'
		return True

	@visitor.when(AST.Addition)
	def visit(self, add, scope, errs):
		if not self.visit(add.first, scope, errs):
			return False
		if not self.visit(add.second, scope, errs):
			return False
		if add.first.static_type != 'Int' or add.second.static_type != 'Int':
			errs.append('Arithmetic must to be betuwen to intergers')
			return False
		add.static_type = 'Int'
		return True

	@visitor.when(AST.Subtraction)
	def visit(self, sub, scope, errs):
		if not self.visit(sub.first, scope, errs):
			return False
		if not self.visit(sub.second, scope, errs):
			return False
		if sub.first.static_type != 'Int' or sub.second.static_type != 'Int':
			errs.append('Arithmetic must to be betuwen to intergers')
			return False
		sub.static_type = 'Int'
		return True

	@visitor.when(AST.Multiplication)
	def visit(self, mul, scope, errs):
		if not self.visit(mul.first, scope, errs):
			return False
		if not self.visit(mul.second, scope, errs):
			return False
		if mul.first.static_type != 'Int' or mul.second.static_type != 'Int':
			errs.append('Arithmetic must to be betuwen to intergers')
			return False
		mul.static_type = 'Int'
		return True

	@visitor.when(AST.Division)
	def visit(self, div, scope, errs):
		if not self.visit(div.first, scope, errs):
			return False
		if not self.visit(div.second, scope, errs):
			return False
		if div.first.static_type != 'Int' or div.second.static_type != 'Int':
			errs.append('Arithmetic must to be betuwen to intergers')
			return False
		div.static_type = 'Int'
		return True

	@visitor.when(AST.Equal)
	def visit(self, eq, scope, errs):
		if not self.visit(eq.first, scope, errs):
			return False
		if not self.visit(eq.second, scope, errs):
			return False
		if (eq.first.static_type == 'Int' or eq.first.static_type == 'String' or eq.first.static_type == 'Bool') and not eq.first.static_type == eq.second.static_type:
			errs.append('equeals must be of the same tipe if are comparet at last on object of basic type')
			return False
		eq.static_type = 'Bool'
		return True

	@visitor.when(AST.ClassAttribute)
	def visit(self, attr, scope, errs):
		t = scope.is_define_obj('self') if attr.attr_type == 'SELF_TYPE' else attr.attr_type
		if not scope.is_define_type(t):
			errs.append('Type {} not define'.format(t))
			return False
		if attr.init_expr:
			if not self.visit(attr.init_expr, scope, errs):
				return False
			if not scope.inherit(attr.init_expr.static_type, t):# and attr.init_expr.static_type != t):
				errs.append('Attribute initialization type does not conform declared type')
				return False
		attr.static_type = t
		return True
		
	@visitor.when(AST.FormalParameter)
	def visit(self, param, scope, errs):
		if not scope.is_define_type(param.param_type):
			errs.append('Type {} not define'.format(param.param_type))
			return False
		param.static_type = param.param_type
		return True
	
	@visitor.when(AST.ClassMethod)
	def visit(self, method, scope, errs):
		for p in method.formal_params:
			if not self.visit(p, scope, errs):
				return False
		child = scope.createChildScope()
		for p in method.formal_params:
			child.O(p.name, p.param_type)
		if not self.visit(method.body, child, errs):
			return False
		t = scope.is_define_obj('self') if method.return_type == 'SELF_TYPE' else method.return_type
		if not scope.is_define_type(t):
			errs.append('Type {} not define'.format(t))
			return False
		if not scope.inherit(method.body.static_type, t):# and method.body.static_type != t):
			errs.append('Method body type does not conform declared type')
			return False
		method.static_type = t
		return True

# s = CoolParser()
# fpath = "/home/luis/Desktop/Cool-Compiler/cool-compiler-hieu-luis-alejandro/examples/type_test.cl"
# ast = None
# with open(fpath, encoding="utf-8") as file:
# 	cool_program_code = file.read()
# 	ast = s.parse(cool_program_code)

# semantic = Semananalyzer()
# semantic.analyze(ast)