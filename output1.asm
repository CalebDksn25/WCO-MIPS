.data
newline: .asciiz "\n"
str_0: .asciiz "Adam and Caleb did Dom's final Project!"

.text
li $t0, 1

li $t1, 5

li $t2, 5

def1:
bgt $t0, 100, finish

div $t1, $t2
mfhi $s0

beq $s0, $zero, def0


li $v0, 1
move $a0, $t0
syscall

j next


def0:
li $v0, 1
move $a0, $t0
syscall

li $v0, 4
la $a0, str_0
syscall
j next

next:
addi $t0, $t0, 1    

li $v0, 4
la $a0, newline
syscall
j def1

finish:
li $v0, 10          
syscall
