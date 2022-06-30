static int ncase = 2;

if (insn.rd() == 0 && insn.i_imm() != 0) {
    for (int reg = insn.rs1(); reg < insn.i_imm(); reg++) {
        for (int i = 0; i < P.VU.VLEN / 64; i++) {
            printf(
                "  TEST_CASE(%d, t0, 0x%llx, ld t0, 0(a1); addi a1, a1, 8)\n",
                ncase++,
                P.VU.elt<type_sew_t<64>::type>(reg, i, false));
        }
    }

    printf("---\n");
}

WRITE_RD(sext_xlen(RS1 + insn.i_imm()));
