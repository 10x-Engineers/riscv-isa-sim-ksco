"""
Templates.
"""

MAKEFRAG_TEMPLATE = """
#=======================================================================
# Makefrag for rv64uv tests
#-----------------------------------------------------------------------

rv64uv_sc_tests = \\
{data}

rv64uv_p_tests = $(addprefix rv64uv-p-, $(rv64uv_sc_tests))
"""

HEADER_TEMPLATE = """
# See LICENSE for license details.

# This file is automatically generated. Do not edit.

#*****************************************************************************
# {filename}
#-----------------------------------------------------------------------------
#
# Test {insn_name} insnructions.
# {extras}
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64UV
"""

MASK_CODE = """
  li t0, -1
  vsetvli t1, t0, e8,m1,ta,ma
  la a3, mask
  vle8.v v0, (a3)
"""

LOAD_WHOLE_TEMPLATE = """
RVTEST_CODE_BEGIN

  li t0, -1
  vsetvli t1, t0, e{eew},m{nf}
  la a2, tdat
  mv s1, a2
  addi a2, a2, 8
  vle{eew}.v v0, (a2)

  vl{nf}re{eew}.v v0, (s1)

  li t0, -1
  vsetvli t1, t0, e{eew},m{nf}
  la a1, res
  vse{eew}.v v0, (a1)

  addi x0, x{from_reg}, {to_reg}

  TEST_CASE(2, x0, 0x0)
  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

res:
  .zero {nbytes}

tdat:
{test_data_str}

RVTEST_DATA_END
"""

STORE_WHOLE_TEMPLATE = """
RVTEST_CODE_BEGIN

  li t0, -1
  vsetvli t1, t0, e8,m{nf}
  la a2, tdat
  mv s1, a2
  addi a2, a2, 8
  vle8.v v0, (a2)
  la a1, res
  vse8.v v0, (a1)
  vle8.v v{nf}, (s1)

  vs{nf}r.v v{nf}, (a1)

  addi x0, x{from_reg}, {to_reg}

  TEST_CASE(2, x0, 0x0)
  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

res:
  .zero {nbytes}

tdat:
{test_data_str}

RVTEST_DATA_END
"""

UNIT_STRIDE_LOAD_CODE_TEMPLATE = """
  li t0, -1
  vsetvli t1, t0, e{eew},m{lmul},ta,ma
  la a2, tdat
  mv s1, a2
  addi a2, a2, 8
  vle{eew}.v v{lmul}, (a2)

  {mask_code}
  li t0, {vl}
  vsetvli t1, t0, e{eew},m{lmul},{vta},{vma}
  vle{eew}.v v{lmul}, (s1){v0t}

  li t0, -1
  vsetvli t1, t0, e{eew},m{lmul},ta,ma
  la a1, res
  vse{eew}.v v{lmul}, (a1)

  addi x0, x{from_reg}, {to_reg}"""

UNIT_STRIDE_STORE_CODE_TEMPLATE = """
  li t0, -1
  vsetvli t1, t0, e{eew},m{lmul},ta,ma
  la a2, tdat
  mv s1, a2
  addi a2, a2, 8
  vle{eew}.v v{lmul}, (a2)
  la a1, res
  vse{eew}.v v{lmul}, (a1)
  vle{eew}.v v{lmul}, (s1)

  {mask_code}
  li t0, {vl}
  vsetvli t1, t0, e{eew},m{lmul},{vta},{vma}
  vse{eew}.v v{lmul}, (a1){v0t}

  li t0, -1
  vsetvli t1, t0, e{eew},m{lmul},ta,ma
  vle{eew}.v v{lmul}, (a1)

  addi x0, x{from_reg}, {to_reg}"""

STRIDE_TEMPLATE = """
RVTEST_CODE_BEGIN

{code}

  TEST_CASE(2, x0, 0x0)
  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

res:
  .zero {nbytes}

tdat:
{test_data_str}

mask:
  .quad 0x5555555555555555
  .quad 0x5555555555555555
  .quad 0x5555555555555555
  .quad 0x5555555555555555

RVTEST_DATA_END
"""

STRIDED_LOAD_CODE_TEMPLATE = """
  li t0, -1
  vsetvli t1, t0, e{eew},m{lmul},ta,ma
  la a2, tdat
  mv s1, a2
  addi a2, a2, 8
  vle{eew}.v v{lmul}, (a2)

  {mask_code}
  li t0, {vl}
  vsetvli t1, t0, e{eew},m{lmul},{vta},{vma}
  li t0, {stride}
  vlse{eew}.v v{lmul}, (s1), t0{v0t}

  li t0, -1
  vsetvli t1, t0, e{eew},m{lmul},{vta},{vma}
  la a1, res
  vse{eew}.v v{lmul}, (a1)

  addi x0, x{from_reg}, {to_reg}"""

INDEXED_TEMPLATE = """
RVTEST_CODE_BEGIN

{code}

  TEST_CASE(2, x0, 0x0)
  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

res:
  .zero {nbytes}

tdat:
{test_data_str}

idat:
{index_data_str}

mask:
  .quad 0x5555555555555555
  .quad 0x5555555555555555
  .quad 0x5555555555555555
  .quad 0x5555555555555555

RVTEST_DATA_END
"""

INDEXED_LOAD_CODE_TEMPLATE = """
  li t0, -1
  vsetvli t1, t0, e{sew},m{lmul},ta,ma
  la a2, tdat
  mv s1, a2
  addi a2, a2, 8
  vle{sew}.v v{vd}, (a2)

  li t0, {vl}
  vsetvli t1, t0, e{offset_eew},m{emul},ta,ma
  la a2, idat
  vle{offset_eew}.v v{vs2}, (a2)

  {mask_code}
  li t0, {vl}
  vsetvli t1, t0, e{sew},m{lmul},{vta},{vma}
  {insn}{offset_eew}.v v{vd}, (s1), v{vs2}{v0t}

  li t0, -1
  vsetvli t1, t0, e{sew},m{lmul},ta,ma
  la a1, res
  vse{sew}.v v{vd}, (a1)

  addi x0, x{from_reg}, {to_reg}"""

ARITH_VV_CODE_TEMPLATE = """
  li t0, -1
  vsetvli t1, t0, e{sew},m{lmul},ta,ma
  la a2, tdat
  vle{sew}.v v{vs1}, (a2)

  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  vle{sew}.v v{vd}, (a2)
  la a2, tdat+8

  vsetvli t1, t0, e{sew},m{lmul},ta,ma
  vle{sew}.v v{vs2}, (a2)

  {mask_code}
  li t0, {vl}
  vsetvli t1, t0, e{sew},m{lmul},{vta},{vma}
  {op} v{vd}, v{vs1}, v{vs2}{v0t}

  li t0, -1
  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  la a1, res
  vse{sew}.v v{vd}, (a1)

  addi x0, x{from_reg}, {to_reg}
"""

ARITH_VI_CODE_TEMPLATE = """
  li t0, -1
  vsetvli t1, t0, e{sew},m{lmul},ta,ma
  la a2, tdat
  vle{sew}.v v{vs1}, (a2)

  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  vle{sew}.v v{vd}, (a2)

  {mask_code}
  li t0, {vl}
  vsetvli t1, t0, e{sew},m{lmul},{vta},{vma}
  {op} v{vd}, v{vs1}, {imm}{v0t}

  li t0, -1
  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  la a1, res
  vse{sew}.v v{vd}, (a1)

  addi x0, x{from_reg}, {to_reg}
"""

ARITH_VX_CODE_TEMPLATE = """
  li t0, -1
  vsetvli t1, t0, e{sew},m{lmul},ta,ma
  la a2, tdat
  vle{sew}.v v{vs1}, (a2)

  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  vle{sew}.v v{vd}, (a2)

  {mask_code}
  li t0, {vl}
  vsetvli t1, t0, e{sew},m{lmul},{vta},{vma}
  li t2, {imm}
  {op} v{vd}, v{vs1}, t2{v0t}

  li t0, -1
  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  la a1, res
  vse{sew}.v v{vd}, (a1)

  addi x0, x{from_reg}, {to_reg}
"""

ARITH_MUL_ADD_VX_CODE_TEMPLATE = """
  li t0, -1
  vsetvli t1, t0, e{sew},m{lmul},ta,ma
  la a2, tdat
  vle{sew}.v v{vs1}, (a2)

  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  vle{sew}.v v{vd}, (a2)

  {mask_code}
  li t0, {vl}
  vsetvli t1, t0, e{sew},m{lmul},{vta},{vma}
  li t2, {imm}
  {op} v{vd}, t2, v{vs1}{v0t}

  li t0, -1
  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  la a1, res
  vse{sew}.v v{vd}, (a1)

  addi x0, x{from_reg}, {to_reg}
"""

ARITH_VF_CODE_TEMPLATE = """
  li t0, -1
  vsetvli t1, t0, e{sew},m{lmul},ta,ma
  la a2, tdat
  vle{sew}.v v{vs1}, (a2)

  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  vle{sew}.v v{vd}, (a2)

  {mask_code}
  li t0, {vl}
  vsetvli t1, t0, e{sew},m{lmul},{vta},{vma}
  li t2, {imm}
  fmv.{fmv_unit}.x f2, t2
  {op} v{vd}, v{vs1}, f2{v0t}

  li t0, -1
  vsetvli t1, t0, e{sew},m{vd_lmul},ta,ma
  la a1, res
  vse{sew}.v v{vd}, (a1)

  addi x0, x{from_reg}, {to_reg}
"""

ARITH_TEMPLATE = """
RVTEST_CODE_BEGIN

{code}

  TEST_CASE(2, x0, 0x0)
  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

res:
  .zero {nbytes}

tdat:
{test_data}

mask:
  .quad 0x5555555555555555
  .quad 0x5555555555555555
  .quad 0x5555555555555555
  .quad 0x5555555555555555

RVTEST_DATA_END
"""
