    j Lmain
Lmain: # begin_block fibonacci
L2: lw t0, -0(sp)
    lw t1, -0(sp)
    sub t2, t0, t1
    sw t2, -0(sp)
L3: lw t0, -0(sp)  # par cv
    sw t0, -100(sp)
L4: addi t0, sp, -0  # par ret
    sw t0, -104(sp)
L5: jal fibonacci
L6: lw t0, -0(sp)
    lw t1, -0(sp)
    sub t2, t0, t1
    sw t2, -0(sp)
L7: lw t0, -0(sp)  # par cv
    sw t0, -100(sp)
L8: addi t0, sp, -0  # par ret
    sw t0, -104(sp)
L9: jal fibonacci
L10: lw t0, -0(sp)
    lw t1, -0(sp)
    add t2, t0, t1
    sw t2, -0(sp)
L11: lw t0, -0(sp)
    lw t1, -8(sp)
    sw t0, 0(t1)
L12: lw ra, -0(sp)
    ret
fibonacci: # begin_block fibonacci
L14: call read_int
    sw a0, -0(sp)
L15: lw t0, -0(sp)  # par cv
    sw t0, -100(sp)
L16: addi t0, sp, -4  # par ret
    sw t0, -104(sp)
L17: jal fibonacci
L18: lw a0, -4(sp)
    call print_int
L19: # halt
L20: lw ra, -0(sp)
    ret

# Runtime routines
read_int:
    li a7, 5
    ecall
    ret

print_int:
    li a7, 1
    ecall
    ret
