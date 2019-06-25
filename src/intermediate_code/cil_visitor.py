import sys
sys.path.append('..')

import commons.cool_ast as ast
import commons.cil_ast as cil
import commons.visitor as visitor
from commons.settings import *
from intermediate_code.name_map import NameMap


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
		self.name_map = None		# Store that contains cool name -> cil name mappings

		# Attributes index map
		self.ind_map = {}

		# Methods index map
		self.mth_map = {}

		# Counters to make variable's names unique
		self.internal_var_count = 0			# LOCAL variables
		self.internal_label_count = 0			# LABELs

		# Class depth dictionary used to analyze Case expressions
		self.class_depth = {}

		# Inheritance graph and root node
		self.inherit_graph = tuple()

		# Add static code
		self.add_built_ins()


	def add_built_ins(self):
		# Add static types, functions and string constants
		self.empty_string = self.register_data("")

		self.dottype.append(cil.Type(VOID_TYPE, [], []))
		

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
		self.dottype.append(ttype)

	#---------- .DATA

	def register_data(self, value):
		vname = f'data_{len(self.dotdata)}'
		data_node = cil.Data(vname, value)
		self.dotdata.append(data_node)
		return data_node.dest

	#---------- .CODE

	def build_internal_vname(self, vname):
		vname = f'_{vname}_{self.internal_var_count}'
		return vname

	def register_internal_local(self):
		return self.register_local('internal')

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

	def build_new_object(self, dest, ttype):
		self.register_instruction(cil.Allocate, dest, ttype)
		self.register_instruction(cil.PushParam, dest)
		self.register_instruction(cil.Call, dest, f'{ttype}_{INIT_CIL_SUFFIX}')
		self.register_instruction(cil.PopParam, dest)

	#---------- CLASS HIERARCHY

	def build_inheritance_graph_and_class_depth(self, program: ast.Program):
		g = {}
		root = None

		# Initialize class depth dictionary
		for c in program.classes:
			self.class_depth[c.name] = 0
			g[c.name] = []

		for klass in program.classes:
			if klass.parent:
				# Build inheritance graph
				g[klass.parent].append(klass)

				# Build the class depth dictionary
				self.class_depth[klass.name] = self.class_depth[klass.parent] + 1

			if klass.name == OBJECT_CLASS:
				root = klass

		self.inherit_graph = g, root

	# ======================================================================


	@visitor.on('node')
	def visit(self, node):
		return "This hides pylint's errors about visit return type"


################################ PROGRAM, TYPE AND OBJECT ##############################



	@visitor.when(ast.Program)
	def visit(self, node: ast.Program):
		#------- Build the inheritance graph and class depth dictionary used to visit Case expressions
		self.build_inheritance_graph_and_class_depth(node)
		childs, root = self.inherit_graph

		visited = {}
		# Initialize visited dict for class visitor
		for klass in node.classes:
			visited[klass.name] = False

		#------- Traverse the class hierarchy using DFS and visit the classes
		def dfs(node, attrs, methods):
			if visited[node.name]:
				return

			node.inherited_attrs = attrs.copy()
			node.inherited_methods = methods.copy()

			new_type = self.visit(node)
			visited[node.name] = True
			self.register_type(new_type)

			for klass in childs[node.name]:
				dfs(klass, new_type.attributes, new_type.methods)

		dfs(root, [], [])

		# Replace the methods and attributes references by their offsets
		for func in self.dotcode:
			for inst in func.body:
				if isinstance(inst, cil.VCall):
					inst.f = self.mth_map[inst.f]
				if (isinstance(inst, cil.SetAttrib) or isinstance(inst, cil.GetAttrib)) \
				 and isinstance(inst.attribute, str):
					inst.attribute = self.ind_map[inst.attribute]

		return cil.Program(self.dottype, self.dotdata, self.dotcode)


	@visitor.when(ast.Class)
	def visit(self, node: ast.Class):
		"""
		Translate the COOL Class to a CIL Type.
		At the same time build an initializer function for that Type.
		"""

		self.current_class_name = node.name

		attributes = node.inherited_attrs
		methods = node.inherited_methods

		# Store the offset of inherited atributes and methods
		for i in range(len(attributes)):
			self.ind_map[f'{self.current_class_name}_{attributes[i].name[attributes[i].name.index("_")+1:]}'] = i
		for i in range(len(methods)):
			self.mth_map[f'{self.current_class_name}_{methods[i].name}'] = i
			# If the method will be redefined, the offset will be replaced.

		# Translate all the properties (COOL) into attributes (CIL)
		# and build an initializer function
		self.localvars = []
		self.instructions = []
		self.internal_var_count = 0
		self.current_function_name = f'{self.current_class_name}_{INIT_CIL_SUFFIX}'

		# Build the initializer function and attributes list
		ind = len(attributes)
		for feature in node.features:
			if isinstance(feature, ast.ClassAttribute):
				feature.index = ind
				attributes.append(self.visit(feature))
				ind += 1

		# Register the initializer function
		self.register_instruction(cil.Return, LOCAL_SELF_NAME)
		func = cil.Function(self.current_function_name, [cil.ArgDeclaration(LOCAL_SELF_NAME)], self.localvars, self.instructions)
		self.register_function(func)

		# Translate all Class Methods (COOL) into Type Methods (CIL)
		# and the functions associated will be automatically registered by the visitor
		ind = len(methods)
		for feature in node.features:
			if isinstance(feature, ast.ClassMethod):
				feature.index = ind

				# Check if this method is being redefined
				for i in range(len(methods)):
					if methods[i].name == feature.name:
						# If it's being redefined, use the offset of the function already defined
						feature.index = i
						del methods[i]
						ind -= 1
						break

				method = self.visit(feature)
				methods.insert(feature.index, method)
				ind += 1

		return cil.Type(node.name, attributes, methods)


	@visitor.when(ast.ClassAttribute)
	def visit(self, node: ast.ClassAttribute):
		if node.init_expr:
			rname = self.visit(node.init_expr)
			self.register_instruction(cil.SetAttrib, LOCAL_SELF_NAME, node.index, rname)
		elif node.attr_type == UNBOXED_PRIMITIVE_DEFAULT_ZERO:
			self.register_instruction(cil.SetAttrib, LOCAL_SELF_NAME, node.index, 0)
		elif node.attr_type == UNBOXED_PRIMITIVE_DEFAULT_EMPTY:
			self.register_instruction(cil.SetAttrib, LOCAL_SELF_NAME, node.index, self.empty_string)
		else:
			_temp = self.register_internal_local()
			if node.attr_type == INTEGER_CLASS:
				self.build_new_object(_temp, INTEGER_CLASS)
			elif node.attr_type == BOOLEAN_CLASS:
				self.build_new_object(_temp, BOOLEAN_CLASS)
			elif node.attr_type == STRING_CLASS:
				self.build_new_object(_temp, STRING_CLASS)
			else:
				self.register_instruction(cil.Allocate, _temp, VOID_TYPE)

			self.register_instruction(cil.SetAttrib, LOCAL_SELF_NAME, node.index, _temp)

		self.ind_map[f'{self.current_class_name}_{node.name}'] = node.index
		return cil.Attribute(f'{self.current_class_name}_{node.name}')


	@visitor.when(ast.ClassMethod)
	def visit(self, node: ast.ClassMethod):
		self.localvars = []
		self.instructions = []
		self.internal_var_count = 0
		self.current_function_name = f'{self.current_class_name}_{node.name}'

		# Reset the name mappings
		self.name_map = NameMap()

		#---- Arguments

		# Self argument
		arguments = [cil.ArgDeclaration(LOCAL_SELF_NAME)]

		# User defined arguments
		for formal_param in node.formal_params:
			arguments.append(self.visit(formal_param))

			
		#----- Function's body
		if self.current_class_name in BUILT_IN_CLASSES:
			# If the current class is a Built-In class then leave the method implementation for the next phase
			pass
		else:
			return_val = self.visit(node.body)
			self.register_instruction(cil.Return, return_val)


		#----- Register the function and return the corresponding method node
		func = cil.Function(self.current_function_name, arguments, self.localvars, self.instructions)
		self.register_function(func)

		# Register the method's offset index
		self.mth_map[func.name] = node.index

		return cil.Method(node.name, func.name)


	@visitor.when(ast.FormalParameter)
	def visit(self, node: ast.FormalParameter):
		self.name_map.define_variable(node.name, f'_{node.name}')
		return cil.ArgDeclaration(f'_{node.name}')


	################################## INSTANCES ##############################


	@visitor.when(ast.Object)
	def visit(self, node: ast.Object):
		obj_vname = self.name_map.get_cil_name(node.name)
		if obj_vname:
			return obj_vname
		else:
			vname = self.register_local(node.name)
			attribute_cil_name = f'{self.current_class_name}_{node.name}'
			self.register_instruction(cil.GetAttrib, vname, LOCAL_SELF_NAME, attribute_cil_name)

			return vname 


	@visitor.when(ast.Self)
	def visit(self, node: ast.Self):
		return LOCAL_SELF_NAME


	################################## CONSTANTS ##############################



	@visitor.when(ast.Integer)
	def visit(self, node: ast.Integer):
		boxed_int = self.register_internal_local()
		self.register_instruction(cil.Allocate, boxed_int, INTEGER_CLASS)
		self.register_instruction(cil.SetAttrib, boxed_int, 0, node.content)
		return boxed_int


	@visitor.when(ast.String)
	def visit(self, node: ast.String):
		data_vname = self.register_data(node.content)
		boxed_string = self.register_internal_local()
		boxed_int = self.register_internal_local()
		self.register_instruction(cil.Allocate, boxed_int, INTEGER_CLASS)
		self.register_instruction(cil.SetAttrib, boxed_int, 0, len(node.content))

		self.register_instruction(cil.Allocate, boxed_string, STRING_CLASS)
		self.register_instruction(cil.SetAttrib, boxed_string, 0, boxed_int)
		self.register_instruction(cil.SetAttrib, boxed_string, 1, data_vname)
		return boxed_string


	@visitor.when(ast.Boolean)
	def visit(self, node: ast.Boolean):
		boxed_bool = self.register_internal_local()
		self.register_instruction(cil.Allocate, boxed_bool, BOOLEAN_CLASS)
		if node.content:
			self.register_instruction(cil.SetAttrib, boxed_bool, 0, 1)
		else:
			self.register_instruction(cil.SetAttrib, boxed_bool, 0, 0)
		return boxed_bool


	################################## EXPRESSIONS ##############################


	@visitor.when(ast.NewObject)
	def visit(self, node: ast.NewObject):
		vname = self.register_internal_local()
		_temp = self.register_internal_local()

		self.register_instruction(cil.Allocate, vname, node.type)
		self.register_instruction(cil.PushParam, vname)
		self.register_instruction(cil.Call, _temp, f'{node.type}_{INIT_CIL_SUFFIX}')
		self.register_instruction(cil.PopParam, vname)
		return vname


	@visitor.when(ast.IsVoid)
	def visit(self, node: ast.IsVoid):
		# LOCAL <isvoid.value>
		# LOCAL <expr.locals>
		# LOCAL <temp_var>
		# 	...
		# <expr.code>
		# ARG <expr.value>
		# <isvoid.value> = Call isvoid

		# <.locals>
		value = self.register_internal_local()

		# <.code>
		expr_val = self.visit(node.expr)
		self.register_instruction(cil.PushParam, expr_val)
		self.register_instruction(cil.Call, value, "isvoid")
		self.register_instruction(cil.PopParam, expr_val)

		return value 

	@visitor.when(ast.Assignment)
	def visit(self, node: ast.Assignment):
		rname = self.visit(node.expr)

		cil_name = self.name_map.get_cil_name(node.instance.name)
		# If a name mapping was found, the destination is a local variable, return expression.value because there's no need to make another LOCAL

		if cil_name:
			self.register_instruction(cil.Assign, cil_name, rname)
		else:
			# If no name was found, the destination is a property of 'self', assign using Setattr node
			attribute_cil_name = f'{self.current_class_name}_{node.instance.name}'
			self.register_instruction(cil.SetAttrib, LOCAL_SELF_NAME, attribute_cil_name, rname)
		return rname


	@visitor.when(ast.Block)
	def visit(self, node: ast.Block):
		# <expr1.locals>
		# 	..
		# <exprN.locals>
		#
		# <expr1.code>
		#  ..
		# <exprN.code>
		# <exprN.value> is the value of the block expression

		block_value = None
		for expr in node.expr_list:
			block_value = self.visit(expr)
		return block_value


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
		self.name_map = self.name_map.create_child_scope()
		for variable in node.variables:
			self.visit(variable)

		# <.code>
		res_vname = self.visit(node.body)
		self.name_map.exit_child_scope()

		return res_vname


	@visitor.when(ast.LetVariable)
	def visit(self, node: ast.LetVariable):
		var_name = ""

		if node.initialization:
			var_name = self.visit(node.initialization)
		else:
			var_name = self.register_local(node.name)

			if node.ttype == INTEGER_CLASS:
				self.build_new_object(var_name, INTEGER_CLASS)
			elif node.ttype == BOOLEAN_CLASS:
				self.build_new_object(var_name, BOOLEAN_CLASS)
			elif node.ttype == STRING_CLASS:
				self.build_new_object(var_name, STRING_CLASS)
			elif node.ttype == UNBOXED_PRIMITIVE_DEFAULT_ZERO:
				self.register_instruction(cil.SetAttrib, LOCAL_SELF_NAME, node.index, 0)
			elif node.ttype == UNBOXED_PRIMITIVE_DEFAULT_EMPTY:
				self.register_instruction(cil.SetAttrib, LOCAL_SELF_NAME, node.index, self.empty_string)
			else:
				self.register_instruction(cil.Allocate, var_name, VOID_TYPE)

		self.name_map.define_variable(node.name, var_name)


	@visitor.when(ast.If)
	def visit(self, node: ast.If):
		# LOCAL <if.value>
		# 	<condition.locals>
		# 	<else.locals>
		# 	<then.locals>
		# 		...
		# 	<condition.body>
		# condition-unboxed = GetAttr <condition.value> _value
		# if condition-unboxed GOTO then_lbl
		# 	<else.code>
		# <if.value> = <else.value>
		# GOTO continue_lbl
		# LABEL then_lbl:
		# 	<then.code>
		# <if.value> = <then.value>
		# LABEL continue_lbl:

		# <.locals>
		if_value = self.register_internal_local()
		condition_unboxed = self.register_internal_local()
		then_lbl = self.define_internal_label()
		continue_lbl = self.define_internal_label()

		# <.body>
		condition_value = self.visit(node.predicate)
		self.register_instruction(cil.GetAttrib, condition_unboxed, condition_value, 0)
		self.register_instruction(cil.IfGoto, condition_unboxed, then_lbl)
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
		# condition-unboxed = GetAttr <condition.value> _value
		# if condition-unboxed GOTO body_lbl
		# GOTO continue_lbl
		# LABEL body_lbl
		# 	<body.code>
		# GOTO start_lbl
		# LABEL continue_lbl
		# <while.value> = 'VOID_TYPE'

		# <.locals>
		while_value = self.register_internal_local()
		condition_unboxed = self.register_internal_local()
		start_lbl = self.define_internal_label()
		body_lbl = self.define_internal_label()
		continue_lbl = self.define_internal_label()

		# <.code>
		self.register_instruction(cil.Label, start_lbl)
		condition_value = self.visit(node.predicate)		# Generate <condition.body> and <condition.locals>
		self.register_instruction(cil.GetAttrib, condition_unboxed, condition_value, 0)
		self.register_instruction(cil.IfGoto, condition_unboxed, body_lbl)
		self.register_instruction(cil.Goto, continue_lbl)
		self.register_instruction(cil.Label, body_lbl)
		self.visit(node.body)
		self.register_instruction(cil.Goto, start_lbl)
		self.register_instruction(cil.Label, continue_lbl)
		self.register_instruction(cil.Allocate, while_value, VOID_TYPE)

		return while_value


	@visitor.when(ast.Case)
	def visit(self, node: ast.Case):
		# Sort types by their depths in the class hierarchy
		actions = list(node.actions)
		actions.sort(key = lambda x: self.class_depth[x.action_type], reverse = True)

		# <.locals>
		_temp = self.register_internal_local()
		expr_type = self.register_local("expression_type")
		case_value = self.register_internal_local()
		
		# Labels
		labels = []
		for _ in node.actions:
			labels.append(self.define_internal_label())
		end_label = self.define_internal_label()

		# <.code>
		expr_value = self.visit(node.expr)
		self.register_instruction(cil.TypeOf, expr_type, expr_value)
		for i in range(len(actions)):
			self.register_instruction(cil.PushParam, actions[i].action_type)
			self.register_instruction(cil.PushParam, expr_type)
			# Call conforms function : (typex, typey) -> typex <= typey
			self.register_instruction(cil.Call, _temp, CONFORMS_FUNC)
			self.register_instruction(cil.PopParam, None)
			self.register_instruction(cil.PopParam, None)
			self.register_instruction(cil.IfGoto, _temp, labels[i])

		# TODO: maybe call some function to show runtime error ?

		for i in range(len(actions)):
			self.register_instruction(cil.Label, labels[i])
			self.name_map.define_variable(actions[i].name, expr_value)
			self.name_map = self.name_map.create_child_scope()
			expr_i = self.visit(actions[i])
			self.name_map.exit_child_scope()
			self.register_instruction(cil.Assign, case_value, expr_i)
			self.register_instruction(cil.Goto, end_label)
			
		self.register_instruction(cil.Label, end_label)
		return case_value


	@visitor.when(ast.Action)
	def visit(self, node: ast.Action):
		return self.visit(node.body)


	################################# DISPATCHS #######################################


	@visitor.when(ast.DynamicDispatch)
	def visit(self, node: ast.DynamicDispatch):
		instance_vname = self.visit(node.instance)
		ttype = self.register_internal_local()
		result = self.register_internal_local()

		# Save the params to do Pop after calling the function
		pops = []
		for i in range(len(node.arguments)-1, -1, -1):
			param = node.arguments[i]
			param_vname = self.visit(param)
			self.register_instruction(cil.PushParam, param_vname)
			pops.append(param_vname)

		# Instance
		self.register_instruction(cil.PushParam, instance_vname)

		# Compute instance's type
		self.register_instruction(cil.TypeOf, ttype, instance_vname)

		# Call the function
		method_name = f'{node.instance.static_type}_{node.method}'
		self.register_instruction(cil.VCall, result, ttype, method_name)
		self.register_instruction(cil.PopParam, instance_vname)

		# Pop the arguments
		for i in range(len(pops)-1, -1, -1):
			self.register_instruction(cil.PopParam, pops[i])

		return result

	@visitor.when(ast.StaticDispatch)
	def visit(self, node: ast.StaticDispatch):
		instance_vname = self.visit(node.instance)
		result = self.register_internal_local()

		# Save the params to do Pop after calling the function
		pops = []
		for i in range(len(node.arguments)-1, -1, -1):
			param = node.arguments[i]
			param_vname = self.visit(param)
			self.register_instruction(cil.PushParam, param_vname)
			pops.append(param_vname)

		# Instance
		self.register_instruction(cil.PushParam, instance_vname)

		# Call the function
		method_name = f'{node.instance.static_type}_{node.method}'
		self.register_instruction(cil.VCall, result, node.dispatch_type, method_name)
		self.register_instruction(cil.PopParam, instance_vname)


		# Pop the arguments
		for i in range(len(pops)-1, -1, -1):
			self.register_instruction(cil.PopParam, pops[i])

		return result


	################################ UNARY OPERATIONS ##################################


	@visitor.when(ast.IntegerComplement)
	def visit(self, node: ast.IntegerComplement):
		# <.locals>
		unboxed_val = self.register_internal_local()
		_temp = self.register_internal_local()
		result = self.register_internal_local()

		# <.code>
		boxed_val = self.visit(node.integer_expr)
		self.register_instruction(cil.GetAttrib, unboxed_val, boxed_val, 0)
		self.register_instruction(cil.Minus, _temp, 0, unboxed_val)
		self.register_instruction(cil.Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.SetAttrib, result, 0, _temp)
		return result


	@visitor.when(ast.BooleanComplement)
	def visit(self, node: ast.BooleanComplement):
		# <.locals>
		unboxed_val = self.register_internal_local()
		_temp = self.register_internal_local()
		result = self.register_internal_local()

		# <.code>
		boxed_val = self.visit(node.boolean_expr)
		self.register_instruction(cil.GetAttrib, unboxed_val, boxed_val, 0)
		self.register_instruction(cil.Minus, _temp, 1, unboxed_val)
		self.register_instruction(cil.Allocate, result, BOOLEAN_CLASS)
		self.register_instruction(cil.SetAttrib, result, 0, _temp)
		return result


	################################ BINARY OPERATIONS ##################################


	@visitor.when(ast.Addition)
	def visit(self, node: ast.Addition):
		# <.locals>
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		# <.code>
		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.GetAttrib, first_val, first_boxed, 0)
		self.register_instruction(cil.GetAttrib, second_val, second_boxed, 0)
		self.register_instruction(cil.Plus, _temp, first_val, second_val)
		self.register_instruction(cil.Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.SetAttrib, result, 0, _temp)
		return result


	@visitor.when(ast.Subtraction)
	def visit(self, node: ast.Subtraction):
		# <.locals>
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		# <.code>
		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.GetAttrib, first_val, first_boxed, 0)
		self.register_instruction(cil.GetAttrib, second_val, second_boxed, 0)
		self.register_instruction(cil.Minus, _temp, first_val, second_val)
		self.register_instruction(cil.Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.SetAttrib, result, 0, _temp)
		return result


	@visitor.when(ast.Multiplication)
	def visit(self, node: ast.Multiplication):
		# <.locals>
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		# <.code>
		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.GetAttrib, first_val, first_boxed, 0)
		self.register_instruction(cil.GetAttrib, second_val, second_boxed, 0)
		self.register_instruction(cil.Mult, _temp, first_val, second_val)
		self.register_instruction(cil.Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.SetAttrib, result, 0, _temp)
		return result


	@visitor.when(ast.Division)
	def visit(self, node: ast.Division):
		# <.locals>
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		# <.code>
		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.GetAttrib, first_val, first_boxed, 0)
		self.register_instruction(cil.GetAttrib, second_val, second_boxed, 0)
		self.register_instruction(cil.Div, _temp, first_val, second_val)
		self.register_instruction(cil.Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.SetAttrib, result, 0, _temp)
		return result


	@visitor.when(ast.Equal)
	def visit(self, node: ast.Equal):
		# <.locals>
		_temp = self.register_internal_local()
		result = self.register_internal_local()

		# <.code>
		first_val = self.visit(node.first)
		second_val = self.visit(node.second)
		self.register_instruction(cil.Equal, _temp, first_val, second_val)
		self.register_instruction(cil.Allocate, result, BOOLEAN_CLASS)
		self.register_instruction(cil.SetAttrib, result, 0, _temp)
		return result


	@visitor.when(ast.LessThan)
	def visit(self, node: ast.LessThan):
		# <.locals>
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		# <.code>
		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.GetAttrib, first_val, first_boxed, 0)
		self.register_instruction(cil.GetAttrib, second_val, second_boxed, 0)
		self.register_instruction(cil.LessThan, _temp, first_val, second_val)
		self.register_instruction(cil.Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.SetAttrib, result, 0, _temp)
		return result


	@visitor.when(ast.LessThanOrEqual)
	def visit(self, node: ast.LessThanOrEqual):
		# <.locals>
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		# <.code>
		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.GetAttrib, first_val, first_boxed, 0)
		self.register_instruction(cil.GetAttrib, second_val, second_boxed, 0)
		self.register_instruction(cil.EqualOrLessThan, _temp, first_val, second_val)
		self.register_instruction(cil.Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.SetAttrib, result, 0, _temp)
		return result


#----------- TESTS
# from parsing.parser import CoolParser
# from semantics.semanalyzer import Semananalyzer

# s = CoolParser()
# c = CILVisitor()
# sem = Semananalyzer()

# fpath = "..\..\examples\\arith.cl"
# with open(fpath, encoding="utf-8") as file:
# 	code = file.read()
# 	test = s.parse(code)
# 	test = sem.analyze(test)
# 	print(test)
# 	print(c.visit(test))
# 	# for c, k in c.class_depth.items():
# 	# 	print(c, k)