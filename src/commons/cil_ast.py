"""
- Type Section, Data Section and Code Section will be represented as an array of Type, Data
and Function respectively.
- First function of the code section will be executed on startup.
- First method of a type will be type constructor.
"""


########################################## AST ##############################################


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


##################################### PROGRAM ############################################################


class Program(AST):
	def __init__(self, type_section, data_section, code_section):
		super(Program, self).__init__()
		self.code_section = code_section
		self.data_section = data_section
		self.type_section = type_section


################################ TYPES, DATAS, STATEMENTS ################################################


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


#################################### FUNCTION ###############################################


class Function(AST):
    def __init__(self, fname, params, locals, instructions):
        self.fname = fname
        self.params = params
        self.locals = locals
        self.instructions = instructions


class ParamDeclaration(AST):
    def __init__(self, name):
        self.name = name


class LocalDeclaration(AST):
    def __init__(self, name):
        self.name = name


#################################### STATEMENTS ##############################################


class Assign(Statement):
    def __init__(self, dest, source):
        self.dest = dest
        self.source = source

#----------- ARITHMETIC

class Arithmetic(Statement):
    def __init__(self, dest, left, right):
        self.dest = dest
        self.left = left
        self.right = right


class Plus(Arithmetic):
    pass


class Minus(Arithmetic):
    pass


class Mult(Arithmetic):
    pass


class Div(Arithmetic):
    pass

#---------- TYPES

class GetAttrib(Statement):
    def __init__(self, dest, instance, attribute):
        self.dest = dest
        self.instance = instance
        self.attribute = attribute


class SetAttrib(Statement):
    def __init__(self, instance, attribute, src):
        self.instance = instance
        self.attribute = attribute
        self.src = src

#---------- ARRAYS

class GetIndex(GetAttrib):
    pass


class SetIndex(SetAttrib):
    pass


################################ MEMORY STATEMENTS ###########################################


class TypeOf(Statement):
    def __init__(self, dest, var):
        self.dest = dest
        self.var = var


class Allocate(Statement):
    def __init__(self, dest, ttype):
        self.dest = dest
        self.ttype = ttype


class Array(Statement):
    def __init__(self, dest, src):
        self.dest = dest
        self.src = src


################################# DISPATCH STATEMENTS, RETURN #################################


class StaticDispatch(Statement):
    def __init__(self, dest, func):
        self.dest = dest
        self.func = func


class DinamicDispatch(Statement):
    def __init__(self, dest, ttype, func):
        self.dest = dest
        self.ttype = ttype
        self.func = func


class ParamDispatch(Statement):
    def __init__(self, name):
        self.name = name


class Return(Statement):
    def __init__(self, value=None):
        self.value = value


################################## JUMP STATEMENTS ###########################################


class Label(Statement):
    def __init__(self, name):
        self.name = name


class Goto(Statement):
    def __init__(self, name):
        self.name = name


class GotoIf(Statement):
    def __init__(self, condition, label):
        self.condition = condition
        self.label = label


######################################## STR STATEMENTS ######################################


class Load(Statement):
    def __init__(self, dest, msg):
        self.dest = dest
        self.msg = msg


class Length(Statement):
    def __init__(self, dest, str_addr):
        self.dest = dest
        self.str_addr = str_addr


class Concat(Statement):
    def __init__(self, dest, head, tail):
        self.dest = dest
        self.head = head
        self.tail = tail


class Substring(Statement):
    def __init__(self, dest, str_addr, pos_left=0, pos_right=-1):
        self.dest = dest
        self.str_addr = str_addr
        self.pos_left = pos_left
        self.pos_right = pos_right


class ToString(Statement):
    def __init__(self, dest, ivalue):
        self.dest = dest
        self.ivalue = ivalue


#################################### IO STATEMENTS ###########################################


class Read(Statement):
    def __init__(self, dest):
        self.dest = dest


class Print(Statement):
    def __init__(self, str_addr):
        self.str_addr = str_addr