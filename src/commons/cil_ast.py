"""
- Type Section, Data Section and Code Section will be represented as an array of Type, Data
and Function respectively.
- First function of the code section will be executed on startup.
- First method of a type will be type constructor.
"""


########################################## AST ####################################################


class AST:
	def __init__(self):
		pass

	@property
	def clsname(self):
		return str(self.__class__.__name__)

	def to_readable(self):
		return "{}".format(self.clsname)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return str(self.to_readable()) + "\n"


##################################### PROGRAM #####################################################


class Program(AST):
	def __init__(self, type_section, data_section, code_section):
		super(Program, self).__init__()
		self.code_section = code_section
		self.data_section = data_section
		self.type_section = type_section

	def to_readable(self):
		return "{}(type={}, data={}, code={})".format(self.clsname, self.type_section, self.data_section, self.code_section)



################################ TYPES, DATAS, STATEMENTS #########################################


class Type(AST):
	def __init__(self, name, attributes, methods):
		self.type_name = name
		self.attributes = attributes
		self.methods = methods

	def to_readable(self):
		return "{}(name={}, attributes={}, methods={})".format(self.clsname, self.type_name, self.attributes, self.methods)


class Data(AST):
	def __init__(self, name, value):
		self.data_name = name
		self.value = value

	def to_readable(self):
		return "{}(name={}, value={})".format(self.clsname, self.data_name, self.value)


class Statement(AST):
	pass


#################################### ATTRIBUTE ###################################################

class TypeFeature(AST):
	pass

class Attribute(TypeFeature):
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def to_readable(self):
		return "{}(name={}, value={})".format(self.clsname, self.name, self.value)


#################################### FUNCTION ####################################################


class Function(TypeFeature):
	def __init__(self, fname, params, vlocals, body):
		self.fname = fname
		self.params = params
		self.vlocals = vlocals
		self.body = body

	def to_readable(self):
		return "{}(fname={}, params={}, locals={}, body={})".format(self.clsname, self.fname, self.params, self.vlocals, self.body)



class ParamDeclaration(AST):
	def __init__(self, name):
		self.name = name

	def to_readable(self):
		return "{}(name={})".format(self.clsname, self.name)


class LocalDeclaration(AST):
	def __init__(self, name):
		self.name = name
		
	def to_readable(self):
		return "{}(name={})".format(self.clsname, self.name)


#################################### STATEMENTS #################################################


class Assign(Statement):
	def __init__(self, dest, source):
		self.dest = dest
		self.source = source
		
	def to_readable(self):
		return "{}(dest={}, source={})".format(self.clsname, self.dest, self.source)

#----------- BinaryOperator

class BinaryOperator(Statement):
	def __init__(self, dest, left, right):
		self.dest = dest
		self.left = left
		self.right = right

	def to_readable(self):
		return "{}(dest={}, left={}, right={})".format(self.clsname, self.dest, self.left, self.right)

class Plus(BinaryOperator):
	pass

class Minus(BinaryOperator):
	pass

class Mult(BinaryOperator):
	pass

class Div(BinaryOperator):
	pass

#---------- COMPARISONS

class Equal(BinaryOperator):
	pass

class LessThan(BinaryOperator):
	pass

class EqualOrLessThan(BinaryOperator):
	pass

#---------- TYPES

class GetAttrib(Statement):
	def __init__(self, dest, instance, attribute):
		self.dest = dest
		self.instance = instance
		self.attribute = attribute

	def to_readable(self):
		return "{}(dest={}, instance={}, attribute={})".format(self.clsname, self.dest, self.instance, self.attribute)

class SetAttrib(Statement):
	def __init__(self, instance, attribute, src):
		self.instance = instance
		self.attribute = attribute
		self.src = src

	def to_readable(self):
		return "{}(dest={}, instance={}, attribute={})".format(self.clsname, self.src, self.instance, self.attribute)

#---------- ARRAYS

class GetIndex(GetAttrib):
	pass


class SetIndex(SetAttrib):
	pass


################################ MEMORY STATEMENTS ##############################################


class TypeOf(Statement):
	def __init__(self, dest, instance):
		self.dest = dest
		self.instance = instance
		
	def to_readable(self):
		return "{}(dest={}, instance={})".format(self.clsname, self.dest, self.instance)



class Allocate(Statement):
	def __init__(self, dest, ttype):
		self.dest = dest
		self.ttype = ttype

	def to_readable(self):
		return "{}(dest={}, type={})".format(self.clsname, self.dest, self.ttype)


class Array(Statement):
	def __init__(self, dest, src):
		self.dest = dest
		self.src = src
		
	def to_readable(self):
		return "{}(dest={}, src={})".format(self.clsname, self.dest, self.src)



################################# DISPATCH STATEMENTS, RETURN #################################


class StaticDispatch(Statement):
	def __init__(self, dest, f):
		self.dest = dest
		self.f = f

	def to_readable(self):
		return "{}(dest={}, function={})".format(self.clsname, self.dest, self.f)


class DinamicDispatch(Statement):
	def __init__(self, dest, ttype, f):
		self.dest = dest
		self.ttype = ttype
		self.f = f

	def to_readable(self):
		return "{}(dest={}, type={}, function={})".format(self.clsname, self.dest, self.ttype, self.f)


class ParamDispatch(Statement):
	def __init__(self, name):
		self.name = name

	def to_readable(self):
		return "{}(name={})".format(self.clsname, self.name)


class Return(Statement):
	def __init__(self, value=None):
		self.value = value

	def to_readable(self):
		return "{}(value={})".format(self.clsname, self.value)

################################## JUMP STATEMENTS ###########################################


class Label(Statement):
	def __init__(self, name):
		self.name = name

	def to_readable(self):
		return "{}(name={})".format(self.clsname, self.name)

class Goto(Statement):
	def __init__(self, name):
		self.name = name

	def to_readable(self):
		return "{}(name={})".format(self.clsname, self.name)

class GotoIf(Statement):
	def __init__(self, condition, label):
		self.condition = condition
		self.label = label

	def to_readable(self):
		return "{}(condition={}, label={})".format(self.clsname, self.condition, self.label)

######################################## STR STATEMENTS ######################################


class Load(Statement):
	def __init__(self, dest, msg):
		self.dest = dest
		self.msg = msg

	def to_readable(self):
		return "{}(dest={}, msg={})".format(self.clsname, self.dest, self.msg)



class Length(Statement):
	def __init__(self, dest, str_addr):
		self.dest = dest
		self.str_addr = str_addr

	def to_readable(self):
		return "{}(dest={}, str_addr={})".format(self.clsname, self.dest, self.str_addr)


class Concat(Statement):
	def __init__(self, dest, first, second):
		self.dest = dest
		self.first = first
		self.second = second

	def to_readable(self):
		return "{}(dest={}, first={}, second={})".format(self.clsname, self.dest, self.first, self.second)


class Substring(Statement):
	def __init__(self, dest, str_addr, pos_left=0, pos_right=-1):
		self.dest = dest
		self.str_addr = str_addr
		self.pos_left = pos_left
		self.pos_right = pos_right

	def to_readable(self):
		return "{}(dest={}, str={}, left={}, right={})".format(self.clsname, self.dest, self.str_addr, self.pos_left, self.pos_right)


class ToString(Statement):
	def __init__(self, dest, num):
		self.dest = dest
		self.num = num

	def to_readable(self):
		return "{}(dest={}, num={})".format(self.clsname, self.dest, self.num)


#################################### IO STATEMENTS ###########################################


class Read(Statement):
	def __init__(self, dest):
		self.dest = dest

	def to_readable(self):
		return "{}(dest={})".format(self.clsname, self.dest)


class Print(Statement):
	def __init__(self, str_addr):
		self.str_addr = str_addr
		
	def to_readable(self):
		return "{}(str_addr={})".format(self.clsname, self.str_addr)