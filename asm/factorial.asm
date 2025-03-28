    la sp, _stack
    j Lmain
Lmain: # begin_block factorial
    sw ra, 20(sp)  # save ra
    addi sp, sp, -20  # allocate frame
L2: call read_int
    sw a0, 20(sp)
L3: li t0, 1
    sw t0, 12(sp)
L4: li t0, 1
    sw t0, 16(sp)
L5: lw t0, 16(sp)
    lw t1, 20(sp)
    ble t0, t1, L7
L6: j L12
L7: lw t0, 12(sp)
    lw t1, 16(sp)
    mul t2, t0, t1
    sw t2, 8(sp)
L8: lw t0, 8(sp)
    sw t0, 12(sp)
L9: lw t0, 16(sp)
    lw t1, 20(sp)
    add t2, t0, t1
    sw t2, 4(sp)
L10: lw t0, 4(sp)
    sw t0, 16(sp)
L11: j L5
L12: lw a0, 12(sp)
    call print_int
L13: # halt
L14: lw ra, 20(sp)
    addi sp, sp, 20  # deallocate frame
    ret

.data
_stack: .space 1024
str_nl: .asciz "\n"
.text

# Runtime routines
read_int:
    li a7, 5
    ecall
    ret

print_int:
    li a7, 1
    ecall
    ret
