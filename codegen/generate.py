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
    VLM_CODE_TEMPLATE,
    VSM_CODE_TEMPLATE,
    STRIDED_LOAD_CODE_TEMPLATE,
    STRIDED_STORE_CODE_TEMPLATE,
    INDEXED_LOAD_CODE_TEMPLATE,
    INDEXED_STORE_CODE_TEMPLATE,
    INDEXED_TEMPLATE,
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
    ARITH_EXT_CODE_TEMPLATE,
    ARITH_CVT_CODE_TEMPLATE,
    ARITH_VFMV_CODE_TEMPLATE,
    ARITH_M_CODE_TEMPLATE,
    ARITH_RDM_CODE_TEMPLATE
)

from utils import (
    generate_test_data,
    generate_indexed_data,
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


class UnitStrideMaskLoadStore:
    """Generate vlm.v, vsm.v tests."""

    def __init__(self, filename, insn):
        self.filename = filename
        self.insn = insn

    def __str__(self):
        test_data_bytes = vlenb + 8
        test_data = generate_test_data(test_data_bytes)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])

        code_template = VLM_CODE_TEMPLATE if self.insn == "vlm" else VSM_CODE_TEMPLATE
        code = ""
        for vl in [vlenb // 2, vlenb - 1, vlenb]:
            code += code_template.format(vl=vl)

        return (HEADER_TEMPLATE + STRIDE_TEMPLATE).format(
            filename=self.filename,
            insn_name=f"{self.insn}.v",
            extras="",
            nbytes=test_data_bytes,
            test_data_str=test_data_str,
            code=code,
        )


class StridedLoadStore:
    """Generate vlse<EEW>.v tests."""

    def __init__(self, filename, lmul, eew, insn):
        self.filename = filename
        self.lmul = lmul
        self.eew = eew
        self.insn = insn

    def __str__(self):
        maxstride = 2
        test_data_bytes = (vlenb * self.lmul) * max(maxstride, 1) + 8
        test_data = generate_test_data(test_data_bytes)
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])

        code_template = (
            STRIDED_LOAD_CODE_TEMPLATE
            if self.insn == "vlse"
            else STRIDED_STORE_CODE_TEMPLATE
        )

        code = ""
        vlmax = (VLEN // self.eew) * self.lmul
        for vl in [vlmax // 2, vlmax - 1, vlmax]:
            for stride in [i * (self.eew // 8) for i in [-1, -2, 0, 1, maxstride]]:
                code += code_template.format(
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

                code += code_template.format(
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

                code += code_template.format(
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

                code += code_template.format(
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


class IndexedLoadStore:
    """Generates indexed load and store tests."""

    def __init__(self, filename, insn, lmul, sew, offset_eew):
        self.filename = filename
        self.insn = insn
        self.lmul = lmul
        self.sew = sew
        self.offset_eew = offset_eew

    def __str__(self):
        emul = max(int((self.offset_eew / self.sew) * self.lmul), 1)
        test_data_bytes = (VLEN * self.lmul) // 8 + 8
        test_data = generate_test_data(test_data_bytes)
        index_data = generate_indexed_data(vlenb * emul, self.offset_eew)
        index_data = [d * (self.sew // 8) for d in index_data]
        test_data_str = "\n".join([f"  .quad 0x{e:x}" for e in test_data])
        index_data_str = "\n".join([f"  .quad 0x{e:x}" for e in index_data])

        code_template = (
            INDEXED_LOAD_CODE_TEMPLATE
            if self.insn.startswith("vl")
            else INDEXED_STORE_CODE_TEMPLATE
        )

        code = ""
        vlmax = (VLEN // self.sew) * self.lmul
        for vl in [vlmax // 2, vlmax - 1, vlmax]:
            code += code_template.format(
                insn=self.insn,
                lmul=self.lmul,
                emul=emul,
                sew=self.sew,
                offset_eew=self.offset_eew,
                vl=vl,
                vd=self.lmul,
                vs2=max(self.lmul * 2, emul * 2),
                mask_code="",
                v0t="",
                vma="ma",
                vta="ta",
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )
            code += code_template.format(
                insn=self.insn,
                lmul=self.lmul,
                emul=emul,
                sew=self.sew,
                offset_eew=self.offset_eew,
                vl=vl,
                vd=self.lmul,
                vs2=max(self.lmul * 2, emul * 2),
                mask_code=MASK_CODE,
                v0t=", v0.t",
                vma="ma",
                vta="ta",
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )
            code += code_template.format(
                insn=self.insn,
                lmul=self.lmul,
                emul=emul,
                sew=self.sew,
                offset_eew=self.offset_eew,
                vl=vl,
                vd=self.lmul,
                vs2=max(self.lmul * 2, emul * 2),
                mask_code="",
                v0t="",
                vma="ma",
                vta="tu",
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )
            code += code_template.format(
                insn=self.insn,
                lmul=self.lmul,
                emul=emul,
                sew=self.sew,
                offset_eew=self.offset_eew,
                vl=vl,
                vd=self.lmul,
                vs2=max(self.lmul * 2, emul * 2),
                mask_code=MASK_CODE,
                v0t=", v0.t",
                vma="mu",
                vta="ta",
                from_reg=self.lmul,
                to_reg=self.lmul * 2,
            )

        return (HEADER_TEMPLATE + INDEXED_TEMPLATE).format(
            filename=self.filename,
            insn_name=f"{self.insn}{self.offset_eew}.v",
            extras=f"With LMUL={self.lmul}, SEW={self.sew}",
            nbytes=test_data_bytes,
            test_data_str=test_data_str,
            index_data_str=index_data_str,
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
        elif (
            self.insn.startswith("vfcvt")
            or self.insn.startswith("vfwcvt")
            or self.insn.startswith("vfncvt")
            or self.insn.startswith("vfsqrt")
            or self.insn.startswith("vfrsqrt7")
            or self.insn.startswith("vfrec7")
            or self.insn.startswith("vfclass")
        ):
            code_template = ARITH_CVT_CODE_TEMPLATE
        elif self.insn.startswith("vfmv"):
            code_template = ARITH_VFMV_CODE_TEMPLATE
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
        elif self.insn.startswith("vzext") or self.insn.startswith("vsext"):
            code_template = ARITH_EXT_CODE_TEMPLATE
        elif self.insn in ["vmsbf.m","vmsif.m","vmsof.m","viota.m"]:
            code_template = ARITH_M_CODE_TEMPLATE
        elif self.insn in ["vfirst.m","vcpop.m"]:
            code_template = ARITH_RDM_CODE_TEMPLATE
        else:
            raise Exception("Unknown suffix.")

        vlmax = (VLEN // self.sew) * self.lmul
        code = ""

        vd = self.lmul
        vd_lmul = self.lmul
        vd_sew = self.sew
        vs1 = self.lmul * 2
        vs2 = self.lmul * 3
        vs2_lmul = self.lmul
        vs2_sew = self.sew
        vs1_lmul = self.lmul
        vs1_sew = self.sew
        if (
            self.insn.startswith("vnsrl")
            or self.insn.startswith("vnsra")
            or self.insn.startswith("vnclipu")
            or self.insn.startswith("vnclip")
        ):
            vs2 += self.lmul
            vs2_lmul *= 2
            vs2_sew *= 2
        elif self.insn.startswith("vfncvt"):
            vd = self.lmul * 2
            vs1 = self.lmul * 4
            vs1_lmul *= 2
        elif self.insn.startswith("vw") or self.insn.startswith("vfw"):
            vd *= 2
            vd_lmul *= 2
            vd_sew *= 2
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
                vd_sew=vd_sew,
                vs1_lmul=vs1_lmul,
                vs1_sew=vs1_sew,
                vs2_lmul=vs2_lmul,
                vs2_sew=vs2_sew,
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
                vd_sew=vd_sew,
                vs1_lmul=vs1_lmul,
                vs1_sew=vs1_sew,
                vs2_lmul=vs2_lmul,
                vs2_sew=vs2_sew,
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
                    vd_sew=vd_sew,
                    vs1_lmul=vs1_lmul,
                    vs1_sew=vs1_sew,
                    vs2_lmul=vs2_lmul,
                    vs2_sew=vs2_sew,
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
                    vd_sew=vd_sew,
                    vs1_lmul=vs1_lmul,
                    vs1_sew=vs1_sew,
                    vs2_lmul=vs2_lmul,
                    vs2_sew=vs2_sew,
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

    for insn in ["vlm", "vsm"]:
        filename = f"{insn}.v.S"
        test = UnitStrideMaskLoadStore(filename, insn)
        save_to_file(BASE_PATH + filename, str(test))

    for lmul in [1, 2, 4, 8]:
        for eew in [8, 16, 32, 64]:
            for insn in ["vlse", "vsse"]:
                filename = f"{insn}{eew}.v_LMUL{lmul}.S"
                test = StridedLoadStore(filename, lmul, eew, insn)
                save_to_file(BASE_PATH + filename, str(test))

    for lmul in [1, 2, 4, 8]:
        for sew in [8, 16, 32, 64]:
            for offset_eew in [8, 16, 32, 64]:
                if (offset_eew // sew) * lmul > 8:
                    continue
                for insn in ["vluxei", "vloxei", "vsuxei", "vsoxei"]:
                    filename = f"{insn}{offset_eew}.v_LMUL{lmul}SEW{sew}.S"
                    test = IndexedLoadStore(filename, insn, lmul, sew, offset_eew)
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
                "vfcvt.xu.f.v",
                "vfcvt.x.f.v",
                "vfcvt.rtz.xu.f.v",
                "vfcvt.rtz.x.f.v",
                "vfcvt.f.xu.v",
                "vfcvt.f.x.v",
                "vfsqrt.v",
                "vfrsqrt7.v",
                "vfrec7.v",
                "vfclass.v",
                # vfmv.f.s is tested by the following two insns.
                "vfmv.v.f",
                "vfmv.s.f",
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

    for lmul in [1, 2, 4, 8]:
        for sew in [8, 16, 32, 64]:
            for f in [2, 4, 8]:
                if (lmul / f) < 1 or (sew // f) < 8:
                    continue
                insn = f"vzext.vf{f}"
                filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
                arith = Arith(filename, insn, lmul, sew)
                save_to_file(BASE_PATH + filename, str(arith))

                insn = f"vsext.vf{f}"
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
                "vfwcvt.xu.f.v",
                "vfwcvt.x.f.v",
                "vfwcvt.rtz.xu.f.v",
                "vfwcvt.rtz.x.f.v",
                "vfwcvt.f.xu.v",
                "vfwcvt.f.x.v",
                "vfwcvt.f.f.v",
                "vfncvt.xu.f.w",
                "vfncvt.x.f.w",
                "vfncvt.rtz.xu.f.w",
                "vfncvt.rtz.x.f.w",
                "vfncvt.f.xu.w",
                "vfncvt.f.x.w",
                "vfncvt.f.f.w",
                "vfncvt.rod.f.f.w",
            ]:
                filename = f"{insn}_LMUL{lmul}SEW{sew}.S"
                arith = Arith(filename, insn, lmul, sew)
                save_to_file(BASE_PATH + filename, str(arith))

    for lmul in [1, 2, 4, 8]:
        for sew in [8, 16, 32, 64]:
            for insn in [
                "vfirst.m",
                "vcpop.m",
                "vmsif.m",
                "vmsbf.m",
                "vmsbf.m",
                "viota.m"
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
