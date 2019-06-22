
.data
data_0: .asciiz ""
data_1: .asciiz "Hello, World.\n"
classname_Void: .asciiz "Void"
classname_Object: .asciiz "Object"
classname_IO: .asciiz "IO"
classname_Main: .asciiz "Main"
classname_Int: .asciiz "Int"
classname_Bool: .asciiz "Bool"
classname_String: .asciiz "String"
classname_void: .asciiz ""

.text
entry:
# CALL
addiu $sp, $sp, -8
sw $ra, 0($sp)
sw $fp, 4($sp)
jal function_build_class_name_table
lw $fp, 4($sp)
lw $ra, 0($sp)
addiu $sp, $sp, 8

# CALL
addiu $sp, $sp, -8
sw $ra, 0($sp)
sw $fp, 4($sp)
jal function_allocate_prototypes_table
lw $fp, 4($sp)
lw $ra, 0($sp)
addiu $sp, $sp, 8

# CALL
addiu $sp, $sp, -8
sw $ra, 0($sp)
sw $fp, 4($sp)
jal function_build_prototypes
lw $fp, 4($sp)
lw $ra, 0($sp)
addiu $sp, $sp, 8

# CALL
addiu $sp, $sp, -8
sw $ra, 0($sp)
sw $fp, 4($sp)
jal function_build_dispatch_tables
lw $fp, 4($sp)
lw $ra, 0($sp)
addiu $sp, $sp, 8

# ALLOCATE
lw $t0 24($s0)
addiu $sp, $sp, -4
sw $t0, 0($sp)
# CALL
addiu $sp, $sp, -8
sw $ra, 0($sp)
sw $fp, 4($sp)
jal function_Object_copy
lw $fp, 4($sp)
lw $ra, 0($sp)
addiu $sp, $sp, 8

addiu $sp, $sp, 4

# CALL
addiu $sp, $sp, -8
sw $ra, 0($sp)
sw $fp, 4($sp)
jal function_Main__init
lw $fp, 4($sp)
lw $ra, 0($sp)
addiu $sp, $sp, 8

# CALL
addiu $sp, $sp, -8
sw $ra, 0($sp)
sw $fp, 4($sp)
jal function_Main_main
lw $fp, 4($sp)
lw $ra, 0($sp)
addiu $sp, $sp, 8

li $v0 10
syscall
function_build_class_name_table:
li $a0 28
li $v0 9
syscall
move $s1 $v0
la $t1 classname_Void
sw $t1 0($s1)
la $t1 classname_Object
sw $t1 4($s1)
la $t1 classname_IO
sw $t1 8($s1)
la $t1 classname_Main
sw $t1 12($s1)
la $t1 classname_Int
sw $t1 16($s1)
la $t1 classname_Bool
sw $t1 20($s1)
la $t1 classname_String
sw $t1 24($s1)

function_allocate_prototypes_table:
li $a0 56
li $v0 9
syscall
move $s0 $v0

function_build_prototypes:

function_build_dispatch_tables:

