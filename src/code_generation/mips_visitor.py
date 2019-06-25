
"""
Registers $v0 and $v1 are used to return values from functions.
Registers $t0 – $t9 are caller-saved registers that are used to
hold temporary quantities that need not be preserved across calls
Registers $s0 – $s7 (16–23) are callee-saved registers that hold long-lived
values that should be preserved across calls. They are preserved across calls
Register $gp is a global pointer that points to the middle of a 64K block
of memory in the static data segment. Preserve across calls
Register $fp is the frame pointer. Register $fp is saved by every procedure
that allocates a new stack frame.Preserve across calls
Register $sp is the stack pointer, which points to the last location on
the stack(Points to Free Memory). Preserve across calls
Register $ra only needs to be saved if the callee itself makes a call.
Register $s0 <- Prototypes table
Register $s1 <- Class Names table
Register $s2 <- Class parents table

0($fp): some local variable
4(%fp): old $ra
8(%fp): old $fp
12(%fp): 1st argument Self
.....

	Class Name table layout
offset 0 - "Class1"
offset 4 - "Class2"
offset 8 - "Class3"
.....

	Prototypes Table layout
offset 0 - protObj1
offset 4 - Obj1_init
offset 8 - protObj2
offset 12 - Obj2_init
.....

	Dispatch Table layout:
offset 0 - addres of method m0
offset 1 - addres of method m1
.....

  Prototype layout:
offset 0 - Class tag : int that identifies the class of the object
offset 4 - Object size :(in 32-bit words) = 12 + 4 * (number of attributes)
offset 8 - Dispatch pointer : pointer to the table of virtual methods
offset 12. . . Attributes
"""

import sys
sys.path.append('..')

import commons.cil_ast as cil
import commons.visitor as visitor
from commons.settings import *




class MipsVisitor:
	"""
	Mips Visitor Class.

	This visitor will process the AST of a CIL generated and return a file with the mips code.
	"""

	def __init__(self):

		self.offset = dict()
		self.type_index = []
		self.dispatchtable_code = []
		self.prototypes_code = []


	# ======================================================================
	# =[ UTILS ]============================================================
	# ======================================================================


	def push(self):
		self.write_file('sw $a0 0($sp)')
		self.write_file('addiu $sp $sp -4')

	def pop(self, dest=None):
		self.write_file(f'addiu $sp $sp 4')


	def write_file(self, msg, mode = "a", tabbed=True):
		f = open("mips_code.asm", mode)
		f.write("{}{}\n".format("\t" if tabbed else "", msg))
		f.close()

	def allocate_memory(self,size, register=False):
		if register:
			self.write_file('move $a0 {}'.format(size))
		else:
			self.write_file('li $a0 {}'.format(size))
		self.write_file('li $v0 9')
		self.write_file('syscall')

	# ======================================================================

	@visitor.on('node')
	def visit(self, node):
		pass


#################################### PROGRAM #################################


	@visitor.when(cil.Program)
	def visit(self, node: cil.Program):
		self.write_file('', "w")

		self.write_file('.data', tabbed = False)
		# Generate data section
		for data in node.data_section:
			self.visit(data)

		# Declare class name strings and map class index
		for i in range(len(node.type_section)):
			self.type_index.append(node.type_section[i].type_name)
			self.write_file('classname_{}: .asciiz \"{}\"'.format(node.type_section[i].type_name,node.type_section[i].type_name))

		# Declare error mensages
		self.write_file('\n########## Error messages ##########\n')
		self.write_file('_index_negative_msg: .asciiz Index to substr is negative')
		self.write_file('_index_out_msg: .asciiz Index out range exeption ')
		self.write_file('_abort_msg: Execution aborted')
		self.write_file('_div_error_msg: Invalid Operation exeption')


		# Declare void type
		self.write_file('classname_void: .asciiz \"\"')

		# Text section
		self.write_file('\n.text')
		self.entry()

		self.write_file('\n########## STATIC FUNCTIONS ##########\n')
		# OBJECT
		self.object_abort()
		self.object_copy()
		self.object_typename()
		# STRING
		self.string_length()
		self.string_concat()
		self.string_substr()
		# IO
		self.io_in_int()
		self.io_in_string()
		self.io_out_int()
		self.io_out_string()
		self.write_file('######################################\n')

		for t in node.type_section:
			self.visit(t)

		# Generate method that creates classes's name table
		self.write_file('function_build_class_name_table:', tabbed=False)
		self.allocate_memory(len(node.type_section) * 4)
		self.write_file('move $s1 $v0') # save the address of the table in a register
		for i in range(len(node.type_section)):
			self.write_file('la $t1 classname_{}'.format(node.type_section[i].type_name))
			self.write_file('sw $t1 {}($s1)'.format(4 * i))
		self.write_file('')


		# Generate method that allocates memory for prototypes table
		self.write_file('function_allocate_prototypes_table:', tabbed=False)
		self.allocate_memory(8 * len(self.type_index))
		self.write_file('move $s0 $v0') # save the address of the table in a register
		self.write_file('')

		# Generate method that allocates memory for parents prototypes table
		self.write_file('function_allocate_parents_prototypes_table:', tabbed=False)
		self.allocate_memory(4 * len(self.type_index))
		self.write_file('move $s2 $v0') # save the address of the table in a register
		self.write_file('')


		# Generate mips method that builds prototypes
		self.write_file('function_build_prototypes:', tabbed=False)
		for ins in self.prototypes_code:
			self.write_file(ins)
		self.write_file('')

		# Generate mips method that builds dispatch tables
		self.write_file('function_build_dispatch_tables:', tabbed=False)
		for ins in self.dispatchtable_code:
    			self.write_file(ins)
		self.write_file('')

		# Generate COOL functions
		self.write_file('\n########### COOL FUNCTIONS ##########\n')
		for func in node.code_section:
			is_built_in = False
			if not INIT_CIL_SUFFIX in func.name:
				for built_in in BUILT_IN_CLASSES:
					if built_in in func.name:
						is_built_in = True
						break
			if not is_built_in:
				self.visit(func)
			# print(func.name)
		self.write_file('\n#####################################\n')


#################################### .DATA ###################################


	@visitor.when(cil.Data)
	def visit(self, node: cil.Data):
		self.write_file(f'{node.dest}: .asciiz \"{str(node.value.encode())[2:-1]}\"')


#################################### TYPES ###################################


	@visitor.when(cil.Type)
	def visit(self, node: cil.Type):
		# Allocate
		self.dispatchtable_code.append(f'# Type {node.type_name}')
		self.dispatchtable_code.append('li $a0 {}'.format(4 * len(node.methods)))
		self.dispatchtable_code.append('li $v0 9')
		self.dispatchtable_code.append('syscall')

		# Add dispatch table code
		for i in range(len(node.methods)):
			self.dispatchtable_code.append('la $t1 function_{}'.format(node.methods[i].function_name))
			self.dispatchtable_code.append('sw $t1 {}($v0)'.format(4 * i))
		self.dispatchtable_code.append('lw $t0 {}($s0)'.format(8 * self.type_index.index(node.type_name)))
		self.dispatchtable_code.append('sw $v0 8($t0)')
		self.dispatchtable_code.append('')
		
		# Allocate
		self.prototypes_code.append(f'# Type {node.type_name}')
		self.prototypes_code.append('li $a0 {}'.format(12 + 4 * len(node.attributes)))
		self.prototypes_code.append('li $v0 9')
		self.prototypes_code.append('syscall')

		# Add prototype code
		class_index = self.type_index.index(node.type_name)
		self.prototypes_code.append('li $a0 {}'.format(class_index))
		self.prototypes_code.append('sw $a0 0($v0)')
		self.prototypes_code.append('li $a0 {}'.format(12 + 4 * len(node.attributes)))
		self.prototypes_code.append('sw $a0 4($v0)')
		self.prototypes_code.append('sw $v0 {}($s0)'.format(8 * class_index))
		self.prototypes_code.append('')


	@visitor.when(cil.Function)
	def visit(self, node: cil.Function):
		self.write_file(f'function_{node.name}:', tabbed=False)

		# Set up stack frame
		self.write_file(f'move $fp, $sp')
		self.write_file(f'subiu $sp, $sp, {4 * len(node.vlocals)}')

		# Register arguments offsets
		for i in range(len(node.args)):
			self.offset[node.args[i].name] = 12 + i * 4

		# Register locals offsets
		for i in range(len(node.vlocals)):
			self.offset[node.vlocals[i].name] = i * (-4)

		# Generate mips code for the function's body
		for inst in node.body:
			self.visit(inst)

		# Pop the stack frame
		self.write_file(f'addiu $sp, $sp, {4 * len(node.vlocals)}')

		# Return
		self.write_file('jr $ra')

		self.write_file('')


############################### ASSIGNMENT ###################################


	@visitor.when(cil.Assign)
	def visit(self, node: cil.Assign):
		self.write_file('# ASSIGN')
		self.write_file('lw $a0, {}($fp)'.format(self.offset[node.source]))
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')


############################## ARITHMETICS ###################################


	@visitor.when(cil.Plus)
	def visit(self, node: cil.Plus):
		self.write_file('# +')
		self.write_file('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write_file('add $a0, $a0, $a1')
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.Minus)
	def visit(self, node: cil.Minus):
		self.write_file('# -')
		if isinstance(node.left, int):
			self.write_file('li $a0 {}'.format(node.left))
		else:
			self.write_file('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write_file('sub $a0, $a0, $a1')
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.Mult)
	def visit(self, node: cil.Mult):
		self.write_file('# *')
		self.write_file('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write_file('mul $a0, $a0, $a1')
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.Div)
	def visit(self, node: cil.Div):
		self.write_file('# /')
		self.write_file('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write_file('beqz $a1 _div_error')
		self.write_file('div $a0, $a0, $a1')
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('b _end')
		self.write_file('_div_error:',tabbed=False)
		self.write_file('la $a0 _div_abort_msg')
		self.write_file('li $v0 4')
		self.write_file('syscall')
		self.write_file('la $a0 _abort_msg')
		self.write_file('li $v0 4')
		self.write_file('syscall')
		self.write_file(f'li $v0 10')
		self.write_file(f'syscall')
		self.write_file('end:',tabbed=False)


############################## COMPARISONS ###################################


	@visitor.when(cil.Equal)
	def visit(self, node: cil.Equal):
		self.write_file('lw $t0 {}($fp)'.format(offset[self.node.left]))
		self.write_file('lw $t1 {}($fp)'.format(offset[self.node.right]))
		self.write_file('beq $t0 $zero _eq_false')  # $t0 can't also be void   
		self.write_file('beq $t1 $zero _eq_false') # $t1 can't also be void   
		self.write_file('lw	$a0 0($t0)')	# get object 1 tag
		self.write_file('lw	$a1 0($t1)')	# get object 2 tag
		self.write_file('bne $a0 $a1 _eq_false')	# compare tags
		self.write_file('lw $a2 _{}'.format(self.type_index.index(INTEGER_CLASS)))	# load int tag
		self.write_file('beq $a0 $a2 _eq_int_bool')	# Integers
		self.write_file('lw	$a2 {}'.format(type_index.index(BOOLEAN_CLASS)))	# load bool tag
		self.write_file('beq $a0 $a2 _eq_int_bool')	# Booleans
		self.write_file('lw	$a2 _string_tag') # load string tag
		self.write_file('bne $a0 $a2 _not_basic_type') # Not a primitive type
		
		# equal strings
		# verify len of the strings
		self.write_file('_eq_str:') 	# handle strings
		self.write_file('lw	$a3 12($t1)')  # get string_1 size
		self.write_file('lw	$a4, 12($t2)') # get string_2 size
		self.write_file('bne $a3 $a4 _eq_false') # string size are distinct
		
		# Verify ascii secuences
		self.write_file('add $t0 16')		 # Point to start of string s1
		self.write_file('lw $t0 $t0')
		self.write_file('add $t1 16') # Point to start of string s2
		self.write_file('lw $t1 $t1')
		self.write_file('move $t2 $a3')		# Keep string length as counter
		self.write_file('_verify_ascii_sequences_:')
		self.write_file('lbu $a0 0($t0)')	# get char of s1
		self.write_file('add $t0 1')
		self.write_file('lbu $a1 0($t1)')	# get char of s2
		self.write_file('add $t2 1')
		self.write_file('bne $a0 $a1 _eq_false') # char s1 /= char s2
		self.write_file('addiu $t2 $t2 -1')	# Decrement counter
		self.write_file('bnez $t2 _verify_ascii_sequences_')
		self.write_file('b _eq_true')		# end of strings

		self.write_file('_not_basic_type:')
		self.write_file('bne $t0 $t1 _eq_false')
		self.write('b _eq_true')

		# equal int or bool
		self.write_file('_eq_int_bool:')	# handles booleans and ints
		self.write_file('lw	$a3 ($t0)')	# load value variable_1
		self.write_file('lw	$a4,($t1)') # load variable_2
		self.write_file('bne $a3 $a4 _eq_false') # value of int or bool are distinct


		#return true
		self.write_file('_eq_true:')
		self.write_file('move $a0 1')
		self.write_file('sw $a0 {}($fp)'.format(offset[self.node.dest]))	
		self.write_file('b end_equal')

		#return false
		self.write_file('_eq_false:')
		self.write_file('move $a0 0')
		self.write_file('sw $a0 {}($fp)'.format(offset[self.node.dest]))
		self.write_file('end_equal:')


	@visitor.when(cil.LessThan)
	def visit(self, node: cil.LessThan):
		self.write_file('# <')
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a2, {}($fp)'.format(self.offset[node.right]))
		self.write_file('slt $a0, $a1, $a2'.format(self.offset[node.right]))
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.EqualOrLessThan)
	def visit(self, node: cil.EqualOrLessThan):
		self.write_file('# <=')
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a2, {}($fp)'.format(self.offset[node.right]))
		self.write_file('sle $a0, $a1, $a2'.format(self.offset[node.right]))
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')


############################## ATTRIBUTES ####################################


	@visitor.when(cil.GetAttrib)
	def visit(self, node: cil.GetAttrib):
		self.write_file('# GETATTR')
		self.write_file(f'lw $a1 {self.offset[node.instance]}($fp)')
		self.write_file(f'lw $a0 {12 + 4 * node.attribute}($a1)')
		self.write_file(f'sw $a0 {self.offset[node.dest]}($fp)')
		self.write_file('')


	@visitor.when(cil.SetAttrib)
	def visit(self, node: cil.SetAttrib):
		self.write_file('# SETATTR')
		self.write_file(f'lw $a1 {self.offset[node.instance]}($fp)')
		if isinstance(node.src, int):
			self.write_file(f'li $a0, {node.src}')
		elif node.src[:5] == "data_":
			self.write_file(f'la $a0, {node.src}')
		else:
			self.write_file(f'lw $a0 {self.offset[node.src]}($fp)')
		self.write_file(f'sw $a0 {12 + 4 * node.attribute}($a1)')
		self.write_file('')


################################# MEMORY #####################################


	@visitor.when(cil.TypeOf)
	def visit(self, node: cil.TypeOf):
		self.write_file('# TYPEOF')
		self.write_file(f'lw $a1 {self.offset[node.instance]}($fp)')
		self.write_file(f'lw $a0 0($a1)')
		self.write_file(f'sw $a0 {self.offset[node.dest]}($fp)')
		self.write_file('')


	@visitor.when(cil.Allocate)
	def visit(self, node: cil.Allocate):
		self.write_file('# ALLOCATE')
		if node.ttype == VOID_TYPE:
			self.write_file(f'la $v0 classname_void')
		else:
			offset_proto = self.type_index.index(node.ttype) * 8
			self.write_file('lw $t0 {}($s0)'.format(offset_proto))
			self.write_file('sw $t0, 0($sp)')
			self.write_file('addiu $sp, $sp, -4')
			self.write_file('')
			self.visit(cil.Call(dest = node.dest, f = "Object_copy"))
			self.write_file('addiu $sp, $sp, 4')
		self.write_file('')


########################## DISPATCH STATEMENTS ###############################


	@visitor.when(cil.Call)
	def visit(self, node: cil.Call):
		self.write_file('# CALL')

		# Save return address and frame pointer
		self.write_file(f'addiu $sp, $sp, -8')
		self.write_file(f'sw $ra, 4($sp)')
		self.write_file(f'sw $fp, 8($sp)')

		# Call the function
		# TODO: check node.f
		self.write_file(f'jal function_{node.f}')

		# Restore return address and frame pointer
		self.write_file(f'lw $fp, 8($sp)')
		self.write_file(f'lw $ra, 4($sp)')
		self.write_file(f'addiu $sp, $sp, 8')

		if node.dest:
			self.write_file(f'sw $v0 {self.offset[node.dest]}($fp)')

		self.write_file('')


	@visitor.when(cil.VCall)
	def visit(self, node: cil.VCall):
		self.write_file('# VCALL')

		# Save return address and frame pointer
		self.write_file(f'addiu $sp, $sp, -8')
		self.write_file(f'sw $ra, 4($sp)')
		self.write_file(f'sw $fp, 8($sp)')

		if node.ttype[0] == "_":
			# If node.type is a local CIL variable 
			self.write_file(f'lw $a2, {self.offset[node.ttype]}($fp)')
		else:
			# If node.type a type name 
			self.write_file(f'li $a2, {self.type_index.index(node.ttype)}')
		self.write_file(f'mulu $a2, $a2, 8')
		self.write_file(f'addu $a2, $a2, $s0')
		self.write_file(f'lw $a1, 0($a2)')

		# Check the dispatch table for the method's address
		self.write_file(f'lw $a2, 8($a1)')
		self.write_file(f'lw $a0 {node.f * 4}($a2)') # TODO: node.f * 4 + ... ?

		# Call the function at 0($a0)
		self.write_file(f'jalr $a0')

		# Restore return address and frame pointer
		self.write_file(f'lw $fp, 8($sp)')
		self.write_file(f'lw $ra, 4($sp)')
		self.write_file(f'addiu $sp, $sp, 8')

		# Save value after restoring $fp
		self.write_file(f'sw $v0 {self.offset[node.dest]}($fp)')

		# Check prototypes table for the dynamic type
		if node.ttype[0] != '_':
			self.write_file(f'li $a2, {self.type_index.index(node.ttype)}')
		else:
			self.write_file(f'lw $a2, {self.offset[node.ttype]}($fp)')

		self.write_file('')



	@visitor.when(cil.PushParam)
	def visit(self, node: cil.PushParam):
		self.write_file('# PUSHPARAM')
		if node.name[0] != "_":
			self.write_file('li $a0, {}'.format(self.type_index.index(node.name)))
		else:
			self.write_file('lw $a0, {}($fp)'.format(self.offset[node.name]))
		self.push()
		self.write_file('')


	@visitor.when(cil.PopParam)
	def visit(self, node: cil.PopParam):
		self.write_file('# POPPARAM')
		self.pop(node.name)
		self.write_file('')


	@visitor.when(cil.Return)
	def visit(self, node: cil.Return):
		self.write_file('# RETURN')
		self.write_file('lw $v0, {}($fp)'.format(self.offset[node.value]))


################################# JUMPS ######################################


	@visitor.when(cil.Label)
	def visit(self, node: cil.Label):
		self.write_file('_cil_label_{}:'.format(node.name), tabbed=False)


	@visitor.when(cil.Goto)
	def visit(self, node: cil.Goto):
		self.write_file('# GOTO')
		self.write_file('j _cil_label_{}'.format(node.label))
		self.write_file('')


	@visitor.when(cil.IfGoto)
	def visit(self, node: cil.IfGoto):
		self.write_file('# IF GOTO')
		self.write_file('lw $a0, {}($fp)'.format(self.offset[node.condition]))
		self.write_file('bnez $a0, _cil_label_{}'.format(node.label))
		self.write_file('')


################################ STATIC CODE #################################

	#----- ENTRY FUNCTION

	def entry(self):
		self.write_file('entry:', tabbed=False)
		self.visit(cil.Call(dest = None, f = 'build_class_name_table'))
		self.visit(cil.Call(dest = None, f = 'allocate_prototypes_table'))
		self.visit(cil.Call(dest = None, f = 'build_prototypes'))
		self.visit(cil.Call(dest = None, f = 'build_dispatch_tables'))
		self.visit(cil.Allocate(dest = None, ttype = 'Main'))
	
		# Push main self
		self.write_file('sw $v0 0($sp)')
		self.write_file('addiu $sp $sp -4')

		self.visit(cil.Call(dest = None, f = f'Main_{INIT_CIL_SUFFIX}'))
		self.write_file('addiu $sp $sp 4')
	
		# Push main self
		self.write_file('sw $v0 0($sp)')
		self.write_file('addiu $sp $sp -4')

		self.visit(cil.Call(dest = None, f = 'Main_main'))
		self.write_file('addiu $sp $sp 4')

		self.write_file('li $v0 10')
		self.write_file('syscall')

	#----- OBJECT METHODS

	def object_abort(self):
		self.write_file('function_Object_abort:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')
		
		self.write_file('jr $ra')
		self.write_file('')

	def object_copy(self):
		self.write_file('function_Object_copy:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')

		self.write_file('lw $t0 12($fp)')# recoger la instancia a copiar
		self.write_file('lw $a0 4($t0)')
		self.write_file('li $v0 9')
		self.write_file('syscall')# guarda en v0 la direccion de memoria que se reservo
		self.write_file('move $t2 $v0')# salvar la direccion donde comienza el objeto
		self.write_file('li $t3 0') # size ya copiado
		self.write_file('_objcopy_loop:', tabbed=False)
		self.write_file('lw $t1 0($t0)') # cargar la palabra por la que voy
		self.write_file('sw $t1 0($v0)') # copiar la palabra
		self.write_file('addiu $t0 $t0 4') # posiciona el puntero en la proxima palabra a copiar
		self.write_file('addiu $v0 $v0 4')	# posiciona el puntero en la direccion donde copiar la proxima palabra
		self.write_file('addiu $t3 $t3 4') # actualizar el size copiado
		self.write_file('ble $a0 $t3 _objcopy_loop') # verificar si la condicion es igual o menor igual
		self.write_file('_objcopy_end:', tabbed=False)
		self.write_file('move $v0 $t2') # dejar en v0 la direccion donde empieza el nuevo objeto
		self.write_file('jr $ra')
		self.write_file('')

	def object_typename(self):
		self.write_file('function_Object_type_name:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')

		self.write_file('lw $a1 12($fp)')				# self
		self.write_file('lw $a1 0($a1)')				# self's class tag (Boxed)
		self.write_file('lw $a1 12($a1)')			# Unbox class tag value
		self.write_file('mulu $a1 $a1 4')			# self's class tag
		self.write_file('addu $a1 $a1 $s1')			# class name table entry address
		self.write_file('lw $a1 0($a1)')				# Get class name address
		
		# Box the string reference
		self.visit(cil.Allocate(dest = None, ttype = STRING_CLASS))		# Create new String object
		self.write_file('move $t1 $v0')
		
		# Box string's length
		self.visit(cil.Allocate(dest = None, ttype = INTEGER_CLASS)	)		# Create new Int object
		
		self.write_file('move $a2 $0')				# Compute string's length
		self.write_file('move $t2 $a1')
		self.write_file('_str_len_clsname_:', tabbed=False)
		self.write_file('lw $a0 0($t2)')
		self.write_file('beq $a0 $0 _end_clsname_len_')
		self.write_file('addiu $a2 $a2 1')
		self.write_file('addiu $t2 $t2 1')
		self.write_file('j _str_len_clsname_')
		self.write_file('_end_clsname_len_:', tabbed=False)

		self.write_file('sw $a2, 12($v0)')			# Store string's length

		self.write_file('sw $v0, 12($t1)')			# Fill String attributes
		self.write_file('sw $a1, 16($t1)')

		self.write_file('move $v0 $t1')
		self.write_file('jr $ra')
		self.write_file('')


	#----- STRING METHODS

	def string_length(self):
		self.write_file('function_String_length:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')

		self.write_file('lw $a0 12($fp)')			# Self
		self.write_file('lw $v0 12($a0)')
		self.write_file('jr $ra')
		self.write_file('')

	def string_concat(self):
		self.write_file('function_String_concat:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')

		self.write_file('lw $a1 12($fp)')			# Self
		self.write_file('lw $a2 16($fp)')		# Boxed String to concat

		self.write_file('lw $t1 12($a1)')		# Self's length Int object
		
		self.visit(cil.Allocate(dest = None, ttype = INTEGER_CLASS))		# Create new Int object
		self.write_file('move $t3 $v0')									# Save new Int Object

		self.write_file('lw $t1 12($t1)')		# Self's length

		self.write_file('lw $t2 12($a2)')		# strings to concat's length Int object
		self.write_file('lw $t2 12($t2)')		# strings to concat's length

		self.write_file('addu $t0 $t2 $t1') 		# New string's length
		self.write_file('sw $t0 12($t3)')		# Store new string's length into box

		self.write_file('lw $a1 16($a1)')		# Unbox strings
		self.write_file('lw $a2 16($a2)')

		self.write_file('addiu $t0 $t0 1')		# Add space for \0
		self.allocate_memory('$t0', register=True)	# Allocate memory for new string
		self.write_file('move $t7 $v0')					# Keep the string's reference in v0 and use t7
		

		# a1: self's string		a2: 2nd string			t1: length self     t2: 2nd string length 	
		#									t3: new string's int object

		self.write_file('move $t4 $a1')			# Index for iterating the self string
		self.write_file('addu $a1 $a1 $t1')		# self's copy limit
		self.write_file('_strcat_copy_:', tabbed=False)
		self.write_file('beq $t4 $a1 _end_strcat_copy_')	# No more characters to copy

		self.write_file('lb $a0 0($t4)')			# Copy the character
		self.write_file('sw $a0 0($t7)')

		self.write_file('addiu $t7 $t7 1')		# Advance indices
		self.write_file('addiu $t4 $t4 1')
		self.write_file('j _strcat_copy_')
		self.write_file('_end_strcat_copy_:', tabbed=False)

		# Copy 2nd string

		self.write_file('move $t4 $a2')			# Index for iterating the strings
		self.write_file('addu $a2 $a2 $t2')		# self's copy limit
		self.write_file('_strcat_copy_snd_:', tabbed=False)
		self.write_file('beq $t4 $a2 _end_strcat_copy_snd_')	# No more characters to copy

		self.write_file('lb $a0 0($t4)')			# Copy the character
		self.write_file('sw $a0 0($t7)')

		self.write_file('addiu $t7 $t7 1')		# Advance indices
		self.write_file('addiu $t4 $t4 1')
		self.write_file('j _strcat_copy_snd_')
		self.write_file('_end_strcat_copy_snd_:', tabbed=False)

		self.write_file('sw $0 0($t7)')			# End string with \0	

		# $a0, $v0: reference to new string			$t3: length int object
		# -> Create boxed string
			
		self.write_file('move $a0 $v0')			# Save new string's reference
		
		self.visit(cil.Allocate(dest = None, ttype = STRING_CLASS))		# Create new String object

		self.write_file('sw $t3 12($v0)')		# New length
		self.write_file('sw $a0 16($v0)')		# New string

		self.write_file('jr $ra')					# Return new String object in $v0
		self.write_file('')

	def string_substr(self):
		self.write_file('function_String_substr:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')
		self.write_file(f'lw $t5 12($fp)') # self param
		self.write_file(f'lw $a1 16($fp)') # reference of object int that represent i
		self.write_file(f'lw $a1 12($a1)') # value of i
		self.write_file(f'lw $a2 18($fp)') # reference of object int that represent j
		self.write_file(f'lw $a2 12($a2)') # value of j that is length to copy
		self.write_file(f'blt $a1 $0 _index_negative') # index i is negative
		self.write_file(f'blt $a2 $0 _index_negative') # index j is negative
		self.write_file(f'add $a2 $a1 $a2') # finish index
		self.write_file(f'lw $a3 12($a0)')
		self.write_file(f'lw $a3 12($a3)') # length of string
		self.write_file(f'bgt $a2 $a3 _index_out') # j > lenght

		# not errors
		self.visit(cil.Allocate(dest = None, ttype = STRING_CLASS))
		self.write_file(f'move $v1 $v0') # new string

		self.visit(cil.Allocate(dest = None, ttype = INTEGER_CLASS))
		self.write_file(f'move $t0 $v0') # lenght of string


		self.allocate_memory('$a2', register=True)
		self.write_file(f'move $t1 $v0') # memory of the string

		self.write_file(f'sw $a2 12($t0)') # save number that represent lenght of new string
		self.write_file(f'sw $t0 12($v1)') # save lenght

		self.write_file(f'sw $t0 $t1') # save ascii code of new string

		# generate substring

		self.write_file('move $t4 $t5')			# Index for iterating the self string
		self.write_file('addu $t4 $t4 $a1')
		self.write_file('addu $t5 $t5 $a1')		
		self.write_file(f'addu $t5 $t5 $a2')# self's copy limit

		self.write_file('_substr_copy_:', tabbed=False)
		self.write_file('beq $t4 $t5 _end_substr_copy_')	# No more characters to copy

		self.write_file('lb $a0 0($t4)')			# Copy the character
		self.write_file('sb $a0 0($t1)')

		self.write_file('addiu $t1 $t1 1')		# Advance indices
		self.write_file('addiu $t4 $t4 1')
		self.write_file('j _substr_copy_')

		# errors sections
		self.write_file(f'_index_negative:',tabbed=False)
		self.write_file(f'la $a0 _index_negative_msg')	
		self.write_file(f'b	_subst_abort')

		self.write_file(f'_index_out',tabbed=False)
		self.write_file(f'la $a0 _substabort_msg3')	
		self.write_file(f'b	_subst_abort')

		# abort execution 
		self.write_file(f'subst_abort:',tabbed=False)
		self.write_file(f'li $v0 4') 
		self.write_file(f'syscall')
		self.write_file('la	$a0 _abort_msg')
		self.write_file(f'li $v0 4')
		self.write_file(f'syscall')
		self.write_file(f'li $v0 10')
		self.write_file(f'syscall') # exit

		# successful execution 
		self.write_file('_end_substr_copy_:', tabbed=False)





	#----- IO

	def io_in_int(self):
		self.write_file('function_IO_in_int:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')

		self.visit(cil.Allocate(dest = None, ttype = INTEGER_CLASS))			# Create new Int object

		self.write_file('move $t0 $v0')				# Save Int object

		self.write_file('li $v0 5')					# Read int
		self.write_file('syscall')

		self.write_file('sw $v0 12($t0)')			# Store int

		self.write_file('move $v0 $t0')
		self.write_file('jr $ra')
		self.write_file('')

	def io_in_string(self):
		self.write_file('function_IO_in_string:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')

		self.visit(cil.Allocate(dest = None, ttype = STRING_CLASS))			# Create new String object

		self.write_file('move $t0 $v0')				# Save String object

		self.write_file('li $v0 5')					# Read string
		self.write_file('syscall')

		self.write_file('sw $v0 12($t0)')			# Store string

		self.write_file('move $v0 $t0')
		self.write_file('jr $ra')
		self.write_file('')
		
	def io_out_int(self):
		self.write_file('function_IO_out_int:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')

		self.write_file('lw $a0 16($fp)')			# Get Int object
		self.write_file('lw $a0 12($a0)')

		self.write_file('li $v0 1')					# Print int
		self.write_file('syscall')

		self.write_file('lw $v0 12($fp)')				# Return self
		self.write_file('jr $ra')
		self.write_file('')
		
	def io_out_string(self):
		self.write_file('function_IO_out_string:', tabbed=False)
		# Set up stack frame
		self.write_file(f'move $fp, $sp')
		
		self.write_file('lw $a0 16($fp)')			# Get String object
		self.write_file('lw $a0 16($a0)')
		# TODO unbox length
		self.write_file('li $v0 4')					# Print string
		self.write_file('syscall')

		self.write_file('lw $v0 12($fp)')				# Return self
		self.write_file('jr $ra')
		self.write_file('')
