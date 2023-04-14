#!/usr/bin/python3
import os
import re
import subprocess

from constants import BASE_PATH, ISA_PATH
from templates import MAKEFRAG_TEMPLATE
from utils import read_file, save_to_file

"""
Merge tests with spike output.
"""

for file in sorted(os.listdir(ISA_PATH)):
    if not file.startswith("rv64uv-p-v") or file.endswith(".dump"):
        continue

    output = subprocess.check_output(
        [
            "/Users/ksco/Developer/riscv-isa-sim-ksco/build/spike",
            "--isa",
            "rv64gcv",
            "--varch",
            "vlen:4096,elen:64",
            f"{ISA_PATH}{file}",
        ],
    )
    output = output.decode(encoding="UTF-8").split("---")

    assembly_filename = file[len("rv64uv-p-") :]
    content = read_file(f"{BASE_PATH}{assembly_filename}.S")

    idx = 0
    while True:
        match = re.search("  addi x0, x.+", content)
        if not match:
            break

        content = "{}{}{}".format(
            content[: match.start()],
            str(output[idx]),
            content[match.end() :],
        )
        idx += 1

    content = content.replace("  TEST_CASE(2, x0, 0x0)", "")
    save_to_file(f"{ISA_PATH}rv64uxx/{assembly_filename}.S", content)

files = []
for file in sorted(os.listdir(f"{ISA_PATH}rv64uxx/")):
    if file.startswith("v"):
        filename = file.rstrip(".S")
        files.append(f"  {filename} \\")
with open(f"{ISA_PATH}rv64uxx/" + "Makefrag", "w", encoding="UTF-8") as f:
    f.write(MAKEFRAG_TEMPLATE.format(data="\n".join(files)))
