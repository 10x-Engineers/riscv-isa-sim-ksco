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
    MASK_CODE,
    ARITH_VF_CODE_TEMPLATE,
    ARITH_VI_CODE_TEMPLATE,
    ARITH_VV_CODE_TEMPLATE,
    ARITH_VX_CODE_TEMPLATE,
    ARITH_TEMPLATE,
)

from utils import (
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

    def __init__(self, filename, inst, lmul, eew):
        self.filename = filename
        self.inst = inst
        self.lmul = lmul
        self.eew = eew

    def __str__(self):
        test_data_bytes = (VLEN * self.lmul) // 8 + 8
        test_data = generate_test_data(test_data_bytes)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])

        code_template = (
            UNIT_STRIDE_STORE_CODE_TEMPLATE
            if self.inst == "vse"
            else UNIT_STRIDE_LOAD_CODE_TEMPLATE
        )

        code = ""
        vlmax = (VLEN // self.eew) * self.lmul
        for vl in [vlmax // 2, vlmax - 1, vlmax]:
            code += code_template.format(
                lmul=self.lmul,
                eew=self.eew,
                vl=vl,
                mask_code="",
                v0t="",
                vma="ma",
                vta="ta",
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )

            code += code_template.format(
                lmul=self.lmul,
                eew=self.eew,
                vl=vl,
                mask_code=MASK_CODE,
                v0t=", v0.t",
                vma="ma",
                vta="ta",
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )

            code += code_template.format(
                lmul=self.lmul,
                eew=self.eew,
                vl=vl,
                mask_code="",
                v0t="",
                vma="ma",
                vta="tu",
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )

            code += code_template.format(
                lmul=self.lmul,
                eew=self.eew,
                vl=vl,
                mask_code=MASK_CODE,
                v0t=", v0.t",
                vma="mu",
                vta="ta",
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )

        return (HEADER_TEMPLATE + STRIDE_TEMPLATE).format(
            filename=self.filename,
            inst_name=f"{self.inst}{self.eew}.v",
            extras=f"With LMUL={self.lmul}",
            nbytes=test_data_bytes,
            test_data_str=test_data_str,
            code=code,
        )


class StridedLoad:
    """Generate vlse<EEW>.v tests."""

    def __init__(self, filename, lmul, eew):
        self.filename = filename
        self.lmul = lmul
        self.eew = eew

    def __str__(self):
        maxstride = 2
        test_data_bytes = (vlenb * self.lmul) * max(maxstride, 1) + 8
        test_data = generate_test_data(test_data_bytes)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])

        code = ""
        vlmax = (VLEN // self.eew) * self.lmul
        for vl in [vlmax // 2, vlmax - 1, vlmax]:
            # TODO: Stride can be negative.
            for stride in [i * (self.eew // 8) for i in [0, 1, maxstride]]:

                code += STRIDED_LOAD_CODE_TEMPLATE.format(
                    lmul=self.lmul,
                    eew=self.eew,
                    vl=vl,
                    stride=stride,
                    mask_code="",
                    v0t="",
                    vma="ma",
                    vta="ta",
                    from_reg=self.lmul,
                    to_reg=self.lmul * 2,
                )

                code += STRIDED_LOAD_CODE_TEMPLATE.format(
                    lmul=self.lmul,
                    eew=self.eew,
                    vl=vl,
                    stride=stride,
                    mask_code=MASK_CODE,
                    v0t=", v0.t",
                    vma="ma",
                    vta="ta",
                    from_reg=self.lmul,
                    to_reg=self.lmul * 2,
                )

                code += STRIDED_LOAD_CODE_TEMPLATE.format(
                    lmul=self.lmul,
                    eew=self.eew,
                    vl=vl,
                    stride=stride,
                    mask_code="",
                    v0t="",
                    vma="ma",
                    vta="tu",
                    from_reg=self.lmul,
                    to_reg=self.lmul * 2,
                )

                code += STRIDED_LOAD_CODE_TEMPLATE.format(
                    lmul=self.lmul,
                    eew=self.eew,
                    vl=vl,
                    stride=stride,
                    mask_code=MASK_CODE,
                    v0t=", v0.t",
                    vma="mu",
                    vta="ta",
                    from_reg=self.lmul,
                    to_reg=self.lmul * 2,
                )

        return (HEADER_TEMPLATE + STRIDE_TEMPLATE).format(
            filename=self.filename,
            inst_name=f"vlse{self.eew}.v",
            extras=f"With LMUL={self.lmul}",
            nbytes=test_data_bytes,
            test_data_str=test_data_str,
            code=code,
        )


class Arith:
    """Generate arith instruction tests."""

    def __init__(self, filename, inst, lmul, sew):
        self.filename = filename
        self.inst = inst
        self.lmul = lmul
        self.sew = sew
        self.suffix = inst.split(".", maxsplit=1)[1]

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
            raise Exception("Unknown suffix.", self.suffix)

        vlmax = (VLEN // self.sew) * self.lmul
        code = ""
        for vl in [vlmax // 2, vlmax - 1, vlmax]:
            code += code_template.format(
                sew=self.sew,
                lmul=self.lmul,
                vl=vl,
                mask_code=MASK_CODE if self.suffix.endswith("m") else "",
                vta="ta",
                vma="ma",
                v0t=", v0" if self.suffix.endswith("m") else "",
                op=self.inst,
                imm=floathex(1.0, self.sew) if self.inst.startswith("vf") else 1,
                fmv_unit="w" if self.sew == 32 else "d",
                vd=self.lmul,
                vs1=self.lmul * 2,
                vs2=self.lmul * 3,
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )

            if not self.suffix.endswith("m"):
                code += code_template.format(
                    sew=self.sew,
                    lmul=self.lmul,
                    vl=vl,
                    mask_code=MASK_CODE,
                    vta="ta",
                    vma="ma",
                    v0t=", v0.t",
                    op=self.inst,
                    imm=floathex(1, self.sew) if self.inst.startswith("vf") else 1,
                    fmv_unit="w" if self.sew == 32 else "d",
                    vd=self.lmul,
                    vs1=self.lmul * 2,
                    vs2=self.lmul * 3,
                    from_reg=self.lmul,
                    to_reg=self.lmul * 2,
                )

            code += code_template.format(
                sew=self.sew,
                lmul=self.lmul,
                vl=vl,
                mask_code=MASK_CODE if self.suffix.endswith("m") else "",
                vta="tu",
                vma="ma",
                v0t=", v0" if self.suffix.endswith("m") else "",
                op=self.inst,
                imm=floathex(1, self.sew) if self.inst.startswith("vf") else 1,
                fmv_unit="w" if self.sew == 32 else "d",
                vd=self.lmul,
                vs1=self.lmul * 2,
                vs2=self.lmul * 3,
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )

            if not self.suffix.endswith("m"):
                code += code_template.format(
                    sew=self.sew,
                    lmul=self.lmul,
                    vl=vl,
                    mask_code=MASK_CODE,
                    vta="ta",
                    vma="ma",
                    v0t=", v0" if self.suffix.endswith("m") else ", v0.t",
                    op=self.inst,
                    imm=floathex(1, self.sew) if self.inst.startswith("vf") else 1,
                    fmv_unit="w" if self.sew == 32 else "d",
                    vd=self.lmul,
                    vs1=self.lmul * 2,
                    vs2=self.lmul * 3,
                    from_reg=self.lmul,
                    to_reg=self.lmul * 2,
                )

        return (HEADER_TEMPLATE + ARITH_TEMPLATE).format(
            filename=self.filename,
            inst_name=self.inst,
            extras=f"With LMUL={self.lmul}, SEW={self.sew}",
            nbytes=test_data_bytes,
            test_data=test_data_str,
            code=code,
        )


def main():
    """Main function."""
    for nf in [1, 2, 4, 8]:
        for eew in [8, 16, 32, 64]:
            filename = f"vl{nf}re{eew}.v.S"
            save_to_file(BASE_PATH + filename, str(LoadWhole(filename, nf, eew)))

    for nf in [1, 2, 4, 8]:
        filename = f"vs{nf}r.v.S"
        save_to_file(BASE_PATH + filename, str(StoreWhole(filename, nf)))

    for lmul in [1, 2, 4, 8]:
        for eew in [8, 16, 32, 64]:
            for inst in ["vle", "vse"]:
                filename = f"{inst}{eew}.v_LMUL{lmul}.S"
                test = UnitStrideLoadStore(filename, inst, lmul, eew)
                save_to_file(BASE_PATH + filename, str(test))

    for lmul in [1, 2, 4, 8]:
        for eew in [8, 16, 32, 64]:
            filename = f"vlse{eew}.v_LMUL{lmul}.S"
            test = StridedLoad(filename, lmul, eew)
            save_to_file(BASE_PATH + filename, str(test))

    for lmul in [1, 2, 4, 8]:
        for sew in [8, 16, 32, 64]:
            for inst in [
                "vadc.vim",
                "vadc.vvm",
                "vadc.vxm",
                "vadd.vi",
                "vadd.vv",
                "vadd.vx",
                "vand.vi",
                "vand.vv",
                "vand.vx",
                "vdiv.vv",
                "vdiv.vx",
                "vdivu.vv",
                "vdivu.vx",
                "vmax.vv",
                "vmax.vx",
                "vmaxu.vv",
                "vmaxu.vx",
                "vmerge.vim",
                "vmerge.vvm",
                "vmerge.vxm",
                "vmin.vv",
                "vmin.vx",
                "vminu.vv",
                "vminu.vx",
                "vmul.vv",
                "vmul.vx",
                "vmulh.vv",
                "vmulh.vx",
                "vmulhsu.vv",
                "vmulhsu.vx",
                "vmulhu.vv",
                "vmulhu.vx",
                "vor.vi",
                "vor.vv",
                "vor.vx",
                "vrem.vv",
                "vrem.vx",
                "vremu.vv",
                "vremu.vx",
                "vrgather.vi",
                "vrgather.vv",
                "vrgather.vx",
                "vrsub.vi",
                "vrsub.vx",
                "vsaddu.vi",
                "vsaddu.vv",
                "vsaddu.vx",
                "vsbc.vvm",
                "vsbc.vxm",
                "vslidedown.vi",
                "vslidedown.vx",
                "vslideup.vi",
                "vslideup.vx",
                "vsll.vi",
                "vsll.vv",
                "vsll.vx",
                "vsra.vi",
                "vsra.vv",
                "vsra.vx",
                "vsrl.vi",
                "vsrl.vv",
                "vsrl.vx",
                "vsub.vv",
                "vsub.vx",
                "vxor.vi",
                "vxor.vv",
                "vxor.vx",
            ]:
                filename = f"{inst}_LMUL{lmul}SEW{sew}.S"
                arith = Arith(filename, inst, lmul, sew)
                save_to_file(BASE_PATH + filename, str(arith))

        for sew in [32, 64]:
            for inst in [
                "vfadd.vf",
                "vfadd.vv",
                "vfmax.vf",
                "vfmax.vv",
                "vfmin.vf",
                "vfmin.vv",
                "vfsgnj.vf",
                "vfsgnj.vv",
                "vfsgnjn.vf",
                "vfsgnjn.vv",
                "vfsgnjx.vf",
                "vfsgnjx.vv",
                "vfsub.vf",
                "vfsub.vv",
            ]:
                filename = f"{inst}_LMUL{lmul}SEW{sew}.S"
                arith = Arith(filename, inst, lmul, sew)
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
