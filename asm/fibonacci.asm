L0: b Lmain
L1: sw $ra,-0($sp)
L1: // begin_block for fibonacci
L2: lw $t1,-0($sp)
    li $t2,1
    sub $t1,$t1,$t2
    sw $t1,-0($sp)
L3: lw $t1,-0($sp)   // par cv
    sw $t1,-100($sp)   // store parameter value
L4: lw $t1,-0($sp)   // par ret
    sw $t1,-104($sp)   // store return value
L5: jal fibonacci
L6: lw $t1,-0($sp)
    li $t2,2
    sub $t1,$t1,$t2
    sw $t1,-0($sp)
L7: lw $t1,-0($sp)   // par cv
    sw $t1,-100($sp)   // store parameter value
L8: lw $t1,-0($sp)   // par ret
    sw $t1,-104($sp)   // store return value
L9: jal fibonacci
L10: lw $t1,-0($sp)
    li $t2,T_4
    add $t1,$t1,$t2
    sw $t1,-0($sp)
L11: lw $t0,-0($sp)
    lw $t1,($t0)
    lw $t0,-8($sp)
    sw $t1,($t0)
L12: lw $ra,-0($sp)
    jr $ra
L13: // begin_block for fibonacci
L14: jal read_int
    sw $v0,-0($sp)
L15: lw $t1,-0($sp)   // par cv
    sw $t1,-100($sp)   // store parameter value
L16: lw $t1,-4($sp)   // par ret
    sw $t1,-104($sp)   // store return value
L17: jal fibonacci
L18: lw $t1,-4($sp)
    move $a0,$t1
    jal print_int
L19: // halt
L20: lw $ra,-0($sp)
    jr $ra
