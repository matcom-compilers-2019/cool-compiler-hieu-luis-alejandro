	
	.data
	data_0: .asciiz ""
	data_1: .asciiz "asda"
	data_2: .asciiz "s"
	classname_Void: .asciiz "Void"
	classname_Object: .asciiz "Object"
	classname_IO: .asciiz "IO"
	classname_Main: .asciiz "Main"
	classname_Int: .asciiz "Int"
	classname_Bool: .asciiz "Bool"
	classname_String: .asciiz "String"
	classname_A: .asciiz "A"
	classname_B: .asciiz "B"
	classname_void: .asciiz ""
	
.text
entry:
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_build_class_name_table
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_allocate_prototypes_table
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_build_prototypes
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_build_dispatch_tables
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	# ALLOCATE
	lw $t0 24($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	addiu $sp, $sp, 4
	
	sw $v0 0($sp)
	addiu $sp $sp -4
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Main__init
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	addiu $sp $sp 4
	sw $v0 0($sp)
	addiu $sp $sp -4
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Main_main
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	addiu $sp $sp 4
	li $v0 10
	syscall
	
########## STATIC FUNCTIONS ##########

function_Object_abort:
	move $fp, $sp
	jr $ra
	
function_Object_copy:
	move $fp, $sp
	lw $t0 12($fp)
	lw $a0 4($t0)
	li $v0 9
	syscall
	move $t2 $v0
	li $t3 0
_objcopy_loop:
	lw $t1 0($t0)
	sw $t1 0($v0)
	addiu $t0 $t0 4
	addiu $v0 $v0 4
	addiu $t3 $t3 4
	ble $a0 $t3 _objcopy_loop
_objcopy_end:
	move $v0 $t2
	jr $ra
	
function_Object_type_name:
	move $fp, $sp
	lw $a1 12($fp)
	lw $a1 0($a1)
	lw $a1 12($a1)
	mulu $a1 $a1 4
	addu $a1 $a1 $s1
	lw $a1 0($a1)
	# ALLOCATE
	lw $t0 48($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	addiu $sp, $sp, 4
	
	move $t1 $v0
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	addiu $sp, $sp, 4
	
	move $a2 $0
	move $t2 $a1
_str_len_clsname_:
	lw $a0 0($t2)
	beq $a0 $0 _end_clsname_len_
	addiu $a2 $a2 1
	addiu $t2 $t2 1
	j _str_len_clsname_
_end_clsname_len_:
	sw $a2, 12($v0)
	sw $v0, 12($t1)
	sw $a1, 16($t1)
	move $v0 $t1
	jr $ra
	
function_String_length:
	move $fp, $sp
	lw $a0 12($fp)
	lw $v0 12($a0)
	jr $ra
	
function_String_concat:
	move $fp, $sp
	lw $a1 12($fp)
	lw $a2 16($fp)
	lw $t1 12($a1)
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	addiu $sp, $sp, 4
	
	move $t3 $v0
	lw $t1 12($t1)
	lw $t2 12($a2)
	lw $t2 12($t2)
	addu $t0 $t2 $t1
	sw $t0 12($t3)
	lw $a1 16($a1)
	lw $a2 16($a2)
	addiu $t0 $t0 1
	move $a0 $t0
	li $v0 9
	syscall
	move $t7 $v0
	move $t4 $a1
	addu $a1 $a1 $t1
_strcat_copy_:
	beq $t4 $a1 _end_strcat_copy_
	lb $a0 0($t4)
	sw $a0 0($t7)
	addiu $t7 $t7 1
	addiu $t4 $t4 1
	j _strcat_copy_
_end_strcat_copy_:
	move $t4 $a2
	addu $a2 $a2 $t2
_strcat_copy_snd_:
	beq $t4 $a2 _end_strcat_copy_snd_
	lb $a0 0($t4)
	sw $a0 0($t7)
	addiu $t7 $t7 1
	addiu $t4 $t4 1
	j _strcat_copy_snd_
_end_strcat_copy_snd_:
	sw $0 0($t7)
	move $a0 $v0
	# ALLOCATE
	lw $t0 48($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	addiu $sp, $sp, 4
	
	sw $t3 12($v0)
	sw $a0 16($v0)
	jr $ra
	
function_String_substr:
	move $fp, $sp
function_IO_in_int:
	move $fp, $sp
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	addiu $sp, $sp, 4
	
	move $t0 $v0
	li $v0 5
	syscall
	sw $v0 12($t0)
	move $v0 $t0
	jr $ra
	
function_IO_in_string:
	move $fp, $sp
	# ALLOCATE
	lw $t0 48($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	
	addiu $sp, $sp, 4
	
	move $t0 $v0
	li $v0 5
	syscall
	sw $v0 12($t0)
	move $v0 $t0
	jr $ra
	
function_IO_out_int:
	move $fp, $sp
	lw $a0 16($fp)
	lw $a0 12($a0)
	li $v0 1
	syscall
	lw $v0 12($fp)
	jr $ra
	
function_IO_out_string:
	move $fp, $sp
	lw $a0 16($fp)
	lw $a0 16($a0)
	li $v0 4
	syscall
	lw $v0 12($fp)
	jr $ra
	
	######################################

function_build_class_name_table:
	li $a0 36
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
	la $t1 classname_A
	sw $t1 28($s1)
	la $t1 classname_B
	sw $t1 32($s1)
	
function_allocate_prototypes_table:
	li $a0 72
	li $v0 9
	syscall
	move $s0 $v0
	
function_build_prototypes:
	# Type Void
	li $a0 12
	li $v0 9
	syscall
	li $a0 0
	sw $a0 0($v0)
	li $a0 12
	sw $a0 4($v0)
	sw $v0 0($s0)
	
	# Type Object
	li $a0 12
	li $v0 9
	syscall
	li $a0 1
	sw $a0 0($v0)
	li $a0 12
	sw $a0 4($v0)
	sw $v0 8($s0)
	
	# Type IO
	li $a0 12
	li $v0 9
	syscall
	li $a0 2
	sw $a0 0($v0)
	li $a0 12
	sw $a0 4($v0)
	sw $v0 16($s0)
	
	# Type Main
	li $a0 12
	li $v0 9
	syscall
	li $a0 3
	sw $a0 0($v0)
	li $a0 12
	sw $a0 4($v0)
	sw $v0 24($s0)
	
	# Type Int
	li $a0 16
	li $v0 9
	syscall
	li $a0 4
	sw $a0 0($v0)
	li $a0 16
	sw $a0 4($v0)
	sw $v0 32($s0)
	
	# Type Bool
	li $a0 16
	li $v0 9
	syscall
	li $a0 5
	sw $a0 0($v0)
	li $a0 16
	sw $a0 4($v0)
	sw $v0 40($s0)
	
	# Type String
	li $a0 20
	li $v0 9
	syscall
	li $a0 6
	sw $a0 0($v0)
	li $a0 20
	sw $a0 4($v0)
	sw $v0 48($s0)
	
	# Type A
	li $a0 16
	li $v0 9
	syscall
	li $a0 7
	sw $a0 0($v0)
	li $a0 16
	sw $a0 4($v0)
	sw $v0 56($s0)
	
	# Type B
	li $a0 12
	li $v0 9
	syscall
	li $a0 8
	sw $a0 0($v0)
	li $a0 12
	sw $a0 4($v0)
	sw $v0 64($s0)
	
	
function_build_dispatch_tables:
	# Type Void
	li $a0 0
	li $v0 9
	syscall
	lw $t0 0($s0)
	sw $v0 8($t0)
	
	# Type Object
	li $a0 12
	li $v0 9
	syscall
	la $t1 function_Object_abort
	sw $t1 0($v0)
	la $t1 function_Object_copy
	sw $t1 4($v0)
	la $t1 function_Object_type_name
	sw $t1 8($v0)
	lw $t0 8($s0)
	sw $v0 8($t0)
	
	# Type IO
	li $a0 28
	li $v0 9
	syscall
	la $t1 function_Object_abort
	sw $t1 0($v0)
	la $t1 function_Object_copy
	sw $t1 4($v0)
	la $t1 function_Object_type_name
	sw $t1 8($v0)
	la $t1 function_IO_in_int
	sw $t1 12($v0)
	la $t1 function_IO_in_string
	sw $t1 16($v0)
	la $t1 function_IO_out_int
	sw $t1 20($v0)
	la $t1 function_IO_out_string
	sw $t1 24($v0)
	lw $t0 16($s0)
	sw $v0 8($t0)
	
	# Type Main
	li $a0 32
	li $v0 9
	syscall
	la $t1 function_Object_abort
	sw $t1 0($v0)
	la $t1 function_Object_copy
	sw $t1 4($v0)
	la $t1 function_Object_type_name
	sw $t1 8($v0)
	la $t1 function_IO_in_int
	sw $t1 12($v0)
	la $t1 function_IO_in_string
	sw $t1 16($v0)
	la $t1 function_IO_out_int
	sw $t1 20($v0)
	la $t1 function_IO_out_string
	sw $t1 24($v0)
	la $t1 function_Main_main
	sw $t1 28($v0)
	lw $t0 24($s0)
	sw $v0 8($t0)
	
	# Type Int
	li $a0 12
	li $v0 9
	syscall
	la $t1 function_Object_abort
	sw $t1 0($v0)
	la $t1 function_Object_copy
	sw $t1 4($v0)
	la $t1 function_Object_type_name
	sw $t1 8($v0)
	lw $t0 32($s0)
	sw $v0 8($t0)
	
	# Type Bool
	li $a0 12
	li $v0 9
	syscall
	la $t1 function_Object_abort
	sw $t1 0($v0)
	la $t1 function_Object_copy
	sw $t1 4($v0)
	la $t1 function_Object_type_name
	sw $t1 8($v0)
	lw $t0 40($s0)
	sw $v0 8($t0)
	
	# Type String
	li $a0 24
	li $v0 9
	syscall
	la $t1 function_Object_abort
	sw $t1 0($v0)
	la $t1 function_Object_copy
	sw $t1 4($v0)
	la $t1 function_Object_type_name
	sw $t1 8($v0)
	la $t1 function_String_length
	sw $t1 12($v0)
	la $t1 function_String_concat
	sw $t1 16($v0)
	la $t1 function_String_substr
	sw $t1 20($v0)
	lw $t0 48($s0)
	sw $v0 8($t0)
	
	# Type A
	li $a0 32
	li $v0 9
	syscall
	la $t1 function_Object_abort
	sw $t1 0($v0)
	la $t1 function_Object_copy
	sw $t1 4($v0)
	la $t1 function_Object_type_name
	sw $t1 8($v0)
	la $t1 function_A_value
	sw $t1 12($v0)
	la $t1 function_A_set_var
	sw $t1 16($v0)
	la $t1 function_A_method1
	sw $t1 20($v0)
	la $t1 function_A_method2
	sw $t1 24($v0)
	la $t1 function_A_method5
	sw $t1 28($v0)
	lw $t0 56($s0)
	sw $v0 8($t0)
	
	# Type B
	li $a0 20
	li $v0 9
	syscall
	la $t1 function_Object_abort
	sw $t1 0($v0)
	la $t1 function_Object_copy
	sw $t1 4($v0)
	la $t1 function_Object_type_name
	sw $t1 8($v0)
	la $t1 function_B_method5
	sw $t1 12($v0)
	la $t1 function_B_method3
	sw $t1 16($v0)
	lw $t0 64($s0)
	sw $v0 8($t0)
	
	
	
########### COOL FUNCTIONS ##########

function_Object__init:
	move $fp, $sp
	subiu $sp, $sp, 0
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 0
	jr $ra
	
function_IO__init:
	move $fp, $sp
	subiu $sp, $sp, 0
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 0
	jr $ra
	
function_Main__init:
	move $fp, $sp
	subiu $sp, $sp, 0
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 0
	jr $ra
	
function_Main_main:
	move $fp, $sp
	subiu $sp, $sp, 32
	# ALLOCATE
	lw $t0 56($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 0($fp)
	
	addiu $sp, $sp, 4
	
	# PUSHPARAM
	lw $a0, 0($fp)
	sw $a0 0($sp)
	addiu $sp $sp -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_A__init
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -4($fp)
	
	# POPPARAM
	addiu $sp $sp 4
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -8($fp)
	
	addiu $sp, $sp, 4
	
	# PUSHPARAM
	lw $a0, -8($fp)
	sw $a0 0($sp)
	addiu $sp $sp -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Int__init
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -8($fp)
	
	# POPPARAM
	addiu $sp $sp 4
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -28($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -28($fp)
	li $a0, 15
	sw $a0 12($a1)
	
	# PUSHPARAM
	lw $a0, -28($fp)
	sw $a0 0($sp)
	addiu $sp $sp -4
	
	# PUSHPARAM
	lw $a0, 0($fp)
	sw $a0 0($sp)
	addiu $sp $sp -4
	
	# TYPEOF
	lw $a1 0($fp)
	lw $a0 0($a1)
	sw $a0 -20($fp)
	
	# VCALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	lw $a2, -20($fp)
	mulu $a2, $a2, 8
	addu $a2, $a2, $s0
	lw $a1, 0($a2)
	lw $a2, 8($a1)
	lw $a0 28($a2)
	jalr $a0
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -24($fp)
	lw $a2, -20($fp)
	
	# POPPARAM
	addiu $sp $sp 4
	
	# POPPARAM
	addiu $sp $sp 4
	
	# PUSHPARAM
	lw $a0, -24($fp)
	sw $a0 0($sp)
	addiu $sp $sp -4
	
	# PUSHPARAM
	lw $a0, 12($fp)
	sw $a0 0($sp)
	addiu $sp $sp -4
	
	# TYPEOF
	lw $a1 12($fp)
	lw $a0 0($a1)
	sw $a0 -12($fp)
	
	# VCALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	lw $a2, -12($fp)
	mulu $a2, $a2, 8
	addu $a2, $a2, $s0
	lw $a1, 0($a2)
	lw $a2, 8($a1)
	lw $a0 20($a2)
	jalr $a0
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -16($fp)
	lw $a2, -12($fp)
	
	# POPPARAM
	addiu $sp $sp 4
	
	# POPPARAM
	addiu $sp $sp 4
	
	# RETURN
	lw $v0, -16($fp)
	addiu $sp, $sp, 32
	jr $ra
	
function_Int__init:
	move $fp, $sp
	subiu $sp, $sp, 0
	# SETATTR
	lw $a1 12($fp)
	li $a0, 0
	sw $a0 12($a1)
	
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 0
	jr $ra
	
function_Bool__init:
	move $fp, $sp
	subiu $sp, $sp, 0
	# SETATTR
	lw $a1 12($fp)
	li $a0, 0
	sw $a0 12($a1)
	
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 0
	jr $ra
	
function_String__init:
	move $fp, $sp
	subiu $sp, $sp, 4
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 0($fp)
	
	addiu $sp, $sp, 4
	
	# PUSHPARAM
	lw $a0, 0($fp)
	sw $a0 0($sp)
	addiu $sp $sp -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Int__init
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 0($fp)
	
	# POPPARAM
	addiu $sp $sp 4
	
	# SETATTR
	lw $a1 12($fp)
	lw $a0 0($fp)
	sw $a0 12($a1)
	
	# SETATTR
	lw $a1 12($fp)
	la $a0, data_0
	sw $a0 16($a1)
	
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 4
	jr $ra
	
function_A__init:
	move $fp, $sp
	subiu $sp, $sp, 4
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 0($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 0($fp)
	li $a0, 0
	sw $a0 12($a1)
	
	# SETATTR
	lw $a1 12($fp)
	lw $a0 0($fp)
	sw $a0 12($a1)
	
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 4
	jr $ra
	
function_A_value:
	move $fp, $sp
	subiu $sp, $sp, 4
	# GETATTR
	lw $a1 12($fp)
	lw $a0 12($a1)
	sw $a0 0($fp)
	
	# RETURN
	lw $v0, 0($fp)
	addiu $sp, $sp, 4
	jr $ra
	
function_A_set_var:
	move $fp, $sp
	subiu $sp, $sp, 0
	# SETATTR
	lw $a1 12($fp)
	lw $a0 16($fp)
	sw $a0 12($a1)
	
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 0
	jr $ra
	
function_A_method1:
	move $fp, $sp
	subiu $sp, $sp, 0
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 0
	jr $ra
	
function_A_method2:
	move $fp, $sp
	subiu $sp, $sp, 20
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 0($fp)
	
	addiu $sp, $sp, 4
	
	# PUSHPARAM
	lw $a0, 0($fp)
	sw $a0 0($sp)
	addiu $sp $sp -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Int__init
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 0($fp)
	
	# POPPARAM
	addiu $sp $sp 4
	
	# GETATTR
	lw $a1 16($fp)
	lw $a0 12($a1)
	sw $a0 -8($fp)
	
	# GETATTR
	lw $a1 20($fp)
	lw $a0 12($a1)
	sw $a0 -12($fp)
	
	# +
	lw $a0, -8($fp)
	lw $a1, -12($fp)
	add $a0, $a0, $a1
	sw $a0, -4($fp)
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -16($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -16($fp)
	lw $a0 -4($fp)
	sw $a0 12($a1)
	
	# ASSIGN
	lw $a0, -16($fp)
	sw $a0, 0($fp)
	
	# RETURN
	lw $v0, -16($fp)
	addiu $sp, $sp, 20
	jr $ra
	
function_A_method5:
	move $fp, $sp
	subiu $sp, $sp, 68
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 0($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 0($fp)
	li $a0, 1
	sw $a0 12($a1)
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -4($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -4($fp)
	li $a0, 1
	sw $a0 12($a1)
	
_cil_label_LABEL_0:
	# GETATTR
	lw $a1 -4($fp)
	lw $a0 12($a1)
	sw $a0 -20($fp)
	
	# GETATTR
	lw $a1 16($fp)
	lw $a0 12($a1)
	sw $a0 -24($fp)
	
	# <=
	lw $a1, -20($fp)
	lw $a2, -24($fp)
	sle $a0, $a1, $a2
	sw $a0, -16($fp)
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -28($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -28($fp)
	lw $a0 -16($fp)
	sw $a0 12($a1)
	
	# GETATTR
	lw $a1 -28($fp)
	lw $a0 12($a1)
	sw $a0 -12($fp)
	
	# IF GOTO
	lw $a0, -12($fp)
	bnez $a0, _cil_label_LABEL_1
	
	# GOTO
	j _cil_label_LABEL_2
	
_cil_label_LABEL_1:
	# GETATTR
	lw $a1 0($fp)
	lw $a0 12($a1)
	sw $a0 -36($fp)
	
	# GETATTR
	lw $a1 -4($fp)
	lw $a0 12($a1)
	sw $a0 -40($fp)
	
	# *
	lw $a0, -36($fp)
	lw $a1, -40($fp)
	mul $a0, $a0, $a1
	sw $a0, -32($fp)
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -44($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -44($fp)
	lw $a0 -32($fp)
	sw $a0 12($a1)
	
	# ASSIGN
	lw $a0, -44($fp)
	sw $a0, 0($fp)
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -64($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -64($fp)
	li $a0, 1
	sw $a0 12($a1)
	
	# GETATTR
	lw $a1 -4($fp)
	lw $a0 12($a1)
	sw $a0 -52($fp)
	
	# GETATTR
	lw $a1 -64($fp)
	lw $a0 12($a1)
	sw $a0 -56($fp)
	
	# +
	lw $a0, -52($fp)
	lw $a1, -56($fp)
	add $a0, $a0, $a1
	sw $a0, -48($fp)
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -60($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -60($fp)
	lw $a0 -48($fp)
	sw $a0 12($a1)
	
	# ASSIGN
	lw $a0, -60($fp)
	sw $a0, -4($fp)
	
	# GOTO
	j _cil_label_LABEL_0
	
_cil_label_LABEL_2:
	# ALLOCATE
	la $v0 classname_void
	
	# RETURN
	lw $v0, 0($fp)
	addiu $sp, $sp, 68
	jr $ra
	
function_B__init:
	move $fp, $sp
	subiu $sp, $sp, 0
	# RETURN
	lw $v0, 12($fp)
	addiu $sp, $sp, 0
	jr $ra
	
function_B_method5:
	move $fp, $sp
	subiu $sp, $sp, 20
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 0($fp)
	
	addiu $sp, $sp, 4
	
	# PUSHPARAM
	lw $a0, 0($fp)
	sw $a0 0($sp)
	addiu $sp $sp -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Int__init
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 0($fp)
	
	# POPPARAM
	addiu $sp $sp 4
	
	# GETATTR
	lw $a1 16($fp)
	lw $a0 12($a1)
	sw $a0 -8($fp)
	
	# GETATTR
	lw $a1 16($fp)
	lw $a0 12($a1)
	sw $a0 -12($fp)
	
	# *
	lw $a0, -8($fp)
	lw $a1, -12($fp)
	mul $a0, $a0, $a1
	sw $a0, -4($fp)
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -16($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -16($fp)
	lw $a0 -4($fp)
	sw $a0 12($a1)
	
	# ASSIGN
	lw $a0, -16($fp)
	sw $a0, 0($fp)
	
	# RETURN
	lw $v0, -16($fp)
	addiu $sp, $sp, 20
	jr $ra
	
function_B_method3:
	move $fp, $sp
	subiu $sp, $sp, 24
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -12($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -12($fp)
	li $a0, 4
	sw $a0 12($a1)
	
	# ALLOCATE
	lw $t0 48($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -8($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -8($fp)
	lw $a0 -12($fp)
	sw $a0 12($a1)
	
	# SETATTR
	lw $a1 -8($fp)
	la $a0, data_1
	sw $a0 16($a1)
	
	# ALLOCATE
	lw $t0 32($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -20($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -20($fp)
	li $a0, 1
	sw $a0 12($a1)
	
	# ALLOCATE
	lw $t0 48($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -16($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -16($fp)
	lw $a0 -20($fp)
	sw $a0 12($a1)
	
	# SETATTR
	lw $a1 -16($fp)
	la $a0, data_2
	sw $a0 16($a1)
	
	# ALLOCATE
	lw $t0 40($s0)
	sw $t0, 0($sp)
	addiu $sp, $sp, -4
	
	# CALL
	addiu $sp, $sp, -8
	sw $ra, 4($sp)
	sw $fp, 8($sp)
	jal function_Object_copy
	lw $fp, 8($sp)
	lw $ra, 4($sp)
	addiu $sp, $sp, 8
	sw $v0 -4($fp)
	
	addiu $sp, $sp, 4
	
	# SETATTR
	lw $a1 -4($fp)
	lw $a0 0($fp)
	sw $a0 12($a1)
	
	# ASSIGN
	lw $a0, -4($fp)
	sw $a0, 16($fp)
	
	# RETURN
	lw $v0, -4($fp)
	addiu $sp, $sp, 24
	jr $ra
	
	
#####################################

