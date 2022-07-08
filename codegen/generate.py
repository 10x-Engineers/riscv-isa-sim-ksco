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
    ARITH_MUL_ADD_VX_CODE_TEMPLATE,
    ARITH_MUL_ADD_VF_CODE_TEMPLATE,
    ARITH_VMV_VI_CODE_TEMPLATE,
    ARITH_VMV_VV_CODE_TEMPLATE,
    ARITH_VMV_VX_CODE_TEMPLATE,
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
            insn_name=f"vl{self.nf}re{self.eew}.v",
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
            insn_name=f"vs{self.nf}r.v",
            extras="",
            nf=self.nf,
            nbytes=nbytes,
            test_data_str=test_data_str,
            from_reg=self.nf,
            to_reg=self.nf * 2,
        )


class UnitStrideLoadStore:
    """Generate vle<EEW>.v, vse<EEW>.v tests."""

    def __init__(self, filename, insn, lmul, eew):
        self.filename = filename
        self.insn = insn
        self.lmul = lmul
        self.eew = eew

    def __str__(self):
        test_data_bytes = (VLEN * self.lmul) // 8 + 8
        test_data = generate_test_data(test_data_bytes)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])

        code_template = (
            UNIT_STRIDE_STORE_CODE_TEMPLATE
            if self.insn == "vse"
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
            insn_name=f"{self.insn}{self.eew}.v",
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
            insn_name=f"vlse{self.eew}.v",
            extras=f"With LMUL={self.lmul}",
            nbytes=test_data_bytes,
            test_data_str=test_data_str,
            code=code,
        )


class Arith:
    """Generate arith insnruction tests."""

    def __init__(self, filename, insn, lmul, sew):
        self.filename = filename
        self.insn = insn
        self.lmul = lmul
        self.sew = sew
        self.suffix = insn.split(".", maxsplit=1)[1]

    def __str__(self):
        test_data_bytes = (VLEN * self.lmul * 2) // 8 + 8
        test_data = generate_test_data(test_data_bytes, width=self.sew)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])

        if self.suffix in ["vv", "vvm", "vs", "mm", "wv", "vm"]:
            code_template = ARITH_VV_CODE_TEMPLATE
        elif self.suffix in ["vi", "vim", "wi"]:
            code_template = ARITH_VI_CODE_TEMPLATE
        elif self.suffix in ["vx", "vxm", "wx"]:
            if self.insn in [
                "vmacc.vx",
                "vnmsac.vx",
                "vmadd.vx",
                "vnmsub.vx",
                "vwmacc.vx",
                "vwmaccsu.vx",
                "vwmaccu.vx",
                "vwmaccus.vx",
            ]:
                code_template = ARITH_MUL_ADD_VX_CODE_TEMPLATE
            else:
                code_template = ARITH_VX_CODE_TEMPLATE
        elif self.suffix in ["vf", "wf"]:
            if self.insn in [
                "vfmacc.vf",
                "vfmadd.vf",
                "vfmsac.vf",
                "vfmsub.vf",
                "vfnmacc.vf",
                "vfnmadd.vf",
                "vfnmsac.vf",
                "vfnmsub.vf",
                "vfwmacc.vf",
                "vfwmsac.vf",
                "vfwnmsac.vf",
                "vfwnmacc.vf",
            ]:
                code_template = ARITH_MUL_ADD_VF_CODE_TEMPLATE
            else:
                code_template = ARITH_VF_CODE_TEMPLATE
        elif self.insn in ["vmv.v.v", "vmv1r.v", "vmv2r.v", "vmv4r.v", "vmv8r.v"]:
            code_template = ARITH_VMV_VV_CODE_TEMPLATE
        elif self.insn == "vmv.v.i":
            code_template = ARITH_VMV_VI_CODE_TEMPLATE
        elif self.insn in ["vmv.v.x", "vmv.s.x"]:
            code_template = ARITH_VMV_VX_CODE_TEMPLATE
        else:
            raise Exception("Unknown suffix.")

        vlmax = (VLEN // self.sew) * self.lmul
        code = ""

        vd = self.lmul
        vd_lmul = self.lmul
        vs1 = self.lmul * 2
        vs2 = self.lmul * 3
        if self.insn.startswith("vw") or self.insn.startswith("vfw"):
            vd *= 2
            vd_lmul *= 2
            vs1 *= 2
            vs2 *= 2
        elif self.insn == "vrgatherei16.vv":
            emul = max(self.lmul, int((16 / self.sew) * self.lmul))
            vd = emul
            vs1 = emul * 2
            vs2 = emul * 3

        for vl in [vlmax // 2, vlmax - 1, vlmax]:
            code += code_template.format(
                sew=self.sew,
                vd_lmul=vd_lmul,
                lmul=self.lmul,
                vl=vl,
                mask_code=MASK_CODE if self.suffix.endswith("m") else "",
                vta="ta",
                vma="ma",
                v0t=", v0" if self.suffix in ["vvm", "vxm", "vim"] else "",
                op=self.insn,
                imm=floathex(1.0, self.sew) if self.insn.startswith("vf") else 1,
                fmv_unit="w" if self.sew == 32 else "d",
                vd=vd,
                vs1=vs1,
                vs2=vs2,
                from_reg=vd,
                to_reg=vs1,
            )

            code += code_template.format(
                sew=self.sew,
                vd_lmul=vd_lmul,
                lmul=self.lmul,
                vl=vl,
                mask_code=MASK_CODE if self.suffix.endswith("m") else "",
                vta="tu",
                vma="ma",
                v0t=", v0" if self.suffix in ["vvm", "vxm", "vim"] else "",
                op=self.insn,
                imm=floathex(1, self.sew) if self.insn.startswith("vf") else 1,
                fmv_unit="w" if self.sew == 32 else "d",
                vd=vd,
                vs1=vs1,
                vs2=vs2,
                from_reg=vd,
                to_reg=vs1,
            )

            if not (
                self.suffix.endswith("m")
                or self.insn.startswith("vmv")
                or self.insn
                in ["vmadc.vv", "vmadc.vx", "vmadc.vi", "vmsbc.vv", "vmsbc.vx"]
            ):
                code += code_template.format(
                    sew=self.sew,
                    vd_lmul=vd_lmul,
                    lmul=self.lmul,
                    vl=vl,
                    mask_code=MASK_CODE,
                    vta="ta",
                    vma="ma",
                    v0t=", v0.t",
                    op=self.insn,
                    imm=floathex(1, self.sew) if self.insn.startswith("vf") else 1,
                    fmv_unit="w" if self.sew == 32 else "d",
                    vd=vd,
                    vs1=vs1,
                    vs2=vs2,
                    from_reg=vd,
                    to_reg=vs1,
                )

                code += code_template.format(
                    sew=self.sew,
                    vd_lmul=vd_lmul,
                    lmul=self.lmul,
                    vl=vl,
                    mask_code=MASK_CODE,
                    vta="ta",
                    vma="ma",
                    v0t=", v0" if self.suffix.endswith("m") else ", v0.t",
                    op=self.insn,
                    imm=floathex(1, self.sew) if self.insn.startswith("vf") else 1,
                    fmv_unit="w" if self.sew == 32 else "d",
                    vd=vd,
                    vs1=vs1,
                    vs2=vs2,
                    from_reg=vd,
                    to_reg=vs1,
                )

        return (HEADER_TEMPLATE + ARITH_TEMPLATE).format(
            filename=self.filename,
            insn_name=self.insn,
            extras=f"With LMUL={self.lmul}, SEW={self.sew}",
            nbytes=test_data_bytes * 2,
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
            for insn in ["vle", "vse"]:
                filename = f"{insn}{eew}.v_LMUL{lmul}.S"
                test = UnitStrideLoadStore(filename, insn, lmul, eew)
                save_to_file(BASE_PATH + filename, str(test))

    for lmul in [1, 2, 4, 8]:
        for eew in [8, 16, 32, 64]:
            filename = f"vlse{eew}.v_LMUL{lmul}.S"
            test = StridedLoad(filename, lmul, eew)
            save_to_file(BASE_PATH + filename, str(test))

    for lmul in [1, 2, 4, 8]:
        for sew in [8, 16, 32, 64]:
            for insn in [
                "vaadd.vv",
                "vaadd.vx",
                "vaaddu.vv",
                "vaaddu.vx",
                "vadc.vim",
                "vadc.vvm",
                "vadc.vxm",
                "vadd.vi",
                "vadd.vv",
                "vadd.vx",
                "vand.vi",
                "vand.vv",
                "vand.vx",
                "vasub.vv",
                "vasub.vx",
                "vasubu.vv",
                "vasubu.vx",
                "vdiv.vv",
                "vdiv.vx",
                "vdivu.vv",
                "vdivu.vx",
                "vmacc.vv",
                "vmacc.vx",
                "vmadc.vi",
                "vmadc.vim",
                "vmadc.vv",
                "vmadc.vvm",
                "vmadc.vx",
                "vmadc.vxm",
                "vmadd.vv",
                "vmadd.vx",
                "vmand.mm",
                "vmandn.mm",
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
                "vmnand.mm",
                "vmnor.mm",
                "vmor.mm",
                "vmorn.mm",
                "vmsbc.vv",
                "vmsbc.vvm",
                "vmsbc.vx",
                "vmsbc.vxm",
                "vmseq.vi",
                "vmseq.vv",
                "vmseq.vx",
                "vmsgt.vi",
                "vmsgt.vx",
                "vmsgtu.vi",
                "vmsgtu.vx",
                "vmsle.vi",
                "vmsle.vv",
                "vmsle.vx",
                "vmsleu.vi",
                "vmsleu.vv",
                "vmsleu.vx",
                "vmslt.vv",
                "vmslt.vx",
                "vmsltu.vv",
                "vmsltu.vx",
                "vmsne.vi",
                "vmsne.vv",
                "vmsne.vx",
                "vmul.vv",
                "vmul.vx",
                "vmulh.vv",
                "vmulh.vx",
                "vmulhsu.vv",
                "vmulhsu.vx",
                "vmulhu.vv",
                "vmulhu.vx",
                "vmxnor.mm",
                "vmxor.mm",
                "vnmsac.vv",
                "vnmsac.vx",
                "vnmsub.vv",
                "vnmsub.vx",
                "vor.vi",
                "vor.vv",
                "vor.vx",
                "vredand.vs",
                "vredmax.vs",
                "vredmaxu.vs",
                "vredmin.vs",
                "vredminu.vs",
                "vredor.vs",
                "vredsum.vs",
                "vredxor.vs",
                "vrem.vv",
                "vrem.vx",
                "vremu.vv",
                "vremu.vx",
                "vrgather.vi",
                "vrgather.vv",
                "vrgather.vx",
                "vrsub.vi",
                "vrsub.vx",
                "vsadd.vi",
                "vsadd.vv",
                "vsadd.vx",
                "vsaddu.vi",
                "vsaddu.vv",
                "vsaddu.vx",
                "vsbc.vvm",
                "vsbc.vxm",
                "vslide1down.vx",
                "vslide1up.vx",
                "vslidedown.vi",
                "vslidedown.vx",
                "vslideup.vi",
                "vslideup.vx",
                "vsll.vi",
                "vsll.vv",
                "vsll.vx",
                "vsmul.vv",
                "vsmul.vx",
                "vsra.vi",
                "vsra.vv",
                "vsra.vx",
                "vsrl.vi",
                "vsrl.vv",
                "vsrl.vx",
                "vssra.vi",
                "vssra.vv",
                "vssra.vx",
                "vssrl.vi",
                "vssrl.vv",
                "vssrl.vx",
                "vssub.vv",
                "vssub.vx",
                "vssubu.vv",
                "vssubu.vx",
                "vsub.vv",
                "vsub.vx",
                "vxor.vi",
                "vxor.vv",
                "vxor.vx",
                "vcompress.vm",
                "vmv.v.v",
                "vmv.v.x",
                "vmv.v.i",
                "vmv.s.x",
            ]:
                filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
                arith = Arith(filename, insn, lmul, sew)
                save_to_file(BASE_PATH + filename, str(arith))

        for sew in [32, 64]:
            for insn in [
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
                "vfredosum.vs",
                "vfredusum.vs",
                "vfredmax.vs",
                "vfredmin.vs",
                "vfredosum.vs",
                "vfredusum.vs",
                "vfredmax.vs",
                "vfredmin.vs",
                "vfslide1up.vf",
                "vfslide1down.vf",
                "vmfeq.vv",
                "vmfeq.vf",
                "vmfne.vv",
                "vmfne.vf",
                "vmflt.vv",
                "vmflt.vf",
                "vmfle.vv",
                "vmfle.vf",
                "vmfgt.vf",
                "vmfge.vf",
                "vfmul.vv",
                "vfmul.vf",
                "vfdiv.vv",
                "vfdiv.vf",
                "vfrdiv.vf",
                "vfmacc.vv",
                "vfmacc.vf",
                "vfnmacc.vv",
                "vfnmacc.vf",
                "vfmsac.vv",
                "vfmsac.vf",
                "vfnmsac.vv",
                "vfnmsac.vf",
                "vfmadd.vv",
                "vfmadd.vf",
                "vfnmadd.vv",
                "vfnmadd.vf",
                "vfmsub.vv",
                "vfmsub.vf",
                "vfnmsub.vv",
                "vfnmsub.vf",
            ]:
                filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
                arith = Arith(filename, insn, lmul, sew)
                save_to_file(BASE_PATH + filename, str(arith))

    for lmul in [1, 2, 4, 8]:
        for sew in [8, 16, 32, 64]:
            emul = (16 / sew) * lmul
            if emul > 8:
                continue
            insn = "vrgatherei16.vv"
            filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
            arith = Arith(filename, insn, lmul, sew)
            save_to_file(BASE_PATH + filename, str(arith))

    for lmul in [1, 2, 4]:
        for sew in [8, 16, 32]:
            for insn in [
                "vnsrl.wv",
                "vnsrl.wx",
                "vnsrl.wi",
                "vnsra.wv",
                "vnsra.wx",
                "vnsra.wi",
                "vnclipu.wv",
                "vnclipu.wx",
                "vnclipu.wi",
                "vnclip.wv",
                "vnclip.wx",
                "vnclip.wi",
                "vwredsumu.vs",
                "vwredsum.vs",
                "vwaddu.vv",
                "vwaddu.vx",
                "vwsubu.vv",
                "vwsubu.vx",
                "vwadd.vv",
                "vwadd.vx",
                "vwsub.vv",
                "vwsub.vx",
                "vwaddu.wv",
                "vwaddu.wx",
                "vwsubu.wv",
                "vwsubu.wx",
                "vwadd.wv",
                "vwadd.wx",
                "vwsub.wv",
                "vwsub.wx",
                "vwmul.vv",
                "vwmul.vx",
                "vwmulu.vv",
                "vwmulu.vx",
                "vwmulsu.vv",
                "vwmulsu.vx",
                "vwmaccu.vv",
                "vwmaccu.vx",
                "vwmacc.vv",
                "vwmacc.vx",
                "vwmaccsu.vv",
                "vwmaccsu.vx",
                "vwmaccus.vx",
            ]:
                filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
                arith = Arith(filename, insn, lmul, sew)
                save_to_file(BASE_PATH + filename, str(arith))

    for lmul in [1, 2, 4]:
        for sew in [32]:
            for insn in [
                "vfwadd.vv",
                "vfwadd.vf",
                "vfwsub.vv",
                "vfwsub.vf",
                "vfwadd.wv",
                "vfwadd.wf",
                "vfwsub.wv",
                "vfwsub.wf",
                "vfwmacc.vv",
                "vfwmacc.vf",
                "vfwnmacc.vv",
                "vfwnmacc.vf",
                "vfwmsac.vv",
                "vfwmsac.vf",
                "vfwnmsac.vv",
                "vfwnmsac.vf",
                "vfwredosum.vs",
                "vfwredusum.vs",
                "vfwmul.vv",
                "vfwmul.vf",
            ]:
                filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
                arith = Arith(filename, insn, lmul, sew)
                save_to_file(BASE_PATH + filename, str(arith))

    sew = 8
    insn = "vmv1r.v"
    lmul = 1
    filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
    arith = Arith(filename, insn, lmul, sew)
    save_to_file(BASE_PATH + filename, str(arith))

    insn = "vmv2r.v"
    lmul = 2
    filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
    arith = Arith(filename, insn, lmul, sew)
    save_to_file(BASE_PATH + filename, str(arith))

    insn = "vmv4r.v"
    lmul = 4
    filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
    arith = Arith(filename, insn, lmul, sew)
    save_to_file(BASE_PATH + filename, str(arith))

    insn = "vmv8r.v"
    lmul = 8
    filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
    arith = Arith(filename, insn, lmul, sew)
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
