    j Lmain
Lmain: # begin_block countDigits
L2: call read_int
    sw a0, -0(sp)
L3: li t0, 0
    sw t0, -4(sp)
L4: lw t0, -0(sp)
    lw t1, -0(sp)
    bgt t0, t1, L6
L5: j L11
L6: lw t0, -0(sp)
    lw t1, -0(sp)
    div t2, t0, t1
    sw t2, -8(sp)
L7: lw t0, -8(sp)
    sw t0, -0(sp)
L8: lw t0, -4(sp)
    lw t1, -0(sp)
    add t2, t0, t1
    sw t2, -12(sp)
L9: lw t0, -12(sp)
    sw t0, -4(sp)
L10: j L4
L11: lw a0, -4(sp)
    call print_int
L12: # halt
L13: lw ra, -0(sp)
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
