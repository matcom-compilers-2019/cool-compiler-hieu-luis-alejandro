
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

	# ======================================================================

	@visitor.on('node')
	def visit(self, node):
		pass
	

#################################### PROGRAM #################################


	@visitor.when(cil.Program)
	def visit(self, node: cil.Program):
		pass


#################################### .DATA #################################

		
	@visitor.when(cil.Data)
	def visit(self, node: cil.Data):
		pass


#################################### TYPES ################################## 


	@visitor.when(cil.Type)
	def visit(self, node: cil.Type):
		pass


	@visitor.when(cil.Attribute)
	def visit(self, node: cil.Attribute):
		pass

		
	@visitor.when(cil.Method)
	def visit(self, node: cil.Method):
		pass


	@visitor.when(cil.Function)
	def visit(self, node: cil.Function):
		self.write_file(f'function_{node.name}:')
		# Aqui va cuerpo del metodo
		self.write_file('')


################################ ASSIGMENT ################################### 


	@visitor.when(cil.Assign)
	def visit(self, node: cil.Assign):
		self.write_file('# ASSIGN')
		self.write_file('lw $a0, {}($sp)'.format(self.offset[node.source]))
		self.write_file('sw $a0, {}($sp)'.format(self.offset[node.dest])


############################## ARITHMETICS ################################### 


	@visitor.when(cil.Plus)
	def visit(self, node: cil.Plus):
		self.write_file('# +')
		self.write_file('lw $a0, {}($sp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($sp)'.format(self.offset[node.right])) 
		self.write_file('add $a0, $a0, &a1')
		self.write_file('sw $a0, {}($sp)'.format(self.offset[node.dest]))
		self.write_file('')
		
	@visitor.when(cil.Minus)
	def visit(self, node: cil.Minus):
		self.write_file('# -')
		self.write_file('lw $a0, {}($sp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($sp)'.format(self.offset[node.right]))
		self.write_file('sub $a0, $a0, &a1')
		self.write_file('sw $a0, {}($sp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.Mult)
	def visit(self, node: cil.Mult):
		self.write_file('# *')
		self.write_file('lw $a0, {}($sp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($sp)'.format(self.offset[node.right]))
		self.write_file('mul $a0, $a0, &a1')
		self.write_file('sw $a0, {}($sp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.Div)
	def visit(self, node: cil.Div):
		self.write_file('# /')
		self.write_file('lw $a0, {}($sp)'.format(self.offset[node.left]))
		self.write_file('lw $a1, {}($sp)'.format(self.offset[node.right]))
		self.write_file('div $a0, $a0, &a1')
		self.write_file('sw $a0, {}($sp)'.format(self.offset[node.dest]))
		self.write_file('')


############################## COMPARISONS ################################### 


	@visitor.when(cil.Equal)
	def visit(self, node: cil.Equal):
		pass

	@visitor.when(cil.LessThan)
	def visit(self, node: cil.LessThan):
		self.write_file('# <')
		self.write_file('lw $a1, {}($sp)'.format(self.offset[node.left]))
		self.write_file('lw $a2, {}($sp)'.format(self.offset[node.right]))
		self.write_file('slt $a0, $a1, $a2'.format(self.offset[node.right]))
		self.write_file('sw $a0, {}($sp)'.format(self.offset[node.dest]))
		self.write_file('')

	@visitor.when(cil.LessThanOrEqual)
	def visit(self, node: cil.LessThanOrEqual):
		self.write_file('# <=')
		self.write_file('lw $a1, {}($sp)'.format(self.offset[node.left]))
		self.write_file('lw $a2, {}($sp)'.format(self.offset[node.right]))
		self.write_file('sle $a0, $a1, $a2'.format(self.offset[node.right]))
		self.write_file('sw $a0, {}($sp)'.format(self.offset[node.dest]))
		self.write_file('')


############################## ATTRIBUTES ################################### 


	@visitor.when(cil.GetAttrib)
	def visit(self, node: cil.GetAttrib):
		self.write_file('# GETATTR')
		self.write_file(f'lw $a1 {self.offset[node.instance]}($sp)')
		self.write_file(f'lw $a0 {12 + 4 * node.attribute}($a1)')
		self.write_file(f'sw $a0 {self.offset[node.dest]}($sp)')
		self.write_file('')

		
	@visitor.when(cil.SetAttrib)
	def visit(self, node: cil.SetAttrib):
		self.write_file('# SETATTR')
		self.write_file(f'lw $a1 {self.offset[node.instance]}($sp)')
		self.write_file(f'lw $a0 {self.offset[node.src]}($sp)')
		self.write_file(f'sw $a0 {12 + 4 * node.attribute}($a1)')
		self.write_file('')


################################# MEMORY ####################################


	@visitor.when(cil.TypeOf)
	def visit(self, node: cil.TypeOf):
		self.write_file('# TYPEOF')
		self.write_file(f'lw $a1 {self.offset[node.instance]}($sp)')
		self.write_file(f'lw $a0 0($a1)')
		self.write_file(f'sw $a0 {self.offset[node.dest]}($sp)')
		self.write_file('')

		
	@visitor.when(cil.Allocate)
	def visit(self, node: cil.Allocate):
		pass


########################## DISPATCH STATEMENTS ###############################


	@visitor.when(cil.Call)
	def visit(self, node: cil.Call):
		self.write_file(f'# CALL')
		self.write_file(f'jal function_{node.f}')
		self.write_file(f'sw $v0 {self.offset[node.dest]}($sp)')
		self.write_file('')

		
	@visitor.when(cil.VCall)
	def visit(self, node: cil.VCall):
		self.write_file(f'# VCALL')

		self.write_file('')


		
	@visitor.when(cil.PushParam)
	def visit(self, node: cil.PushParam):
		self.write_file('# PUSHPARAM')
		self.write_file('lw $a0, {}($sp)'.format(self.offset[node.name]))
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
		self.write_file('lw $a0, {}($sp)'.format(self.offset[node.value]))
		self.write_file('jr $ra')
		self.write_file('')


############################## JUMPS ################################### 


	@visitor.when(cil.Label)
	def visit(self, node: cil.Label):
    	self.write_file('{}:').format(node.name)


	@visitor.when(cil.Goto)
	def visit(self, node: cil.Goto):
		self.write_file('# GOTO')
		self.write_file('j {}').format(node.label)
		self.write_file('')
	
	
	@visitor.when(cil.IfGoto)
	def visit(self, node: cil.IfGoto):
		self.write_file('# IF GOTO')
		self.write_file('lw $a0, {}($sp)'.format(node.label))
		self.write_file('bnez $a0, {}'.format(node.label))
		self.write_file('')