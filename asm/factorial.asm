L0: b Lmain
L1: sw $ra,-0($sp)
L1: // begin_block for factorial
L2: jal read_int
    sw $v0,-0($sp)
L3: li $t1,1
    sw $t1,-8($sp)
L4: li $t1,1
    sw $t1,-4($sp)
L5: // Unhandled op: <= i x 7
L6: j 12
L7: lw $t1,-8($sp)
    lw $t2,-4($sp)
    mul $t1,$t1,$t2
    sw $t1,-12($sp)
L8: lw $t1,-12($sp)
    lw $t0,-8($sp)
    sw $t1,($t0)
L9: lw $t1,-4($sp)
    li $t2,1
    add $t1,$t1,$t2
    sw $t1,-16($sp)
L10: lw $t1,-16($sp)
    lw $t0,-4($sp)
    sw $t1,($t0)
L11: j 5
L12: lw $t1,-8($sp)
    move $a0,$t1
    jal print_int
L13: // halt
L14: lw $ra,-0($sp)
    jr $ra
