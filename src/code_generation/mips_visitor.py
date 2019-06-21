
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

  Prototipe layout:
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
		self.dispatchtable_code = []
		self.prototypes_code = []


	# ======================================================================
	# =[ UTILS ]============================================================
	# ======================================================================


	def push():
		self.write_file('addiu $sp $sp -4')
    	self.write_file('sw $a0 0($sp)')

	def pop(dest=None):
		if dest:
			self.write_file(f'lw $a0 0($sp)')
			self.write_file(f'sw $a0 {self.offset[dest]}($sp)')
    	self.write_file(f'addiu $sp $sp 4')


	def write_file(msg):
    	f = open("mips_code.txt","a")
		f.write("{}\n").format(msg)
		f.close()

	def allocate_memory(self,size):
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
		# Generate data section
		for data in node.data_section:
			self.visit(data)

		# Declare class name strings and map class index
		for i in range(len(node.dottypes)):
			self.type_index.append(node.dottypes[i].name)
			self.write_file('classname_{}: .asciiz \"{}\"'.format(node.dottypes[i].name,node.dottypes[i].name))

		# Text section
		self.write_file('.text')

		# Generate method that creates classes's name table
		self.write_file('class_name_table:')
		self.allocate_memory(len(node.dottypes) * 4)
		self.write_file('move $s1 $v0') # save the address of the table in a register
		for i in range(len(node.dottypes)):
			self.write_file('la $t1 classname_{}'.format(node.dottypes[i].name))
			self.write_file('sw $t1 {}($s1)'.format(4 * i))

		# Generate method that allocates memory for prototypes table
		self.write_file('alllocate_prototypes_table:')
		self.allocate_memory(8 * len(self.type_index))
		self.write_file('move $s0 $v0') # save the address of the table in a register

		# Generate mips method that builds prototypes
		self.write_file('build_prototype:')
		for ins in self.prototypes_code:
			self.write_file(ins)

		# Generate mips method that builds dispatch tables
		self.write_file('build_methods_table:')
		for ins in self.dispatchtable_code:
    			self.write_file(ins)


#################################### .DATA #################################


	@visitor.when(cil.Data)
	def visit(self, node: cil.Data):
		self.write_file(f'{node.dest}: .asciiz \"{node.value}\"')


#################################### TYPES ##################################


	@visitor.when(cil.Type)
	def visit(self, node: cil.Type):
		# Allocate
		self.write_file('li $a0 {}'.format(4 * len(node.methods)))
		self.write_file('li $v0 9')
		self.write_file('syscall')

		# Add dispatch table code
		for i in range(len(node.methods)):
			self.dispatchtable_code.append('la $t1 function_{}_{}'.format(node.type_name,node.methods[i]))
			self.dispatchtable_code.append('sw $t1 {}($v0)'.format(4 * i))
		self.dispatchtable_code.append('lw $t0 {}($s0)'.format(8 * self.type_index.index(node.type_name)))
		self.dispatchtable_code.append('sw $v0 8($t0)')

		
		# Allocate
		self.write_file('li $a0 {}'.format(12 + 4 * len(node.attributes)))
		self.write_file('li $v0 9')
		self.write_file('syscall')

		# Add prototype code
		class_index = self.type_index.index(node.type_name)
		self.prototypes_code.append('li $a0 {}'.format(class_index))
		self.prototypes_code.append('sw $a0 0($v0)')
		self.prototypes_code.append('li $a0 {}'.format(12 + 4 * len(node.attributes)))
		self.prototypes_code.append('sw $a0 4($v0)')
		self.prototypes_code.append('sw $v0 {}($s0)'.format(8 * class_index))


	@visitor.when(cil.Function)
	def visit(self, node: cil.Function):
		self.write_file(f'function_{node.name}:')

		# Set up stack frame
		self.write_file(f'mov $fp, $sp')
		self.write_file(f'subiu $fp, $fp, 4')
		self.write_file(f'subiu $sp, $sp, {4 * len(node.vlocals)}')

		# Register arguments offsets
		for i in range(len(node.args)):
			self.offset[node.args[i].name] = 8 + (len(node.args) - i + 1) * 4

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


################################ ASSIGMENT ###################################


	@visitor.when(cil.Assign)
	def visit(self, node: cil.Assign):
		self.write_file('# ASSIGN')
		self.write_file('lw $a0, {}($fp)'.format(self.offset[node.source]))
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest])


############################## ARITHMETICS ###################################


	@visitor.when(cil.Plus)
	def visit(self, node: cil.Plus):
		self.write_file('# +')
		self.write_file('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write_file('add $a0, $a0, &a1')
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
		self.write_file('sub $a0, $a0, &a1')
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.Mult)
	def visit(self, node: cil.Mult):
		self.write_file('# *')
		self.write_file('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write_file('mul $a0, $a0, &a1')
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.Div)
	def visit(self, node: cil.Div):
		self.write_file('# /')
		self.write_file('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write_file('div $a0, $a0, &a1')
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')


############################## COMPARISONS ###################################


	@visitor.when(cil.Equal)
	def visit(self, node: cil.Equal):
		pass

	@visitor.when(cil.LessThan)
	def visit(self, node: cil.LessThan):
		self.write_file('# <')
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a2, {}($fp)'.format(self.offset[node.right]))
		self.write_file('slt $a0, $a1, $a2'.format(self.offset[node.right]))
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.LessThanOrEqual)
	def visit(self, node: cil.LessThanOrEqual):
		self.write_file('# <=')
		self.write_file('lw $a1, {}($fp)'.format(self.offset[node.left]))
		self.write_file('lw $a2, {}($fp)'.format(self.offset[node.right]))
		self.write_file('sle $a0, $a1, $a2'.format(self.offset[node.right]))
		self.write_file('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write_file('')


############################## ATTRIBUTES ###################################


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


################################# MEMORY ####################################


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
		offset_proto = self.type_index.index(node.ttype) * 8
		self.write_file('lw $t0 {}($s0)'.format(offset_proto))
		self.write_file('addiu $sp, $sp, -4')
		self.write_file('sw $t0, 0($sp)')
		self.visit(cil.Call(dest = node.dest, f = "Object_copy"))
		self.write_file('addiu $sp, $sp, -4')
		self.write_file('')


########################## DISPATCH STATEMENTS ###############################


	@visitor.when(cil.Call)
	def visit(self, node: cil.Call):
		self.write_file('# CALL')

		# Save return address and frame pointer
		self.write_file(f'addiu $sp, $sp, -8')
		self.write_file(f'sw $ra, 0($sp)')
		self.write_file(f'sw $fp, 4($sp)')

		# Call the function
		# TODO: check node.f
		self.write_file(f'jal function_{node.f}')
		self.write_file(f'sw $v0 {self.offset[node.dest]}($fp)')

		# Restore return address and frame pointer
		self.write_file(f'lw $fp, 4($sp)')
		self.write_file(f'lw $ra, 0($sp)')
		self.write_file(f'addiu $sp, $sp, 8')

		self.write_file('')


	@visitor.when(cil.VCall)
	def visit(self, node: cil.VCall):
		self.write_file('# VCALL')

		# Save return address and frame pointer
		self.write_file(f'addiu $sp, $sp, -8')
		self.write_file(f'sw $ra, 0($sp)')
		self.write_file(f'sw $fp, 4($sp)')

		# Check prototypes table for the dynamic type
		self.write_file(f'lw $a2, {self.offset[node.ttype]}($fp)')
		self.write_file(f'mulu $a2, $a2, 4')
		self.write_file(f'addu $a2, $a2, $s0')
		self.write_file(f'lw $a1, 0($a2)')

		# Check the dispatch table for the method's address
		self.write_file(f'lw $a2, 8($a1)')
		self.write_file(f'lw $a0 {node.f * 4}($a2)') # TODO: node.f * 4 + ... ?

		# Call the function at 0($a0)
		self.write_file(f'jalr $a0')
		self.write_file(f'sw $v0 {self.offset[node.dest]}($fp)')

		# Restore return address and frame pointer
		self.write_file(f'lw $fp, 4($sp)')
		self.write_file(f'lw $ra, 0($sp)')
		self.write_file(f'addiu $sp, $sp, 8')

		self.write_file('')



	@visitor.when(cil.PushParam)
	def visit(self, node: cil.PushParam):
		self.write_file('# PUSHPARAM')
		if isinstance(node.name, str):
			# node.name is a type; replace with type index
			pass
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


############################## JUMPS ###################################


	@visitor.when(cil.Label)
	def visit(self, node: cil.Label):
    	self.write_file('{}:'.format(node.name))


	@visitor.when(cil.Goto)
	def visit(self, node: cil.Goto):
		self.write_file('# GOTO')
		self.write_file('j {}'.format(node.label))
		self.write_file('')


	@visitor.when(cil.IfGoto)
	def visit(self, node: cil.IfGoto):
		self.write_file('# IF GOTO')
		self.write_file('lw $a0, {}($fp)'.format(node.label))
		self.write_file('bnez $a0, {}'.format(node.label))
		self.write_file('')


############################## STATIC CODE ###############################

	def object_copy(self):
		self.write_file('function_Object_copy:')
		self.write_file('lw $t0 8($fp)')# recoger la instancia a copiar
		self.write_file('lw $a0 4($t0)')
		self.write_file('li $v0 9')
		self.write_file('syscall')# guarda en v0 la direccion de memoria que se reservo
		self.write_file('move $t2 $v0')# salvar la direccion donde comienza el objeto
		self.write_file('li $t3 0') # size ya copiado
		self.write_file('_objcopy_loop:')
		self.write_file('lw	$t1 0($t0)') # cargar la palabra por la que voy
		self.write_file('sw	$t1 0($v0)') # copiar la palabra
		self.write_file('addiu	$t0 $t0 4') # posiciona el puntero en la proxima palabra a copiar
		self.write_file('addiu	$v0 $v0 4')	# posiciona el puntero en la direccion donde copiar la proxima palabra
		self.write_file('addiu	$t3 $t3 4') # actualizar el size copiado
		self.write_file('ble $a0 $t3 _objcopy_loop') # verificar si la condicion es igual o menor igual
		self.write_file('_objcopy_end:')
		self.write_file('move $v0 $t2') # dejar en v0 la direccion donde empieza el nuevo objeto
		self.write_file('jr $ra')