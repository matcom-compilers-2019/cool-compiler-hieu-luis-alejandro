
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
li $a0 0
li $v0 9
syscall
li $a0 12
li $v0 9
syscall
li $a0 12
li $v0 9
syscall
li $a0 12
li $v0 9
syscall
li $a0 28
li $v0 9
syscall
li $a0 12
li $v0 9
syscall
li $a0 32
li $v0 9
syscall
li $a0 12
li $v0 9
syscall
li $a0 12
li $v0 9
syscall
li $a0 16
li $v0 9
syscall
li $a0 12
li $v0 9
syscall
li $a0 16
li $v0 9
syscall
li $a0 24
li $v0 9
syscall
li $a0 20
li $v0 9
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
li $a0 0
sw $a0 0($v0)
li $a0 12
sw $a0 4($v0)
sw $v0 0($s0)
li $a0 1
sw $a0 0($v0)
li $a0 12
sw $a0 4($v0)
sw $v0 8($s0)
li $a0 2
sw $a0 0($v0)
li $a0 12
sw $a0 4($v0)
sw $v0 16($s0)
li $a0 3
sw $a0 0($v0)
li $a0 12
sw $a0 4($v0)
sw $v0 24($s0)
li $a0 4
sw $a0 0($v0)
li $a0 16
sw $a0 4($v0)
sw $v0 32($s0)
li $a0 5
sw $a0 0($v0)
li $a0 16
sw $a0 4($v0)
sw $v0 40($s0)
li $a0 6
sw $a0 0($v0)
li $a0 20
sw $a0 4($v0)
sw $v0 48($s0)

function_build_dispatch_tables:
lw $t0 0($s0)
sw $v0 8($t0)
la $t1 function_Object_method abort : Object_abort


sw $t1 0($v0)
la $t1 function_Object_method copy : Object_copy


sw $t1 4($v0)
la $t1 function_Object_method type_name : Object_type_name


sw $t1 8($v0)
lw $t0 8($s0)
sw $v0 8($t0)
la $t1 function_IO_method abort : Object_abort


sw $t1 0($v0)
la $t1 function_IO_method copy : Object_copy


sw $t1 4($v0)
la $t1 function_IO_method type_name : Object_type_name


sw $t1 8($v0)
la $t1 function_IO_method in_int : IO_in_int


sw $t1 12($v0)
la $t1 function_IO_method in_string : IO_in_string


sw $t1 16($v0)
la $t1 function_IO_method out_int : IO_out_int


sw $t1 20($v0)
la $t1 function_IO_method out_string : IO_out_string


sw $t1 24($v0)
lw $t0 16($s0)
sw $v0 8($t0)
la $t1 function_Main_method abort : Object_abort


sw $t1 0($v0)
la $t1 function_Main_method copy : Object_copy


sw $t1 4($v0)
la $t1 function_Main_method type_name : Object_type_name


sw $t1 8($v0)
la $t1 function_Main_method in_int : IO_in_int


sw $t1 12($v0)
la $t1 function_Main_method in_string : IO_in_string


sw $t1 16($v0)
la $t1 function_Main_method out_int : IO_out_int


sw $t1 20($v0)
la $t1 function_Main_method out_string : IO_out_string


sw $t1 24($v0)
la $t1 function_Main_method main : Main_main


sw $t1 28($v0)
lw $t0 24($s0)
sw $v0 8($t0)
la $t1 function_Int_method abort : Object_abort


sw $t1 0($v0)
la $t1 function_Int_method copy : Object_copy


sw $t1 4($v0)
la $t1 function_Int_method type_name : Object_type_name


sw $t1 8($v0)
lw $t0 32($s0)
sw $v0 8($t0)
la $t1 function_Bool_method abort : Object_abort


sw $t1 0($v0)
la $t1 function_Bool_method copy : Object_copy


sw $t1 4($v0)
la $t1 function_Bool_method type_name : Object_type_name


sw $t1 8($v0)
lw $t0 40($s0)
sw $v0 8($t0)
la $t1 function_String_method abort : Object_abort


sw $t1 0($v0)
la $t1 function_String_method copy : Object_copy


sw $t1 4($v0)
la $t1 function_String_method type_name : Object_type_name


sw $t1 8($v0)
la $t1 function_String_method length : String_length


sw $t1 12($v0)
la $t1 function_String_method concat : String_concat


sw $t1 16($v0)
la $t1 function_String_method substr : String_substr


sw $t1 20($v0)
lw $t0 48($s0)
sw $v0 8($t0)

