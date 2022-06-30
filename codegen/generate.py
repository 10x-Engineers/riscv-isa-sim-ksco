#!/usr/bin/python3

"""
Generate RV64 tests.
"""

import os
import sys
from constants import VLEN, vlenb, BASE_PATH
from templates import (
    HEADER_TEMPLATE,
    LOAD_WHOLE_TEMPLATE,
    STORE_WHOLE_TEMPLATE,
    MAKEFRAG_TEMPLATE,
    STRIDE_TEMPLATE,
    UNIT_STRIDE_LOAD_CODE_TEMPLATE,
    UNIT_STRIDE_STORE_CODE_TEMPLATE,
    STRIDED_LOAD_CODE_TEMPLATE,
    INDEXED_LOAD_CODE_TEMPLATE,
    INDEXED_TEMPLATE,
    MASK_CODE,
    ARITH_VF_CODE_TEMPLATE,
    ARITH_VI_CODE_TEMPLATE,
    ARITH_VV_CODE_TEMPLATE,
    ARITH_VX_CODE_TEMPLATE,
    ARITH_TEMPLATE,
)
from utils import (
    generate_indexed_data,
    generate_test_data,
    save_to_file,
    floathex,
)


class LoadWhole:
    """Generate vl<NF>re<EEW>.v tests."""

    def __init__(self, filename, nf, eew):
        self.filename = filename
        self.nf = nf
        self.eew = eew

    def __str__(self):
        nbytes = vlenb * self.nf
        test_data = generate_test_data(nbytes)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])
        return (HEADER_TEMPLATE + LOAD_WHOLE_TEMPLATE).format(
            filename=self.filename,
            inst_name=f"vl{self.nf}re{self.eew}.v",
            extras="",
            nf=self.nf,
            nbytes=nbytes,
            eew=self.eew,
            test_data_str=test_data_str,
            from_reg=0,
            to_reg=self.nf,
        )


class StoreWhole:
    """Generate vs<NF>r.v tests."""

    def __init__(self, filename, nf):
        self.filename = filename
        self.nf = nf

    def __str__(self):
        nbytes = vlenb * self.nf
        test_data = generate_test_data(nbytes)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])
        return (HEADER_TEMPLATE + STORE_WHOLE_TEMPLATE).format(
            filename=self.filename,
            inst_name=f"vs{self.nf}r.v",
            extras="",
            nf=self.nf,
            nbytes=nbytes,
            test_data_str=test_data_str,
            from_reg=self.nf,
            to_reg=self.nf * 2,
        )


class UnitStrideLoadStore:
    """Generate vle<EEW>.v, vse<EEW>.v tests."""

    def __init__(self, filename, inst, lmul, eew, vl):
        self.filename = filename
        self.inst = inst
        self.lmul = lmul
        self.eew = eew
        self.vl = vl

    def __str__(self):
        nbytes = (self.vl * self.eew) // 8
        test_data_bytes = (VLEN * self.lmul) // 8 + 8
        test_data = generate_test_data(test_data_bytes)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])

        code_template = (
            UNIT_STRIDE_STORE_CODE_TEMPLATE
            if self.inst == "vse"
            else UNIT_STRIDE_LOAD_CODE_TEMPLATE
        )
        code_vm0_ta_ma = code_template.format(
            lmul=self.lmul,
            eew=self.eew,
            vl=self.vl,
            mask_code="",
            v0t="",
            vma="ma",
            vta="ta",
        )

        code_vm1_ta_ma = code_template.format(
            lmul=self.lmul,
            eew=self.eew,
            vl=self.vl,
            mask_code=MASK_CODE,
            v0t=", v0.t",
            vma="ma",
            vta="ta",
        )

        code_vm0_tu_ma = code_template.format(
            lmul=self.lmul,
            eew=self.eew,
            vl=self.vl,
            mask_code="",
            v0t="",
            vma="ma",
            vta="tu",
        )

        code_vm1_ta_mu = code_template.format(
            lmul=self.lmul,
            eew=self.eew,
            vl=self.vl,
            mask_code=MASK_CODE,
            v0t=", v0.t",
            vma="mu",
            vta="ta",
        )

        return (HEADER_TEMPLATE + STRIDE_TEMPLATE).format(
            filename=self.filename,
            inst_name=f"{self.inst}{self.eew}.v",
            extras=f"With LMUL={self.lmul}, VL={self.vl}",
            nbytes=test_data_bytes,
            test_data_str=test_data_str,
            code_vm0_ta_ma=code_vm0_ta_ma,
            code_vm1_ta_ma=code_vm1_ta_ma,
            code_vm0_tu_ma=code_vm0_tu_ma,
            code_vm1_ta_mu=code_vm1_ta_mu,
            from_reg=self.lmul,
            to_reg=self.lmul * 2,
        )


class StridedLoad:
    """Generate vlse<EEW>.v tests."""

    def __init__(self, filename, lmul, eew, vl, stride):
        self.filename = filename
        self.lmul = lmul
        self.eew = eew
        self.vl = vl
        self.stride = stride

    def __str__(self):
        test_data_bytes = (vlenb * self.lmul) * max(self.stride, 1) + 8
        test_data = generate_test_data(test_data_bytes)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])

        code_vm0_ta_ma = STRIDED_LOAD_CODE_TEMPLATE.format(
            lmul=self.lmul,
            eew=self.eew,
            vl=self.vl,
            stride=self.stride,
            mask_code="",
            v0t="",
            vma="ma",
            vta="ta",
        )

        code_vm1_ta_ma = STRIDED_LOAD_CODE_TEMPLATE.format(
            lmul=self.lmul,
            eew=self.eew,
            vl=self.vl,
            stride=self.stride,
            mask_code=MASK_CODE,
            v0t=", v0.t",
            vma="ma",
            vta="ta",
        )

        code_vm0_tu_ma = STRIDED_LOAD_CODE_TEMPLATE.format(
            lmul=self.lmul,
            eew=self.eew,
            vl=self.vl,
            stride=self.stride,
            mask_code="",
            v0t="",
            vma="ma",
            vta="tu",
        )

        code_vm1_ta_mu = STRIDED_LOAD_CODE_TEMPLATE.format(
            lmul=self.lmul,
            eew=self.eew,
            vl=self.vl,
            mask_code=MASK_CODE,
            stride=self.stride,
            v0t=", v0.t",
            vma="mu",
            vta="ta",
        )

        return (HEADER_TEMPLATE + STRIDE_TEMPLATE).format(
            filename=self.filename,
            inst_name=f"vlse{self.eew}.v",
            extras=f"With LMUL={self.lmul}, VL={self.vl}, STRIDE={self.stride}",
            nbytes=test_data_bytes,
            test_data_str=test_data_str,
            code_vm0_ta_ma=code_vm0_ta_ma,
            code_vm1_ta_ma=code_vm1_ta_ma,
            code_vm0_tu_ma=code_vm0_tu_ma,
            code_vm1_ta_mu=code_vm1_ta_mu,
            from_reg=self.lmul,
            to_reg=self.lmul * 2,
        )


class Arith:
    """Generate arith instruction tests."""

    def __init__(self, filename, inst, lmul, sew, vl, suffix):
        self.filename = filename
        self.inst = inst
        self.lmul = lmul
        self.sew = sew
        self.vl = vl
        self.suffix = suffix

    def __str__(self):
        test_data_bytes = (VLEN * self.lmul) // 8 + 8
        test_data = generate_test_data(test_data_bytes, width=self.sew)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])

        if self.suffix in ["vv", "vvm"]:
            code_template = ARITH_VV_CODE_TEMPLATE
        elif self.suffix in ["vi", "vim"]:
            code_template = ARITH_VI_CODE_TEMPLATE
        elif self.suffix in ["vx", "vxm"]:
            code_template = ARITH_VX_CODE_TEMPLATE
        elif self.suffix in ["vf"]:
            code_template = ARITH_VF_CODE_TEMPLATE
        else:
            raise Exception("Unknown suffix.")

        code_vm0_ta_ma = code_template.format(
            sew=self.sew,
            lmul=self.lmul,
            vl=self.vl,
            mask_code=MASK_CODE if self.suffix.endswith("m") else "",
            vta="ta",
            vma="ma",
            v0t=", v0" if self.suffix.endswith("m") else "",
            op=f"v{self.inst}.{self.suffix}",
            imm=floathex(1.0, self.sew) if self.inst.startswith("f") else 1,
            fmv_unit="w" if self.sew == 32 else "d",
            vd=self.lmul,
            vs1=self.lmul * 2,
            vs2=self.lmul * 3,
            from_reg=self.lmul,
            to_reg=self.lmul * 2,
        )

        code_vm1_ta_ma = ""
        if not self.suffix.endswith("m"):
            code_vm1_ta_ma = code_template.format(
                sew=self.sew,
                lmul=self.lmul,
                vl=self.vl,
                mask_code=MASK_CODE,
                vta="ta",
                vma="ma",
                v0t=", v0.t",
                op=f"v{self.inst}.{self.suffix}",
                imm=floathex(1, self.sew) if self.inst.startswith("f") else 1,
                fmv_unit="w" if self.sew == 32 else "d",
                vd=self.lmul,
                vs1=self.lmul * 2,
                vs2=self.lmul * 3,
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )

        code_vm0_tu_ma = code_template.format(
            sew=self.sew,
            lmul=self.lmul,
            vl=self.vl,
            mask_code=MASK_CODE if self.suffix.endswith("m") else "",
            vta="tu",
            vma="ma",
            v0t=", v0" if self.suffix.endswith("m") else "",
            op=f"v{self.inst}.{self.suffix}",
            imm=floathex(1, self.sew) if self.inst.startswith("f") else 1,
            fmv_unit="w" if self.sew == 32 else "d",
            vd=self.lmul,
            vs1=self.lmul * 2,
            vs2=self.lmul * 3,
            from_reg=self.lmul,
            to_reg=self.lmul * 2,
        )

        code_vm1_ta_mu = ""
        if not self.suffix.endswith("m"):
            code_vm1_ta_mu = code_template.format(
                sew=self.sew,
                lmul=self.lmul,
                vl=self.vl,
                mask_code=MASK_CODE,
                vta="ta",
                vma="ma",
                v0t=", v0" if self.suffix.endswith("m") else ", v0.t",
                op=f"v{self.inst}.{self.suffix}",
                imm=floathex(1, self.sew) if self.inst.startswith("f") else 1,
                fmv_unit="w" if self.sew == 32 else "d",
                vd=self.lmul,
                vs1=self.lmul * 2,
                vs2=self.lmul * 3,
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )

        return (HEADER_TEMPLATE + ARITH_TEMPLATE).format(
            filename=self.filename,
            inst_name=f"v{self.inst}.{self.suffix}",
            extras=f"With LMUL={self.lmul}, SEW={self.sew}, VL={self.vl}",
            nbytes=test_data_bytes,
            test_data=test_data_str,
            code_vm0_ta_ma=code_vm0_ta_ma,
            code_vm1_ta_ma=code_vm1_ta_ma,
            code_vm0_tu_ma=code_vm0_tu_ma,
            code_vm1_ta_mu=code_vm1_ta_mu,
        )


def main():
    """Main function."""
    for nf in [1, 2, 4, 8]:
        for eew in [8, 16, 32, 64]:
            filename = f"vl{nf}re{eew}_v.S"
            save_to_file(BASE_PATH + filename, str(LoadWhole(filename, nf, eew)))

    for nf in [1, 2, 4, 8]:
        filename = f"vs{nf}r_v.S"
        save_to_file(BASE_PATH + filename, str(StoreWhole(filename, nf)))

    for lmul in [1, 2, 4, 8]:
        for eew in [8, 16, 32, 64]:
            vlmax = (VLEN // eew) * lmul
            for vl in [vlmax // 2, vlmax - 1, vlmax]:
                for inst in ["vle", "vse"]:
                    filename = f"{inst}{eew}_v_LMUL{lmul}VL{vl}.S"
                    test = UnitStrideLoadStore(filename, inst, lmul, eew, vl)
                    save_to_file(BASE_PATH + filename, str(test))

    for lmul in [1, 2, 4, 8]:
        for eew in [8, 16, 32, 64]:
            vlmax = (VLEN // eew) * lmul
            for vl in [vlmax // 2, vlmax - 1, vlmax]:
                for stride in [i * (eew // 8) for i in [0, 1, 2]]:
                    filename = f"vlse{eew}_v_LMUL{lmul}VL{vl}STRIDE{stride}.S"
                    test = StridedLoad(filename, lmul, eew, vl, stride)
                    save_to_file(BASE_PATH + filename, str(test))

    for lmul in [1, 2, 4, 8]:
        for sew in [8, 16, 32, 64]:
            vlmax = (VLEN // sew) * lmul
            for vl in [vlmax // 2, vlmax - 1, vlmax]:
                for inst in [
                    "add",
                    "sub",
                    "minu",
                    "min",
                    "maxu",
                    "max",
                    "and",
                    "or",
                    "xor",
                    "divu",
                    "div",
                    "rem",
                    "remu",
                    "mulhu",
                    "mul",
                    "mulhsu",
                    "mulh",
                    "rgather",
                    "saddu",
                    "sll",
                    "srl",
                    "sra",
                ]:
                    filename = f"v{inst}_vv_LMUL{lmul}SEW{sew}VL{vl}.S"
                    arith = Arith(filename, inst, lmul, sew, vl, "vv")
                    save_to_file(BASE_PATH + filename, str(arith))

                for inst in [
                    "add",
                    "rsub",
                    "and",
                    "or",
                    "xor",
                    "rgather",
                    "slideup",
                    "slidedown",
                    "saddu",
                    "sll",
                    "srl",
                    "sra",
                ]:
                    filename = f"v{inst}_vi_LMUL{lmul}SEW{sew}VL{vl}.S"
                    arith = Arith(filename, inst, lmul, sew, vl, "vi")
                    save_to_file(BASE_PATH + filename, str(arith))
                for inst in [
                    "add",
                    "sub",
                    "rsub",
                    "minu",
                    "min",
                    "maxu",
                    "max",
                    "and",
                    "or",
                    "xor",
                    "divu",
                    "div",
                    "rem",
                    "remu",
                    "mulhu",
                    "mul",
                    "mulhsu",
                    "mulh",
                    "rgather",
                    "slideup",
                    "slidedown",
                    "saddu",
                    "sll",
                    "srl",
                    "sra",
                ]:
                    filename = f"v{inst}_vx_LMUL{lmul}SEW{sew}VL{vl}.S"
                    arith = Arith(filename, inst, lmul, sew, vl, "vx")
                    save_to_file(BASE_PATH + filename, str(arith))
                for inst in ["adc", "sbc", "merge"]:
                    filename = f"v{inst}_vvm_LMUL{lmul}SEW{sew}VL{vl}.S"
                    arith = Arith(filename, inst, lmul, sew, vl, "vvm")
                    save_to_file(BASE_PATH + filename, str(arith))
                for inst in ["adc", "merge"]:
                    filename = f"v{inst}_vim_LMUL{lmul}SEW{sew}VL{vl}.S"
                    arith = Arith(filename, inst, lmul, sew, vl, "vim")
                    save_to_file(BASE_PATH + filename, str(arith))
                for inst in ["adc", "sbc", "merge"]:
                    filename = f"v{inst}_vxm_LMUL{lmul}SEW{sew}VL{vl}.S"
                    arith = Arith(filename, inst, lmul, sew, vl, "vxm")
                    save_to_file(BASE_PATH + filename, str(arith))

        for sew in [32, 64]:
            vlmax = (VLEN // sew) * lmul
            for vl in [vlmax // 2, vlmax - 1, vlmax]:
                for inst in [
                    "fadd",
                    "fsub",
                    "fmin",
                    "fmax",
                    "fsgnj",
                    "fsgnjn",
                    "fsgnjx",
                ]:
                    filename = f"v{inst}_vv_LMUL{lmul}SEW{sew}VL{vl}.S"
                    arith = Arith(filename, inst, lmul, sew, vl, "vv")
                    save_to_file(BASE_PATH + filename, str(arith))
                for inst in [
                    "fadd",
                    "fsub",
                    "fmin",
                    "fmax",
                    "fsgnj",
                    "fsgnjn",
                    "fsgnjx",
                ]:
                    filename = f"v{inst}_vf_LMUL{lmul}SEW{sew}VL{vl}.S"
                    arith = Arith(filename, inst, lmul, sew, vl, "vf")
                    save_to_file(BASE_PATH + filename, str(arith))

    files = []
    for file in sorted(os.listdir(BASE_PATH)):
        if file.startswith("v"):
            filename = file.rstrip(".S")
            files.append(f"  {filename} \\")
    with open(BASE_PATH + "Makefrag", "w", encoding="UTF-8") as f:
        f.write(MAKEFRAG_TEMPLATE.format(data="\n".join(files)))


if __name__ == "__main__":
    sys.exit(main())
